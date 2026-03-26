-- Databricks notebook source
-- Entity: Disputes (Chargebacks)
-- Layer: Bronze - Raw Ingestion
-- Source: UC Volume landing zone - chargeback and dispute records

CREATE OR REFRESH STREAMING TABLE `${catalog}`.bronze.psp_disputes
COMMENT "Raw chargeback and dispute records from PSP dispute management - reason codes, stages, liability, resolution"
TBLPROPERTIES (
    "quality" = "bronze",
    "source_system" = "psp_disputes",
    "domain" = "disputes",
    "delta.feature.timestampNtz" = "supported"
)
AS SELECT
    *,
    current_timestamp() AS _ingested_at,
    _metadata.file_path AS _source_file,
    _metadata.file_name AS _source_file_name,
    _metadata.file_modification_time AS _source_file_modified
FROM STREAM read_files(
    "${landing_volume}/disputes/",
    format => "json",
    schemaEvolutionMode => "addNewColumns"
);
