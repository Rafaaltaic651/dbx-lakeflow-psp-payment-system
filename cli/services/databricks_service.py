from __future__ import annotations

import logging
import os
import subprocess

from cli.config import FlowConfig
from cli.models import LayerResult, LayerStatus

logger = logging.getLogger(__name__)


class DatabricksService:
    def __init__(self, config: FlowConfig, client=None):
        self._config = config
        self._client = client

    @property
    def client(self):
        if self._client is None:
            from databricks.sdk import WorkspaceClient

            host = self._config.databricks_host
            token = os.environ.get("DATABRICKS_TOKEN")
            if token:
                self._client = WorkspaceClient(host=host, token=token)
            else:
                # Check if databricks CLI auth is available (non-blocking)
                try:
                    result = subprocess.run(
                        ["databricks", "auth", "token", "--host", host],
                        capture_output=True, text=True, timeout=5,
                    )
                    if result.returncode != 0:
                        raise RuntimeError("Databricks auth not configured")
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    raise RuntimeError("Databricks auth not configured")
                self._client = WorkspaceClient(host=host)
        return self._client

    def _find_pipeline(self):
        pipelines = list(
            self.client.pipelines.list_pipelines(
                filter=f"name LIKE '%{self._config.pipeline_name}'"
            )
        )
        return pipelines[0] if pipelines else None

    def get_pipeline_status(self) -> LayerResult:
        try:
            pipeline = self._find_pipeline()
            if not pipeline:
                return LayerResult(
                    layer="Lakeflow Pipeline",
                    status=LayerStatus.NOT_FOUND,
                    message=f"Pipeline '{self._config.pipeline_name}' not found",
                )
            latest_update = None
            if hasattr(pipeline, "latest_updates") and pipeline.latest_updates:
                lu = pipeline.latest_updates[0]
                latest_update = {
                    "update_id": lu.update_id,
                    "state": lu.state.value if lu.state else "UNKNOWN",
                    "creation_time": str(lu.creation_time) if lu.creation_time else None,
                }
            return LayerResult(
                layer="Lakeflow Pipeline",
                status=LayerStatus.OK,
                data={
                    "pipeline_id": pipeline.pipeline_id,
                    "name": pipeline.name,
                    "state": pipeline.state.value if pipeline.state else "UNKNOWN",
                    "latest_update": latest_update,
                },
            )
        except Exception as e:
            return self._handle_error("Lakeflow Pipeline", e)

    def query_row_count(self, layer: str) -> LayerResult:
        table_name = self._config.full_table_name(layer)
        if table_name is None:
            return LayerResult(
                layer=f"{layer.title()} ({self._config.entity.value})",
                status=LayerStatus.NOT_FOUND,
                message=f"No {layer} table defined for {self._config.entity.value}",
            )

        display_table = self._config.table_name(layer)
        layer_label = f"{layer.title()} ({display_table})"
        try:
            result = self.client.statement_execution.execute_statement(
                warehouse_id=self._get_warehouse_id(),
                statement=f"SELECT COUNT(*) AS cnt FROM {table_name}",
                wait_timeout="30s",
            )
            row_count = int(result.result.data_array[0][0])
            return LayerResult(
                layer=layer_label,
                status=LayerStatus.OK,
                data={"table": table_name, "row_count": row_count},
            )
        except Exception as e:
            return self._handle_error(layer_label, e)

    def list_volume_files(self, volume_path: str | None = None) -> LayerResult:
        path = volume_path or self._config.volume_path
        try:
            files = []
            for entry in self.client.files.list_directory_contents(path):
                files.append({
                    "name": entry.name,
                    "path": entry.path,
                    "size_bytes": entry.file_size if hasattr(entry, "file_size") else None,
                    "is_directory": entry.is_directory,
                    "last_modified": str(entry.last_modified) if hasattr(entry, "last_modified") and entry.last_modified else None,
                })
            if not files:
                return LayerResult(
                    layer="UC Volume",
                    status=LayerStatus.NOT_FOUND,
                    message=f"No files in volume: {path}",
                )
            return LayerResult(
                layer="UC Volume",
                status=LayerStatus.OK,
                data={"files": files, "count": len(files), "path": path},
            )
        except Exception as e:
            if "NOT_FOUND" in str(e) or "404" in str(e):
                return LayerResult(
                    layer="UC Volume",
                    status=LayerStatus.NOT_FOUND,
                    message=f"Volume path not found: {path}",
                )
            return self._handle_error("UC Volume", e)

    def get_pipeline_events(self) -> LayerResult:
        try:
            pipeline = self._find_pipeline()
            if not pipeline:
                return LayerResult(
                    layer="Pipeline Events",
                    status=LayerStatus.NOT_FOUND,
                    message=f"Pipeline '{self._config.pipeline_name}' not found",
                )
            pipeline_id = pipeline.pipeline_id
            events = list(self.client.pipelines.list_pipeline_events(pipeline_id=pipeline_id))
            entries = []
            for event in events[:50]:
                entries.append({
                    "timestamp": str(event.timestamp) if event.timestamp else "",
                    "message": event.message or "",
                })
            return LayerResult(
                layer="Pipeline Events",
                status=LayerStatus.OK,
                data={"entries": entries, "count": len(entries), "pipeline_id": pipeline_id},
            )
        except Exception as e:
            return self._handle_error("Pipeline Events", e)

    def _get_warehouse_id(self) -> str:
        warehouses = list(self.client.warehouses.list())
        for wh in warehouses:
            if wh.state and wh.state.value == "RUNNING":
                return wh.id
        if warehouses:
            return warehouses[0].id
        raise RuntimeError("No SQL warehouse found")

    @staticmethod
    def _handle_error(layer: str, error: Exception) -> LayerResult:
        msg = str(error).lower()
        if "authentication" in msg or "token" in msg or "credential" in msg:
            return LayerResult(
                layer=layer,
                status=LayerStatus.SKIPPED,
                message="Databricks credentials not configured — run: databricks auth login",
            )
        return LayerResult(
            layer=layer,
            status=LayerStatus.ERROR,
            message=str(error),
        )
