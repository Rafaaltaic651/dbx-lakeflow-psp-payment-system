-- Databricks notebook source
-- Entity: Transactions
-- Layer: Bronze - Raw Ingestion
-- Source: UC Volume landing zone - payment gateway transaction events

CREATE OR REFRESH STREAMING TABLE `${catalog}`.bronze.psp_transactions
COMMENT "Raw payment transaction events from PSP payment gateway - includes state lifecycle, authorization, and fee data"
TBLPROPERTIES (
    "quality" = "bronze",
    "source_system" = "psp_gateway",
    "domain" = "transactions",
    "delta.feature.timestampNtz" = "supported"
)
AS SELECT
    *,
    current_timestamp() AS _ingested_at,
    _metadata.file_path AS _source_file,
    _metadata.file_name AS _source_file_name,
    _metadata.file_modification_time AS _source_file_modified
FROM STREAM read_files(
    "${landing_volume}/transactions/",
    format => "json",
    schemaEvolutionMode => "addNewColumns"
);
