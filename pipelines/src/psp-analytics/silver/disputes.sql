-- Databricks notebook source
-- Entity: Disputes (Chargebacks)
-- Layer: Silver - Cleansing & Conforming
-- Upstream: bronze.psp_disputes

CREATE OR REFRESH STREAMING TABLE `${catalog}`.silver.psp_disputes (
    CONSTRAINT valid_dispute_id EXPECT (dispute_id IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_txn_id EXPECT (txn_id IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_reason_code EXPECT (dispute_reason_code IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_amount EXPECT (dispute_amount_cents > 0) ON VIOLATION DROP ROW,
    CONSTRAINT valid_stage EXPECT (dispute_stage IN ('inquiry', 'chargeback', 'pre_arbitration', 'arbitration')) ON VIOLATION DROP ROW,
    CONSTRAINT valid_opened_at EXPECT (dispute_opened_at IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_date_logic EXPECT (dispute_closed_at IS NULL OR dispute_closed_at >= dispute_opened_at) ON VIOLATION DROP ROW,
    CONSTRAINT valid_status EXPECT (dispute_status IN ('open', 'pending_evidence', 'won', 'lost')) ON VIOLATION DROP ROW,
    CONSTRAINT valid_liability EXPECT (liability_party IN ('merchant', 'issuer', 'shared')) ON VIOLATION DROP ROW
)
COMMENT "Cleaned chargeback and dispute data - reason codes classified, stages scored, aging calculated"
TBLPROPERTIES (
    "quality" = "silver",
    "domain" = "disputes",
    "delta.feature.timestampNtz" = "supported"
)
AS SELECT
    -- Keys
    TRIM(dispute_id) AS dispute_id,
    TRIM(txn_id) AS txn_id,

    -- Reason code and classification
    UPPER(reason_code) AS dispute_reason_code,
    CASE
        WHEN UPPER(reason_code) = 'FRAUD' THEN 'fraud_related'
        WHEN UPPER(reason_code) IN ('PRODUCT_NOT_RECEIVED', 'NOT_AS_DESCRIBED') THEN 'service_issue'
        WHEN UPPER(reason_code) IN ('DUPLICATE', 'CREDIT_NOT_PROCESSED') THEN 'processing_error'
        WHEN UPPER(reason_code) = 'SUBSCRIPTION_CANCELED' THEN 'subscription_issue'
        WHEN UPPER(reason_code) = 'UNAUTHORIZED' THEN 'unauthorized'
        ELSE 'other'
    END AS dispute_category,

    -- Stage and status normalization
    LOWER(stage) AS dispute_stage,
    LOWER(liability) AS liability_party,
    LOWER(status) AS dispute_status,

    -- Stage severity scoring (1=lowest, 4=highest)
    CASE
        WHEN LOWER(stage) = 'inquiry' THEN 1
        WHEN LOWER(stage) = 'chargeback' THEN 2
        WHEN LOWER(stage) = 'pre_arbitration' THEN 3
        WHEN LOWER(stage) = 'arbitration' THEN 4
    END AS stage_severity_level,

    -- Amount fields
    amount_cents AS dispute_amount_cents,
    CAST(amount_cents / 100.0 AS DECIMAL(18,2)) AS dispute_amount,

    -- Timestamps
    opened_at AS dispute_opened_at,
    closed_at AS dispute_closed_at,

    -- Dispute aging (days since opened)
    CASE
        WHEN closed_at IS NOT NULL THEN DATEDIFF(CAST(closed_at AS DATE), CAST(opened_at AS DATE))
        ELSE DATEDIFF(CURRENT_DATE(), CAST(opened_at AS DATE))
    END AS dispute_age_days,

    -- Date dimensions
    CAST(opened_at AS DATE) AS dispute_opened_date,
    CAST(closed_at AS DATE) AS dispute_closed_date,

    -- Resolution flags
    CASE WHEN closed_at IS NOT NULL THEN TRUE ELSE FALSE END AS is_dispute_closed,
    CASE WHEN LOWER(status) = 'won' THEN TRUE ELSE FALSE END AS is_dispute_won,
    CASE WHEN LOWER(status) = 'lost' THEN TRUE ELSE FALSE END AS is_dispute_lost,

    -- Liability flags
    CASE WHEN LOWER(liability) = 'merchant' THEN TRUE ELSE FALSE END AS is_merchant_liable,
    CASE WHEN LOWER(liability) = 'issuer' THEN TRUE ELSE FALSE END AS is_issuer_liable,

    -- Fraud identification
    CASE WHEN UPPER(reason_code) = 'FRAUD' THEN TRUE ELSE FALSE END AS is_fraud_dispute,

    -- Escalation tracking
    CASE WHEN LOWER(stage) IN ('pre_arbitration', 'arbitration') THEN TRUE ELSE FALSE END AS is_escalated,

    -- SLA tracking buckets
    CASE
        WHEN DATEDIFF(COALESCE(CAST(closed_at AS DATE), CURRENT_DATE()), CAST(opened_at AS DATE)) <= 7 THEN 'within_sla'
        WHEN DATEDIFF(COALESCE(CAST(closed_at AS DATE), CURRENT_DATE()), CAST(opened_at AS DATE)) <= 30 THEN 'approaching_sla'
        WHEN DATEDIFF(COALESCE(CAST(closed_at AS DATE), CURRENT_DATE()), CAST(opened_at AS DATE)) <= 60 THEN 'sla_warning'
        ELSE 'sla_breached'
    END AS sla_status,

    -- Lineage
    _ingested_at,
    current_timestamp() AS _processed_at

FROM STREAM(`${catalog}`.bronze.psp_disputes);
