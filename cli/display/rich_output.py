from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cli.models import LayerResult, LayerStatus, TraceResult

console = Console()

STATUS_ICONS = {
    LayerStatus.OK: "[green]✔[/green]",
    LayerStatus.SKIPPED: "[yellow]⚠[/yellow]",
    LayerStatus.ERROR: "[red]✘[/red]",
    LayerStatus.NOT_FOUND: "[dim]--[/dim]",
}


def render_trace(result: TraceResult, verbose: bool = False) -> None:
    table = Table(title=f"FlowCheck Trace: {result.filename} ({result.file_type})")
    table.add_column("#", style="dim", width=3)
    table.add_column("Layer", min_width=24)
    table.add_column("Status", min_width=8)
    table.add_column("Details", min_width=40)

    for i, layer in enumerate(result.layers, 1):
        icon = STATUS_ICONS[layer.status]
        detail = _format_detail(layer, verbose)
        table.add_row(str(i), layer.layer, icon, detail)

    console.print(table)


def render_status_dashboard(
    rows: list[dict[str, Any]],
    env: str = "dev",
) -> None:
    table = Table(title=f"FlowCheck Status Dashboard — PSP ({env})")
    table.add_column("Entity", style="bold", min_width=14)
    table.add_column("Blob Files", min_width=12)
    table.add_column("Pipeline", min_width=12)
    table.add_column("Bronze", min_width=10)
    table.add_column("Silver", min_width=10)
    table.add_column("Gold", min_width=10)

    for row in rows:
        table.add_row(
            row["type"],
            _status_cell(row.get("blob")),
            _status_cell(row.get("pipeline")),
            _status_cell(row.get("bronze")),
            _status_cell(row.get("silver")),
            _status_cell(row.get("gold")),
        )

    console.print(table)


def render_profile_comparison(
    file_type: str,
    layers: list[LayerResult],
    env: str = "dev",
) -> None:
    table = Table(title=f"FlowCheck Profile: {file_type} ({env})")
    table.add_column("Layer", min_width=24)
    table.add_column("Status", min_width=8)
    table.add_column("Row Count", justify="right", min_width=12)
    table.add_column("Delta", justify="right", min_width=10)
    table.add_column("% Change", justify="right", min_width=10)

    prev_count = None
    for layer in layers:
        icon = STATUS_ICONS[layer.status]
        row_count = layer.data.get("row_count")

        if row_count is not None:
            count_str = f"{row_count:,}"
            if prev_count is not None and prev_count > 0:
                delta = row_count - prev_count
                pct = (delta / prev_count) * 100
                delta_str = f"{delta:+,}"
                pct_str = f"{pct:+.1f}%"
                if delta < 0:
                    delta_str = f"[red]{delta_str}[/red]"
                    pct_str = f"[red]{pct_str}[/red]"
            else:
                delta_str = "--"
                pct_str = "--"
            prev_count = row_count
        else:
            count_str = "--"
            delta_str = "--"
            pct_str = "--"

        table.add_row(layer.layer, icon, count_str, delta_str, pct_str)

    console.print(table)


def render_blob_objects(blobs: list[dict[str, Any]], title: str = "Azure Blobs") -> None:
    table = Table(title=title)
    table.add_column("Blob Name", min_width=40)
    table.add_column("Size", justify="right", min_width=10)
    table.add_column("Last Modified", min_width=24)

    for blob in blobs:
        size_mb = blob.get("size_bytes", 0) / (1024 * 1024)
        table.add_row(
            blob.get("name", ""),
            f"{size_mb:.2f} MB",
            blob.get("last_modified", ""),
        )

    console.print(table)


def render_volume_files(files: list[dict[str, Any]], title: str = "UC Volume") -> None:
    table = Table(title=title)
    table.add_column("Name", min_width=40)
    table.add_column("Size", justify="right", min_width=10)
    table.add_column("Type", min_width=10)

    for f in files:
        size = f.get("size_bytes")
        size_str = f"{size / (1024*1024):.2f} MB" if size else "--"
        ftype = "DIR" if f.get("is_directory") else "FILE"
        table.add_row(f.get("name", ""), size_str, ftype)

    console.print(table)


def render_parquet_info(files: list[dict[str, Any]]) -> None:
    table = Table(title="Parquet Inspection")
    table.add_column("File", min_width=30)
    table.add_column("Rows", justify="right", min_width=8)
    table.add_column("Columns", justify="right", min_width=8)
    table.add_column("Size", justify="right", min_width=10)

    for f in files:
        table.add_row(
            f.get("filename", ""),
            f"{f.get('row_count', 0):,}",
            str(f.get("num_columns", 0)),
            f"{f.get('size_mb', 0):.2f} MB",
        )

    console.print(table)


