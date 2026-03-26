from __future__ import annotations

from typing import Optional

import typer

from cli.config import FlowConfig, EntityType
from cli.display.rich_output import render_status_dashboard
from cli.services.blob_service import AzureBlobService
from cli.services.databricks_service import DatabricksService


def status(
    entity: Optional[EntityType] = typer.Option(
        None, "--entity", "-t", help="Filter by entity type (default: all)"
    ),
    env: str = typer.Option("dev", "--env", "-e", help="Environment (dev/prd)"),
) -> None:
    """Show pipeline health dashboard across all entity types."""
    entities = [entity] if entity else FlowConfig.all_entities()

    # Share the Databricks client across entities for performance
    first_config = FlowConfig(entity=entities[0], env=env)
    shared_dbx = DatabricksService(first_config)
    _ = shared_dbx.client  # warm up the client once

    rows = []
    for ent in entities:
        config = FlowConfig(entity=ent, env=env)
        blob = AzureBlobService(config)
        dbx = DatabricksService(config, client=shared_dbx.client)

        row = {
            "type": ent.value.title(),
            "blob": blob.list_blobs(),
            "pipeline": dbx.get_pipeline_status() if ent == entities[0] else None,
            "bronze": dbx.query_row_count("bronze"),
            "silver": dbx.query_row_count("silver"),
            "gold": dbx.query_row_count("gold"),
        }
        rows.append(row)

    render_status_dashboard(rows, env=env)
