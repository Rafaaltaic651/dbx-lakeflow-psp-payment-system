from __future__ import annotations

import typer

from cli.config import FlowConfig, EntityType
from cli.display.rich_output import render_profile_comparison
from cli.models import LayerResult, LayerStatus
from cli.services.blob_service import AzureBlobService
from cli.services.databricks_service import DatabricksService


def profile(
    entity: EntityType = typer.Argument(help="Entity type (merchants, customers, ...)"),
    env: str = typer.Option("dev", "--env", "-e", help="Environment"),
) -> None:
    """Show cross-layer row count profile for an entity type."""
    config = FlowConfig(entity=entity, env=env)
    blob = AzureBlobService(config)
    dbx = DatabricksService(config)

    layers: list[LayerResult] = []

    # Blob storage file count
    blob_result = blob.list_blobs()
    if blob_result.is_ok:
        layers.append(LayerResult(
            layer="Azure Blob (files)",
            status=LayerStatus.OK,
            data={"row_count": blob_result.data["count"]},
        ))
    else:
        layers.append(LayerResult(
            layer="Azure Blob (files)",
            status=blob_result.status,
            message=blob_result.message,
        ))

    # Volume file count
    volume_result = dbx.list_volume_files()
    if volume_result.is_ok:
        layers.append(LayerResult(
            layer="UC Volume (files)",
            status=LayerStatus.OK,
            data={"row_count": volume_result.data["count"]},
        ))
    else:
        layers.append(LayerResult(
            layer="UC Volume (files)",
            status=volume_result.status,
            message=volume_result.message,
        ))

    # Medallion layers
    layers.append(dbx.query_row_count("bronze"))
    layers.append(dbx.query_row_count("silver"))
    layers.append(dbx.query_row_count("gold"))

    render_profile_comparison(
        file_type=entity.value,
        layers=layers,
        env=env,
    )
