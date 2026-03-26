-- Databricks notebook source
-- Entity: Orders
-- Layer: Bronze - Raw Ingestion
-- Source: UC Volume landing zone - order records linking merchants and customers

CREATE OR REFRESH STREAMING TABLE `${catalog}`.bronze.psp_orders
COMMENT "Raw order transaction data from PSP system - links merchants, customers, and amounts"
TBLPROPERTIES (
    "quality" = "bronze",
    "source_system" = "psp_gateway",
    "domain" = "orders",
    "delta.feature.timestampNtz" = "supported"
)
AS SELECT
    *,
    current_timestamp() AS _ingested_at,
    _metadata.file_path AS _source_file,
    _metadata.file_name AS _source_file_name,
    _metadata.file_modification_time AS _source_file_modified
FROM STREAM read_files(
    "${landing_volume}/orders/",
    format => "json",
    schemaEvolutionMode => "addNewColumns"
);
