-- Databricks notebook source
-- Entity: Merchants
-- Layer: Bronze - Raw Ingestion
-- Source: UC Volume landing zone - merchant profiles and onboarding data

CREATE OR REFRESH STREAMING TABLE `${catalog}`.bronze.psp_merchants
COMMENT "Raw merchant account profiles from PSP onboarding system - KYB, pricing, risk, and MCC data"
TBLPROPERTIES (
    "quality" = "bronze",
    "source_system" = "psp_onboarding",
    "domain" = "merchants",
    "delta.feature.timestampNtz" = "supported"
)
AS SELECT
    *,
    current_timestamp() AS _ingested_at,
    _metadata.file_path AS _source_file,
    _metadata.file_name AS _source_file_name,
    _metadata.file_modification_time AS _source_file_modified
FROM STREAM read_files(
    "${landing_volume}/merchants/",
    format => "json",
    schemaEvolutionMode => "addNewColumns"
);
