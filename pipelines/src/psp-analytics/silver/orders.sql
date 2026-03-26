-- Databricks notebook source
-- Entity: Orders
-- Layer: Silver - Cleansing & Conforming
-- Upstream: bronze.psp_orders

CREATE OR REFRESH STREAMING TABLE `${catalog}`.silver.psp_orders (
    CONSTRAINT valid_order_id EXPECT (order_id IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_merchant_id EXPECT (merchant_id IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_customer_id EXPECT (customer_id IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_currency EXPECT (order_currency IN ('USD', 'GBP', 'CAD', 'AUD')) ON VIOLATION DROP ROW,
    CONSTRAINT valid_total EXPECT (total_amount_cents > 0) ON VIOLATION DROP ROW,
    CONSTRAINT valid_amount_sum EXPECT (ABS(total_amount_cents - (subtotal_cents + tax_cents + tip_cents)) <= 2) ON VIOLATION DROP ROW,
    CONSTRAINT valid_created_at EXPECT (order_created_at IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_channel EXPECT (order_channel IN ('ecommerce', 'pos', 'mobile', 'ivr')) ON VIOLATION DROP ROW
)
COMMENT "Cleaned and conformed order data - amounts validated, channels normalized, value categorized"
TBLPROPERTIES (
    "quality" = "silver",
    "domain" = "orders",
    "delta.feature.timestampNtz" = "supported"
)
AS SELECT
    TRIM(order_id) AS order_id,
    TRIM(merchant_id) AS merchant_id,
    TRIM(customer_id) AS customer_id,

    -- Amounts: cents preserved + dollar conversion
    currency AS order_currency,
    subtotal_cents,
    tax_cents,
    tip_cents,
    total_amount_cents,
    CAST(subtotal_cents / 100.0 AS DECIMAL(18,2)) AS subtotal_amount,
    CAST(tax_cents / 100.0 AS DECIMAL(18,2)) AS tax_amount,
    CAST(tip_cents / 100.0 AS DECIMAL(18,2)) AS tip_amount,
    CAST(total_amount_cents / 100.0 AS DECIMAL(18,2)) AS total_amount,

    -- Derived rates
    CAST(tax_cents * 1.0 / subtotal_cents AS DECIMAL(8,4)) AS tax_rate,
    CAST(tip_cents * 1.0 / subtotal_cents AS DECIMAL(8,4)) AS tip_rate,

    -- Channel normalization
    LOWER(channel) AS order_channel,

    -- Boolean flags
    CASE WHEN LOWER(channel) = 'ecommerce' THEN TRUE ELSE FALSE END AS is_ecommerce_order,
    CASE WHEN tip_cents > 0 THEN TRUE ELSE FALSE END AS has_tip,
    CASE WHEN total_amount_cents >= 10000 THEN TRUE ELSE FALSE END AS is_high_value_order,

    -- Value categorization
    CASE
        WHEN total_amount_cents < 2000 THEN 'small'
        WHEN total_amount_cents < 5000 THEN 'medium'
        WHEN total_amount_cents < 10000 THEN 'large'
        ELSE 'extra_large'
    END AS order_size_category,

    -- Time dimensions
    created_at AS order_created_at,
    CAST(created_at AS DATE) AS order_date,
    HOUR(created_at) AS order_hour,
    DAYOFWEEK(created_at) AS order_day_of_week,

    -- Lineage
    _ingested_at,
    current_timestamp() AS _processed_at

FROM STREAM(`${catalog}`.bronze.psp_orders);
