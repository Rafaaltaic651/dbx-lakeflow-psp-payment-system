-- Databricks notebook source
-- Entity: Merchants
-- Layer: Silver - Cleansing & Conforming
-- Upstream: bronze.psp_merchants

CREATE OR REFRESH STREAMING TABLE `${catalog}`.silver.psp_merchants (
    CONSTRAINT valid_merchant_id EXPECT (merchant_id IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_legal_name EXPECT (legal_name IS NOT NULL AND LENGTH(TRIM(legal_name)) > 0) ON VIOLATION DROP ROW,
    CONSTRAINT valid_mcc EXPECT (LENGTH(merchant_category_code) = 4 AND merchant_category_code RLIKE '^[0-9]{4}$') ON VIOLATION DROP ROW,
    CONSTRAINT valid_country EXPECT (country_code IN ('US', 'GB', 'CA', 'AU')) ON VIOLATION DROP ROW,
    CONSTRAINT valid_kyb_status EXPECT (kyb_status IN ('pending', 'approved', 'rejected', 'review')) ON VIOLATION DROP ROW,
    CONSTRAINT valid_pricing_tier EXPECT (pricing_tier IN ('standard', 'premium', 'enterprise')) ON VIOLATION DROP ROW,
    CONSTRAINT valid_risk_level EXPECT (risk_level IN ('low', 'medium', 'high', 'critical')) ON VIOLATION DROP ROW,
    CONSTRAINT valid_created_at EXPECT (merchant_created_at IS NOT NULL) ON VIOLATION DROP ROW
)
COMMENT "Cleaned and conformed merchant profiles - KYB validated, risk classified, PII-safe"
TBLPROPERTIES (
    "quality" = "silver",
    "domain" = "merchants",
    "delta.feature.timestampNtz" = "supported"
)
AS SELECT
    TRIM(merchant_id) AS merchant_id,
    TRIM(legal_name) AS legal_name,

    -- MCC and geography
    mcc AS merchant_category_code,
    UPPER(country) AS country_code,

    -- Status normalization
    LOWER(kyb_status) AS kyb_status,
    LOWER(pricing_tier) AS pricing_tier,
    LOWER(risk_level) AS risk_level,

    -- Derived boolean flags
    CASE WHEN LOWER(kyb_status) = 'approved' THEN TRUE ELSE FALSE END AS is_kyb_approved,
    CASE WHEN LOWER(risk_level) IN ('high', 'critical') THEN TRUE ELSE FALSE END AS is_high_risk,
    CASE WHEN LOWER(pricing_tier) = 'enterprise' THEN TRUE ELSE FALSE END AS is_enterprise,

    -- MCC category grouping
    CASE
        WHEN mcc BETWEEN '5411' AND '5499' THEN 'grocery'
        WHEN mcc BETWEEN '5811' AND '5814' THEN 'food_and_beverage'
        WHEN mcc BETWEEN '5541' AND '5542' THEN 'fuel'
        WHEN mcc BETWEEN '5912' AND '5912' THEN 'pharmacy'
        WHEN mcc BETWEEN '5200' AND '5261' THEN 'home_improvement'
        WHEN mcc BETWEEN '5600' AND '5699' THEN 'apparel'
        WHEN mcc BETWEEN '7011' AND '7033' THEN 'lodging'
        WHEN mcc BETWEEN '4511' AND '4599' THEN 'travel'
        ELSE 'other'
    END AS mcc_category,

    -- Timestamps
    created_at AS merchant_created_at,

    -- Lineage
    _ingested_at,
    current_timestamp() AS _processed_at

FROM STREAM(`${catalog}`.bronze.psp_merchants);
