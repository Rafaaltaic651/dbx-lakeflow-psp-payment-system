from __future__ import annotations

from typing import Optional

import typer

from cli.config import FlowConfig, EntityType
from cli.display.rich_output import render_trace
from cli.models import TraceResult
from cli.services.blob_service import AzureBlobService
from cli.services.databricks_service import DatabricksService


def trace(
    entity: EntityType = typer.Argument(help="Entity type to trace"),
    env: str = typer.Option("dev", "--env", "-e", help="Environment (dev/prd)"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Trace an entity's journey from Azure Blob → UC Volume → Bronze → Silver → Gold."""
    config = FlowConfig(entity=entity, env=env)
    blob = AzureBlobService(config)
    dbx = DatabricksService(config)

    layers = []

    # 1. Azure Blob Storage
    layers.append(blob.list_blobs())

    # 2. UC Volume landing zone
    layers.append(dbx.list_volume_files())

    # 3. Bronze → Silver → Gold
    layers.append(dbx.query_row_count("bronze"))
    layers.append(dbx.query_row_count("silver"))
    layers.append(dbx.query_row_count("gold"))

    result = TraceResult(
        filename=entity.value,
        file_type=entity.value,
        layers=layers,
    )
    render_trace(result, verbose=verbose)
