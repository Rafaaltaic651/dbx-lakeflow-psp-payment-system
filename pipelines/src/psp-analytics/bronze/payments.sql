-- Databricks notebook source
-- Entity: Payments (Payment Instruments)
-- Layer: Bronze - Raw Ingestion
-- Source: UC Volume landing zone - tokenized card and wallet records

CREATE OR REFRESH STREAMING TABLE `${catalog}`.bronze.psp_payment_instruments
COMMENT "Raw payment instrument data from PSP system - tokenized card and wallet records"
TBLPROPERTIES (
    "quality" = "bronze",
    "source_system" = "psp_gateway",
    "domain" = "payments",
    "delta.feature.timestampNtz" = "supported"
)
AS SELECT
    *,
    current_timestamp() AS _ingested_at,
    _metadata.file_path AS _source_file,
    _metadata.file_name AS _source_file_name,
    _metadata.file_modification_time AS _source_file_modified
FROM STREAM read_files(
    "${landing_volume}/payments/",
    format => "json",
    schemaEvolutionMode => "addNewColumns"
);
