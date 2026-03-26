-- Databricks notebook source
-- Entity: Customers
-- Layer: Bronze - Raw Ingestion
-- Source: UC Volume landing zone - customer profile data with pre-hashed PII

CREATE OR REFRESH STREAMING TABLE `${catalog}`.bronze.psp_customers
COMMENT "Raw customer profile data from PSP system - PII fields pre-hashed at source"
TBLPROPERTIES (
    "quality" = "bronze",
    "source_system" = "psp_gateway",
    "domain" = "customers",
    "delta.feature.timestampNtz" = "supported"
)
AS SELECT
    *,
    current_timestamp() AS _ingested_at,
    _metadata.file_path AS _source_file,
    _metadata.file_name AS _source_file_name,
    _metadata.file_modification_time AS _source_file_modified
FROM STREAM read_files(
    "${landing_volume}/customers/",
    format => "json",
    schemaEvolutionMode => "addNewColumns"
);
