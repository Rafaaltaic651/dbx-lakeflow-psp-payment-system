from __future__ import annotations

from typing import Optional

import typer

from cli.config import FlowConfig, EntityType
from cli.display.rich_output import (
    render_blob_objects,
    render_layer_result,
    render_parquet_info,
    render_parquet_sample,
    render_parquet_schema,
    render_pipeline_info,
    render_volume_files,
)
from cli.services.blob_service import AzureBlobService
from cli.services.databricks_service import DatabricksService
from cli.services.parquet_service import ParquetService

inspect_app = typer.Typer(help="Inspect Azure Blob, UC Volume, Parquet, or pipeline")


@inspect_app.command("blob")
def inspect_blob(
    entity: EntityType = typer.Argument(help="Entity type (merchants, customers, ...)"),
    env: str = typer.Option("dev", "--env", "-e", help="Environment"),
) -> None:
    """List blobs in Azure Blob Storage for an entity."""
    config = FlowConfig(entity=entity, env=env)
    blob = AzureBlobService(config)

    result = blob.list_blobs()
    if result.is_ok:
        render_blob_objects(
            result.data["blobs"],
            title=f"{config.container}/{entity.value}/",
        )
    else:
        render_layer_result(result)


@inspect_app.command("volume")
def inspect_volume(
    entity: EntityType = typer.Argument(help="Entity type (merchants, customers, ...)"),
    env: str = typer.Option("dev", "--env", "-e", help="Environment"),
) -> None:
    """List files in UC Volume landing zone for an entity."""
    config = FlowConfig(entity=entity, env=env)
    dbx = DatabricksService(config)

    result = dbx.list_volume_files()
    if result.is_ok:
        render_volume_files(
            result.data["files"],
            title=f"Volume: {config.volume_path}",
        )
    else:
        render_layer_result(result)


@inspect_app.command("parquet")
def inspect_parquet(
    path: str = typer.Argument(help="Local file or directory path"),
    sample: int = typer.Option(5, "--sample", "-s", help="Number of sample rows"),
) -> None:
    """Inspect local Parquet file(s): schema, row count, sample data."""
    svc = ParquetService()

    info_result = svc.inspect_path(path)
    if info_result.is_ok:
        render_parquet_info(info_result.data["files"])
    else:
        render_layer_result(info_result)
        return

    schema_result = svc.get_schema(path)
    if schema_result.is_ok:
        render_parquet_schema(schema_result.data)

    sample_result = svc.get_sample(path, num_rows=sample)
    if sample_result.is_ok:
        render_parquet_sample(sample_result.data)


@inspect_app.command("pipeline")
def inspect_pipeline(
    env: str = typer.Option("dev", "--env", "-e", help="Environment"),
) -> None:
    """Inspect Lakeflow pipeline state."""
    config = FlowConfig(entity=EntityType.TRANSACTIONS, env=env)
    dbx = DatabricksService(config)

    result = dbx.get_pipeline_status()
    if result.is_ok:
        render_pipeline_info(result.data)
    else:
        render_layer_result(result)
