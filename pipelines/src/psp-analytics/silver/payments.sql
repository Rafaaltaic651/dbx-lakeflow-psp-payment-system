-- Databricks notebook source
-- Entity: Payments (Payment Instruments)
-- Layer: Silver - Cleansing & Conforming
-- Upstream: bronze.psp_payment_instruments

CREATE OR REFRESH STREAMING TABLE `${catalog}`.silver.psp_payment_instruments (
    CONSTRAINT valid_payment_id EXPECT (payment_id IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_customer_id EXPECT (customer_id IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_card_brand EXPECT (card_brand IN ('visa', 'mastercard', 'amex', 'discover', 'diners')) ON VIOLATION DROP ROW,
    CONSTRAINT valid_card_bin EXPECT (LENGTH(card_bin) = 6 AND card_bin RLIKE '^[0-9]{6}$') ON VIOLATION DROP ROW,
    CONSTRAINT valid_card_last4 EXPECT (LENGTH(card_last4) = 4 AND card_last4 RLIKE '^[0-9]{4}$') ON VIOLATION DROP ROW,
    CONSTRAINT valid_expiry_month EXPECT (card_expiry_month BETWEEN 1 AND 12) ON VIOLATION DROP ROW,
    CONSTRAINT valid_expiry_year EXPECT (card_expiry_year BETWEEN 2024 AND 2035) ON VIOLATION DROP ROW
)
COMMENT "Cleaned payment instruments - card brand normalized, expiry validated, wallet classified"
TBLPROPERTIES (
    "quality" = "silver",
    "domain" = "payments",
    "delta.feature.timestampNtz" = "supported"
)
AS SELECT
    TRIM(payment_id) AS payment_id,
    TRIM(customer_id) AS customer_id,

    -- Card details
    LOWER(brand) AS card_brand,
    bin AS card_bin,
    CONCAT('****-', last4) AS card_last4_masked,
    last4 AS card_last4,
    expiry_month AS card_expiry_month,
    expiry_year AS card_expiry_year,

    -- Wallet classification
    CASE
        WHEN wallet_type IS NULL THEN 'card_only'
        ELSE LOWER(wallet_type)
    END AS wallet_type,
    LOWER(status) AS payment_status,

    -- Boolean flags
    CASE WHEN LOWER(status) = 'active' THEN TRUE ELSE FALSE END AS is_active,
    CASE WHEN wallet_type IS NOT NULL THEN TRUE ELSE FALSE END AS is_wallet_payment,
    CASE WHEN MAKE_DATE(expiry_year, expiry_month, 1) < CURRENT_DATE() THEN TRUE ELSE FALSE END AS is_expired,

    -- Network tier classification
    CASE
        WHEN LOWER(brand) IN ('visa', 'mastercard', 'discover') THEN 'general'
        WHEN LOWER(brand) = 'amex' THEN 'premium'
        WHEN LOWER(brand) = 'diners' THEN 'specialty'
    END AS card_network_tier,

    -- Timestamps
    first_seen_at AS payment_first_seen_at,

    -- Lineage
    _ingested_at,
    current_timestamp() AS _processed_at

FROM STREAM(`${catalog}`.bronze.psp_payment_instruments);
