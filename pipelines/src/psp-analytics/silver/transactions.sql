-- Databricks notebook source
-- Entity: Transactions
-- Layer: Silver - Cleansing & Conforming
-- Upstream: bronze.psp_transactions

CREATE OR REFRESH STREAMING TABLE `${catalog}`.silver.psp_transactions (
    CONSTRAINT valid_txn_id EXPECT (txn_id IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_order_id EXPECT (order_id IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_payment_id EXPECT (payment_id IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_amount EXPECT (amount_cents > 0) ON VIOLATION DROP ROW,
    CONSTRAINT valid_currency EXPECT (transaction_currency IN ('USD', 'GBP', 'CAD', 'AUD')) ON VIOLATION DROP ROW,
    CONSTRAINT valid_state EXPECT (transaction_state IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_response_code EXPECT (response_code IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_authorized_at EXPECT (transaction_authorized_at IS NOT NULL) ON VIOLATION DROP ROW,
    CONSTRAINT valid_processor EXPECT (processor_name IN ('mastercard_network', 'discover_network', 'visa_network', 'amex_network')) ON VIOLATION DROP ROW,
    CONSTRAINT valid_three_ds EXPECT (three_ds_status IN ('not_supported', 'attempted', 'frictionless', 'challenge')) ON VIOLATION DROP ROW
)
COMMENT "Cleaned and conformed payment transactions - amounts as DECIMAL, states normalized, response codes decoded"
TBLPROPERTIES (
    "quality" = "silver",
    "domain" = "transactions",
    "delta.feature.timestampNtz" = "supported"
)
AS SELECT
    -- Keys
    TRIM(txn_id) AS txn_id,
    TRIM(order_id) AS order_id,
    TRIM(payment_id) AS payment_id,

    -- Amount fields: cents preserved + dollar conversion
    currency AS transaction_currency,
    amount_cents,
    CAST(amount_cents / 100.0 AS DECIMAL(18,2)) AS transaction_amount,

    -- State lifecycle normalization
    LOWER(state.state_name) AS transaction_state,
    from_unixtime(CAST(state.timestamp AS BIGINT) / 1000) AS state_timestamp,

    CASE
        WHEN state.state_name IN ('completed', 'closed') THEN 'terminal_success'
        WHEN state.state_name IN ('failed', 'cancelled') THEN 'terminal_failure'
        WHEN state.state_name IN ('disputed', 'under_review', 'chargeback') THEN 'disputed'
        WHEN state.state_name IN ('refunded', 'refund_pending') THEN 'refunded'
        ELSE 'in_progress'
    END AS transaction_state_category,

    -- Response code decoding
    TRIM(response_code) AS response_code,
    CASE
        WHEN response_code = '00' THEN 'approved'
        WHEN response_code = '05' THEN 'do_not_honor'
        WHEN response_code = '51' THEN 'insufficient_funds'
        WHEN response_code = '54' THEN 'expired_card'
        WHEN response_code = '61' THEN 'exceeds_limit'
        WHEN response_code = '65' THEN 'activity_limit'
        ELSE 'other_decline'
    END AS response_code_description,

    -- 3DS authentication
    LOWER(three_ds) AS three_ds_status,
    CASE
        WHEN three_ds IN ('frictionless', 'challenge') THEN TRUE
        ELSE FALSE
    END AS is_3ds_authenticated,

    -- Fee calculations
    fees_total_cents,
    CAST(fees_total_cents / 100.0 AS DECIMAL(18,2)) AS fees_total_amount,
    network_fee_cents,
    CAST(network_fee_cents / 100.0 AS DECIMAL(18,2)) AS network_fee_amount,
    CAST((fees_total_cents * 100.0 / amount_cents) AS DECIMAL(8,4)) AS effective_fee_rate_pct,

    -- Net amount (gross minus fees)
    amount_cents - fees_total_cents AS net_amount_cents,
    CAST((amount_cents - fees_total_cents) / 100.0 AS DECIMAL(18,2)) AS net_amount,

    -- Processor
    LOWER(processor_name) AS processor_name,

    -- Boolean flags for common query filters
    CASE WHEN state.state_name IN ('completed', 'closed') THEN TRUE ELSE FALSE END AS is_successful,
    CASE WHEN state.state_name IN ('declined', 'failed') THEN TRUE ELSE FALSE END AS is_failed,
    CASE WHEN state.state_name IN ('disputed', 'under_review', 'chargeback') THEN TRUE ELSE FALSE END AS is_disputed,
    CASE WHEN response_code != '00' THEN TRUE ELSE FALSE END AS is_declined,

    -- Time dimensions
    authorized_at AS transaction_authorized_at,
    CAST(authorized_at AS DATE) AS transaction_date,
    HOUR(authorized_at) AS transaction_hour,
    DAYOFWEEK(authorized_at) AS transaction_day_of_week,

    -- Lineage
    _ingested_at,
    current_timestamp() AS _processed_at

FROM STREAM(`${catalog}`.bronze.psp_transactions);
