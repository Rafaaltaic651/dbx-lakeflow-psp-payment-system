-- Databricks notebook source
-- Entity: Customers
-- Layer: Silver - Cleansing & Conforming
-- Upstream: bronze.psp_customers

CREATE OR REFRESH STREAMING TABLE `${catalog}`.silver.psp_customers (
    CONSTRAINT valid_customer_id EXPECT (customer_id IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_email_hash EXPECT (email_hash IS NOT NULL AND email_hash LIKE 'hash_%') ON VIOLATION DROP ROW,
    CONSTRAINT valid_phone_hash EXPECT (phone_hash IS NOT NULL AND phone_hash LIKE 'hash_%') ON VIOLATION DROP ROW,
    CONSTRAINT valid_customer_type EXPECT (customer_type IN ('regular', 'vip', 'flagged')) ON VIOLATION DROP ROW,
    CONSTRAINT valid_created_at EXPECT (customer_created_at IS NOT NULL) ON VIOLATION DROP ROW
)
COMMENT "Cleaned and conformed customer profiles - PII hashed, type validated, tenure derived"
TBLPROPERTIES (
    "quality" = "silver",
    "domain" = "customers",
    "delta.feature.timestampNtz" = "supported"
)
AS SELECT
    TRIM(customer_id) AS customer_id,

    -- PII fields (pre-hashed at source - validated only)
    LOWER(email_hash) AS email_hash,
    LOWER(phone_hash) AS phone_hash,

    -- Customer classification
    LOWER(customer_type) AS customer_type,

    -- Derived flags
    CASE WHEN LOWER(customer_type) = 'vip' THEN TRUE ELSE FALSE END AS is_vip_customer,
    CASE WHEN LOWER(customer_type) = 'flagged' THEN TRUE ELSE FALSE END AS is_flagged_customer,

    -- Tenure
    DATEDIFF(CURRENT_DATE(), CAST(created_at AS DATE)) AS customer_tenure_days,

    -- Timestamps
    created_at AS customer_created_at,

    -- Lineage
    _ingested_at,
    current_timestamp() AS _processed_at

FROM STREAM(`${catalog}`.bronze.psp_customers);
