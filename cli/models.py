from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LayerStatus(str, Enum):
    OK = "ok"
    SKIPPED = "skipped"
    ERROR = "error"
    NOT_FOUND = "not_found"


@dataclass(frozen=True)
class LayerResult:
    layer: str
    status: LayerStatus
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    @property
    def is_ok(self) -> bool:
        return self.status == LayerStatus.OK


@dataclass(frozen=True)
class TraceResult:
    filename: str
    file_type: str
    layers: list[LayerResult] = field(default_factory=list)

    @property
    def all_ok(self) -> bool:
        return all(lr.is_ok for lr in self.layers)
