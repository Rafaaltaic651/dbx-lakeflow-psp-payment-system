-- Databricks notebook source
-- Entity: Payouts (Settlements)
-- Layer: Silver - Cleansing & Conforming
-- Upstream: bronze.psp_payouts

CREATE OR REFRESH STREAMING TABLE `${catalog}`.silver.psp_payouts (
    CONSTRAINT valid_payout_id EXPECT (payout_id IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_merchant_id EXPECT (merchant_id IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_batch_date EXPECT (payout_batch_date IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_currency EXPECT (payout_currency IN ('USD', 'GBP', 'CAD', 'AUD')) ON VIOLATION DROP ROW,
    CONSTRAINT valid_gross EXPECT (gross_cents > 0) ON VIOLATION DROP ROW,
    CONSTRAINT valid_net_calculation EXPECT (ABS(net_cents - (gross_cents - fees_cents - reserve_cents)) <= 2) ON VIOLATION DROP ROW,
    CONSTRAINT valid_status EXPECT (payout_status IN ('paid', 'pending', 'in_transit', 'failed')) ON VIOLATION DROP ROW,
    CONSTRAINT valid_paid_at EXPECT (payout_paid_at IS NOT NULL) ON VIOLATION DROP ROW
)
COMMENT "Cleaned settlement and payout data - signed amounts, fee breakdowns, net position validated"
TBLPROPERTIES (
    "quality" = "silver",
    "domain" = "payouts",
    "delta.feature.timestampNtz" = "supported"
)
AS SELECT
    TRIM(payout_id) AS payout_id,
    TRIM(merchant_id) AS merchant_id,

    -- Settlement date and currency
    batch_day AS payout_batch_date,
    currency AS payout_currency,

    -- Raw cents preserved
    gross_cents,
    fees_cents,
    reserve_cents,
    net_cents,

    -- Dollar amounts as DECIMAL
    CAST(gross_cents / 100.0 AS DECIMAL(18,2)) AS gross_amount,
    CAST(fees_cents / 100.0 AS DECIMAL(18,2)) AS fees_amount,
    CAST(reserve_cents / 100.0 AS DECIMAL(18,2)) AS reserve_amount,
    CAST(net_cents / 100.0 AS DECIMAL(18,2)) AS net_amount,

    -- Fee and margin rates
    CAST((fees_cents * 100.0 / gross_cents) AS DECIMAL(8,4)) AS effective_fee_rate_pct,
    CAST((reserve_cents * 100.0 / gross_cents) AS DECIMAL(8,4)) AS reserve_rate_pct,
    CAST((net_cents * 100.0 / gross_cents) AS DECIMAL(8,4)) AS net_margin_pct,

    -- Transaction volume metrics
    transaction_count AS payout_transaction_count,
    CAST(gross_cents / transaction_count / 100.0 AS DECIMAL(18,2)) AS avg_transaction_amount,

    -- Status normalization
    LOWER(status) AS payout_status,

    -- Boolean flags
    CASE WHEN LOWER(status) = 'paid' THEN TRUE ELSE FALSE END AS is_payout_completed,
    CASE WHEN LOWER(status) = 'failed' THEN TRUE ELSE FALSE END AS is_payout_failed,
    CASE WHEN LOWER(status) = 'in_transit' THEN TRUE ELSE FALSE END AS is_payout_in_transit,

    -- Size categorization
    CASE
        WHEN gross_cents < 50000 THEN 'small'
        WHEN gross_cents < 200000 THEN 'medium'
        WHEN gross_cents < 500000 THEN 'large'
        ELSE 'extra_large'
    END AS payout_size_category,

    -- Large payout flag (>$1000)
    CASE WHEN gross_cents >= 100000 THEN TRUE ELSE FALSE END AS is_large_payout,

    -- Settlement timing
    paid_at AS payout_paid_at,
    DATEDIFF(CAST(paid_at AS DATE), batch_day) AS settlement_delay_days,

    -- Lineage
    _ingested_at,
    current_timestamp() AS _processed_at

FROM STREAM(`${catalog}`.bronze.psp_payouts);
