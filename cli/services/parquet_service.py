from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from cli.models import LayerResult, LayerStatus

logger = logging.getLogger(__name__)


class ParquetService:
    def inspect_path(self, path: str, sample_rows: int = 5) -> LayerResult:
        target = Path(path)
        try:
            if target.is_file():
                files = [target]
            elif target.is_dir():
                files = sorted(target.glob("*.parquet"))
            else:
                return LayerResult(
                    layer="Parquet",
                    status=LayerStatus.NOT_FOUND,
                    message=f"Path not found: {path}",
                )

            if not files:
                return LayerResult(
                    layer="Parquet",
                    status=LayerStatus.NOT_FOUND,
                    message=f"No Parquet files found in {path}",
                )

            file_infos = []
            for f in files:
                info = self._read_file_info(f)
                file_infos.append(info)

            return LayerResult(
                layer="Parquet",
                status=LayerStatus.OK,
                data={"files": file_infos, "count": len(file_infos)},
            )
        except Exception as e:
            return LayerResult(
                layer="Parquet",
                status=LayerStatus.ERROR,
                message=str(e),
            )

    def get_schema(self, path: str) -> LayerResult:
        target = Path(path)
        try:
            if target.is_dir():
                files = sorted(target.glob("*.parquet"))
                if not files:
                    return LayerResult(
                        layer="Parquet Schema",
                        status=LayerStatus.NOT_FOUND,
                        message=f"No Parquet files in {path}",
                    )
                target = files[0]

            metadata = pq.read_metadata(target)
            schema = pq.read_schema(target)
            columns = []
            for i in range(len(schema)):
                columns.append({
                    "name": schema.field(i).name,
                    "type": str(schema.field(i).type),
                })

            return LayerResult(
                layer="Parquet Schema",
                status=LayerStatus.OK,
                data={
                    "filename": target.name,
                    "columns": columns,
                    "num_columns": len(columns),
                    "row_count": metadata.num_rows,
                },
            )
        except Exception as e:
            return LayerResult(
                layer="Parquet Schema",
                status=LayerStatus.ERROR,
                message=str(e),
            )

    def get_sample(self, path: str, num_rows: int = 5) -> LayerResult:
        target = Path(path)
        try:
            if target.is_dir():
                files = sorted(target.glob("*.parquet"))
                if not files:
                    return LayerResult(
                        layer="Parquet Sample",
                        status=LayerStatus.NOT_FOUND,
                        message=f"No Parquet files in {path}",
                    )
                target = files[0]

            table = pq.read_table(target)
            sample = table.slice(0, min(num_rows, len(table)))
            columns = [field.name for field in table.schema]
            rows = []
            for i in range(len(sample)):
                row = {}
                for col in columns:
                    val = sample.column(col)[i].as_py()
                    row[col] = val
                rows.append(row)

            return LayerResult(
                layer="Parquet Sample",
                status=LayerStatus.OK,
                data={
                    "filename": target.name,
                    "columns": columns,
                    "rows": rows,
                    "total_rows": len(table),
                },
            )
        except Exception as e:
            return LayerResult(
                layer="Parquet Sample",
                status=LayerStatus.ERROR,
                message=str(e),
            )

    def _read_file_info(self, path: Path) -> dict[str, Any]:
        metadata = pq.read_metadata(path)
        return {
            "filename": path.name,
            "path": str(path),
            "row_count": metadata.num_rows,
            "num_columns": metadata.num_columns,
            "size_mb": path.stat().st_size / (1024 * 1024),
        }
