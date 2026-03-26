-- Databricks notebook source
-- Entity: Payouts (Settlements)
-- Layer: Bronze - Raw Ingestion
-- Source: UC Volume landing zone - settlement and payout funding files

CREATE OR REFRESH STREAMING TABLE `${catalog}`.bronze.psp_payouts
COMMENT "Raw settlement and payout batch data from PSP funding engine - gross, fees, reserves, net amounts"
TBLPROPERTIES (
    "quality" = "bronze",
    "source_system" = "psp_funding",
    "domain" = "payouts",
    "delta.feature.timestampNtz" = "supported"
)
AS SELECT
    *,
    current_timestamp() AS _ingested_at,
    _metadata.file_path AS _source_file,
    _metadata.file_name AS _source_file_name,
    _metadata.file_modification_time AS _source_file_modified
FROM STREAM read_files(
    "${landing_volume}/payouts/",
    format => "json",
    schemaEvolutionMode => "addNewColumns"
);
