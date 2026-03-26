from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path

from cli.config import FlowConfig
from cli.models import LayerResult, LayerStatus

logger = logging.getLogger(__name__)


def _get_az_storage_token() -> str | None:
    """Get Azure Storage access token via az CLI (fast, non-blocking)."""
    try:
        result = subprocess.run(
            ["az", "account", "get-access-token",
             "--resource", "https://storage.azure.com/",
             "--query", "accessToken", "-o", "tsv"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


class AzureBlobService:
    def __init__(self, config: FlowConfig, client=None):
        self._config = config
        self._client = client

    @property
    def client(self):
        if self._client is None:
            from azure.storage.blob import BlobServiceClient

            conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
            if conn_str:
                self._client = BlobServiceClient.from_connection_string(conn_str)
            else:
                token = _get_az_storage_token()
                if token is None:
                    raise RuntimeError(
                        "Azure credentials not available. "
                        "Run: az login   or set AZURE_STORAGE_CONNECTION_STRING"
                    )
                from azure.core.credentials import AccessToken

                class _StaticTokenCredential:
                    """Wrap a pre-fetched token so the SDK can use it."""
                    def __init__(self, access_token: str):
                        self._token = access_token

                    def get_token(self, *scopes, **kwargs):
                        return AccessToken(self._token, 0)

                credential = _StaticTokenCredential(token)
                account_url = f"https://{self._config.storage_account}.blob.core.windows.net"
                self._client = BlobServiceClient(account_url=account_url, credential=credential)
        return self._client

    @property
    def container_client(self):
        return self.client.get_container_client(self._config.container)

    def list_blobs(self, entity: str | None = None) -> LayerResult:
        prefix = f"{entity}/" if entity else self._config.blob_prefix
        try:
            blobs = []
            for blob in self.container_client.list_blobs(name_starts_with=prefix):
                blobs.append({
                    "name": blob.name,
                    "size_bytes": blob.size,
                    "last_modified": str(blob.last_modified),
                    "content_type": blob.content_settings.content_type if blob.content_settings else "",
                })
            if not blobs:
                return LayerResult(
                    layer="Azure Blob Storage",
                    status=LayerStatus.NOT_FOUND,
                    message=f"No blobs found at {self._config.container}/{prefix}",
                )
            return LayerResult(
                layer="Azure Blob Storage",
                status=LayerStatus.OK,
                data={"blobs": blobs, "count": len(blobs)},
            )
        except Exception as e:
            if "authentication" in str(e).lower() or "credential" in str(e).lower():
                return LayerResult(
                    layer="Azure Blob Storage",
                    status=LayerStatus.SKIPPED,
                    message="Azure credentials not configured — run: az login",
                )
            return LayerResult(
                layer="Azure Blob Storage",
                status=LayerStatus.ERROR,
                message=str(e),
            )

    def check_blob_exists(self, blob_name: str) -> LayerResult:
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            props = blob_client.get_blob_properties()
            return LayerResult(
                layer="Azure Blob Storage",
                status=LayerStatus.OK,
                data={
                    "name": blob_name,
                    "size_bytes": props.size,
                    "last_modified": str(props.last_modified),
                    "container": self._config.container,
                },
            )
        except Exception as e:
            if "BlobNotFound" in str(e) or "404" in str(e):
                return LayerResult(
                    layer="Azure Blob Storage",
                    status=LayerStatus.NOT_FOUND,
                    message=f"{self._config.container}/{blob_name}",
                )
            if "authentication" in str(e).lower() or "credential" in str(e).lower():
                return LayerResult(
                    layer="Azure Blob Storage",
                    status=LayerStatus.SKIPPED,
                    message="Azure credentials not configured — run: az login",
                )
            return LayerResult(
                layer="Azure Blob Storage",
                status=LayerStatus.ERROR,
                message=str(e),
            )

    def upload_blob(self, local_path: str, blob_name: str | None = None) -> LayerResult:
        path = Path(local_path)
        if not path.exists():
            return LayerResult(
                layer="Azure Blob Upload",
                status=LayerStatus.ERROR,
                message=f"Local file not found: {local_path}",
            )

        if blob_name is None:
            blob_name = f"{self._config.entity.value}/{path.name}"

        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            with open(path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)

            return LayerResult(
                layer="Azure Blob Upload",
                status=LayerStatus.OK,
                message=f"Uploaded to {self._config.container}/{blob_name}",
                data={
                    "local_path": str(path),
                    "blob_name": blob_name,
                    "size_bytes": path.stat().st_size,
                    "container": self._config.container,
                },
            )
        except Exception as e:
            if "authentication" in str(e).lower() or "credential" in str(e).lower():
                return LayerResult(
                    layer="Azure Blob Upload",
                    status=LayerStatus.SKIPPED,
                    message="Azure credentials not configured — run: az login",
                )
            return LayerResult(
                layer="Azure Blob Upload",
                status=LayerStatus.ERROR,
                message=str(e),
            )
