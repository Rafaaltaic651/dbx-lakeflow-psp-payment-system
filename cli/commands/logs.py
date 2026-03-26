from __future__ import annotations

import typer

from cli.config import FlowConfig, EntityType
from cli.display.rich_output import render_layer_result, render_log_entries
from cli.services.databricks_service import DatabricksService

logs_app = typer.Typer(help="Query Lakeflow pipeline logs")


@logs_app.command("pipeline")
def logs_pipeline(
    env: str = typer.Option("dev", "--env", "-e", help="Environment"),
) -> None:
    """Query Lakeflow pipeline event logs."""
    config = FlowConfig(entity=EntityType.TRANSACTIONS, env=env)
    dbx = DatabricksService(config)

    result = dbx.get_pipeline_events()
    if result.is_ok:
        render_log_entries(
            result.data["entries"],
            title=f"Pipeline Events: {config.pipeline_name} ({result.data['count']} events)",
        )
    else:
        render_layer_result(result)
