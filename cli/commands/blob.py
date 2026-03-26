from __future__ import annotations

from pathlib import Path

import typer

from cli.config import FlowConfig, EntityType
from cli.display.rich_output import render_blob_objects, render_layer_result
from cli.services.blob_service import AzureBlobService

blob_app = typer.Typer(help="Azure Blob Storage operations")


@blob_app.command("list")
def blob_list(
    entity: EntityType = typer.Argument(help="Entity type (merchants, customers, ...)"),
    env: str = typer.Option("dev", "--env", "-e", help="Environment"),
) -> None:
    """List blobs in Azure Blob Storage for an entity."""
    config = FlowConfig(entity=entity, env=env)
    svc = AzureBlobService(config)

    result = svc.list_blobs()
    if result.is_ok:
        render_blob_objects(
            result.data["blobs"],
            title=f"{config.container}/{entity.value}/",
        )
    else:
        render_layer_result(result)


@blob_app.command("upload")
def blob_upload(
    entity: EntityType = typer.Argument(help="Entity type (merchants, customers, ...)"),
    file: str = typer.Option(
        None, "--file", "-f",
        help="Path to local JSONL file (default: data/<entity>.jsonl)",
    ),
    env: str = typer.Option("dev", "--env", "-e", help="Environment"),
) -> None:
    """Upload local JSONL file to Azure Blob Storage."""
    config = FlowConfig(entity=entity, env=env)
    svc = AzureBlobService(config)

    if file is None:
        file = str(Path("data") / f"{entity.value}.jsonl")

    result = svc.upload_blob(file)
    render_layer_result(result)