def render_parquet_schema(schema_info: dict[str, Any]) -> None:
    table = Table(title=f"Schema: {schema_info.get('filename', '')}")
    table.add_column("Column", min_width=30)
    table.add_column("Type", min_width=20)

    for col in schema_info.get("columns", []):
        table.add_row(col["name"], col["type"])

    console.print(table)


def render_parquet_sample(sample: dict[str, Any]) -> None:
    rows = sample.get("rows", [])
    columns = sample.get("columns", [])
    if not rows or not columns:
        console.print("[dim]No sample data available[/dim]")
        return

    table = Table(title=f"Sample: {sample.get('filename', '')} ({len(rows)} rows)")
    for col in columns:
        table.add_column(col, max_width=30)

    for row in rows:
        table.add_row(*[str(row.get(c, "")) for c in columns])

    console.print(table)


def render_pipeline_info(data: dict[str, Any]) -> None:
    latest = data.get("latest_update")
    update_info = ""
    if latest:
        update_info = (
            f"\nLast Update: {latest.get('state', 'N/A')}"
            f" ({latest.get('creation_time', 'N/A')})"
        )

    panel = Panel(
        f"[bold]{data.get('name', 'Unknown')}[/bold]\n"
        f"Pipeline ID: {data.get('pipeline_id', 'N/A')}\n"
        f"State: {data.get('state', 'UNKNOWN')}"
        f"{update_info}",
        title="Lakeflow Pipeline",
    )
    console.print(panel)


def render_log_entries(entries: list[dict[str, Any]], title: str = "Log Entries") -> None:
    table = Table(title=title)
    table.add_column("Timestamp", min_width=24)
    table.add_column("Message", min_width=60)

    for entry in entries:
        table.add_row(
            entry.get("timestamp", ""),
            entry.get("message", ""),
        )

    console.print(table)


def render_layer_result(result: LayerResult) -> None:
    icon = STATUS_ICONS[result.status]
    if result.status == LayerStatus.OK:
        detail = _format_detail(result, verbose=True)
        console.print(f"{icon} {result.layer}: {detail}")
    elif result.status == LayerStatus.SKIPPED:
        console.print(f"{icon} {result.layer}: [yellow]{result.message}[/yellow]")
    elif result.status == LayerStatus.ERROR:
        console.print(f"{icon} {result.layer}: [red]{result.message}[/red]")
    else:
        console.print(f"{icon} {result.layer}: [dim]{result.message}[/dim]")


def _status_cell(result: LayerResult | None) -> str:
    if result is None:
        return "[dim]--[/dim]"
    icon = STATUS_ICONS[result.status]
    if result.status == LayerStatus.OK:
        row_count = result.data.get("row_count")
        count = result.data.get("count")
        state = result.data.get("state")
        if row_count is not None:
            return f"{icon} {row_count:,}"
        if count is not None:
            return f"{icon} {count} files"
        if state is not None:
            return f"{icon} {state}"
        return f"{icon} OK"
    if result.status == LayerStatus.SKIPPED:
        return f"{icon} SKIP"
    if result.status == LayerStatus.ERROR:
        return f"{icon} ERR"
    return f"{icon} N/A"


def _format_detail(layer: LayerResult, verbose: bool) -> str:
    if layer.status == LayerStatus.SKIPPED:
        return f"[yellow]{layer.message}[/yellow]"
    if layer.status == LayerStatus.ERROR:
        return f"[red]{layer.message}[/red]"
    if layer.status == LayerStatus.NOT_FOUND:
        return f"[dim]{layer.message}[/dim]"

    data = layer.data
    if "size_bytes" in data and "name" in data:
        size_mb = data["size_bytes"] / (1024 * 1024)
        return f"Found ({size_mb:.1f} MB) — {data.get('name', '')}"
    if "blob_name" in data:
        size_mb = data.get("size_bytes", 0) / (1024 * 1024)
        return f"Uploaded ({size_mb:.1f} MB) → {data['blob_name']}"
    if "blobs" in data:
        return f"{data['count']} blob(s) found"
    if "files" in data:
        return f"{data['count']} file(s) found"
    if "row_count" in data:
        return f"{data['row_count']:,} rows"
    if "count" in data:
        return f"{data['count']} files"
    if "state" in data:
        return f"{data['state']}"
    return layer.message or (str(data) if verbose else "OK")
