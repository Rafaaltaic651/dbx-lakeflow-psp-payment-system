from __future__ import annotations

import typer

from cli.commands.blob import blob_app
from cli.commands.inspect_cmd import inspect_app
from cli.commands.logs import logs_app
from cli.commands.profile import profile
from cli.commands.status import status
from cli.commands.trace import trace

app = typer.Typer(
    name="flowcheck",
    help="FlowCheck — End-to-End Pipeline Debugger for PSP Payment System\n\n"
    "Trace data from Azure Blob Storage → UC Volumes → Bronze → Silver → Gold",
    no_args_is_help=True,
)

app.command()(trace)
app.command()(status)
app.command()(profile)
app.add_typer(blob_app, name="blob", help="Azure Blob Storage operations")
app.add_typer(inspect_app, name="inspect", help="Inspect Blob, Volume, Parquet, or pipeline")
app.add_typer(logs_app, name="logs", help="Query Lakeflow pipeline logs")
