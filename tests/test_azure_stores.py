"""Tests for AzureTableStore and AzureBlobStore using mocked Azure clients."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.storage.blob.aio import BlobServiceClient

from fca_mcp.azure.blob_key_value import (
    AzureBlobStore,
    BlobCollectionSanitizationStrategy,
    BlobKeySanitizationStrategy,
)
from fca_mcp.azure.table_key_value import AzureTableStore


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _make_table_service(table_client: AsyncMock) -> MagicMock:
    svc = MagicMock()
    svc.get_table_client = MagicMock(return_value=table_client)
    svc.create_table = AsyncMock()
    return svc


def _make_table_store(table_client: AsyncMock) -> AzureTableStore:
    svc = _make_table_service(table_client)
    store = AzureTableStore(client=svc, table_name="t")
    store._table_client = table_client
    return store


@pytest.mark.anyio
async def test_table_setup_creates_table():
    tc = AsyncMock()
    svc = _make_table_service(tc)
    store = AzureTableStore(client=svc, table_name="t")
    await store._setup()
    svc.create_table.assert_awaited_once_with("t")


@pytest.mark.anyio
async def test_table_setup_table_already_exists_ok():
    tc = AsyncMock()
    svc = _make_table_service(tc)
    err = HttpResponseError()
    err.error_code = "TableAlreadyExists"  # type: ignore[attr-defined]
    svc.create_table = AsyncMock(side_effect=err)
    store = AzureTableStore(client=svc, table_name="t")
    await store._setup()


@pytest.mark.anyio
async def test_table_setup_other_error_reraises():
    tc = AsyncMock()
    svc = _make_table_service(tc)
    err = HttpResponseError()
    err.error_code = "SomethingElse"  # type: ignore[attr-defined]
    svc.create_table = AsyncMock(side_effect=err)
    store = AzureTableStore(client=svc, table_name="t")
    with pytest.raises(HttpResponseError):
        await store._setup()


@pytest.mark.anyio
async def test_table_connected_client_raises_before_setup():
    svc = _make_table_service(AsyncMock())
    store = AzureTableStore(client=svc, table_name="t")
    with pytest.raises(RuntimeError, match="Store not initialized"):
        _ = store._connected_client


@pytest.mark.anyio
async def test_table_get_missing_returns_none():
    tc = AsyncMock()
    tc.get_entity = AsyncMock(side_effect=ResourceNotFoundError())
    store = _make_table_store(tc)
    assert await store._get_managed_entry(collection="c", key="k") is None


@pytest.mark.anyio
async def test_table_get_empty_payload_returns_none():
    tc = AsyncMock()
    tc.get_entity = AsyncMock(return_value={"RowKey": "x"})
    store = _make_table_store(tc)
    assert await store._get_managed_entry(collection="c", key="k") is None


@pytest.mark.anyio
async def test_table_put_then_get_roundtrip():
    tc = AsyncMock()

    captured: dict = {}

    async def upsert(entity, mode):
        captured.update(entity)

    async def get_entity(partition_key, row_key):
        return dict(captured)

    tc.upsert_entity = AsyncMock(side_effect=upsert)
    tc.get_entity = AsyncMock(side_effect=get_entity)
    tc.delete_entity = AsyncMock()
    store = _make_table_store(tc)

    await store.put(key="k", value={"hello": "world"}, collection="c")
    result = await store.get(key="k", collection="c")
    assert result == {"hello": "world"}


@pytest.mark.anyio
async def test_table_delete_hit_and_miss():
    tc = AsyncMock()
    tc.delete_entity = AsyncMock()
    store = _make_table_store(tc)
    assert await store._delete_managed_entry(collection="c", key="k") is True

    tc.delete_entity = AsyncMock(side_effect=ResourceNotFoundError())
    assert await store._delete_managed_entry(collection="c", key="k") is False


@pytest.mark.anyio
async def test_table_delete_entity_quiet_swallows_missing():
    tc = AsyncMock()
    tc.delete_entity = AsyncMock(side_effect=ResourceNotFoundError())
    store = _make_table_store(tc)
    await store._delete_entity_quiet("p", "r")  # does not raise


@pytest.mark.anyio
async def test_table_collection_keys():
    tc = AsyncMock()

    async def gen():
        for k in ("a", "b", "c"):
            yield {"RowKey": k}

    tc.query_entities = MagicMock(return_value=gen())
    store = _make_table_store(tc)
    keys = await store._get_collection_keys(collection="x", limit=2)
    assert len(keys) == 2


@pytest.mark.anyio
async def test_table_close_is_noop():
    tc = AsyncMock()
    store = _make_table_store(tc)
    await store._close()


def test_blob_sanitization_strategy_validate_noop():
    BlobKeySanitizationStrategy().validate("anything")
    BlobCollectionSanitizationStrategy().validate("anything")


def test_blob_sanitization_strategy_sanitize_short_passthrough():
    strat = BlobKeySanitizationStrategy(max_length=100)
    assert strat.sanitize("short") == "short"


def _make_blob_service() -> MagicMock:
    svc = MagicMock(spec=BlobServiceClient)
    container = AsyncMock()
    svc.get_container_client = MagicMock(return_value=container)
    svc.create_container = AsyncMock()
    return svc


@pytest.mark.anyio
async def test_blob_setup_creates_container():
    svc = _make_blob_service()
    store = AzureBlobStore(client=svc, container_name="c")
    await store._setup()
    svc.create_container.assert_awaited_once()


@pytest.mark.anyio
async def test_blob_setup_container_exists_ok():
    svc = _make_blob_service()
    svc.create_container = AsyncMock(side_effect=ResourceExistsError())
    store = AzureBlobStore(client=svc, container_name="c")
    await store._setup()  # no raise


@pytest.mark.anyio
async def test_blob_delete_hit_and_miss():
    svc = _make_blob_service()
    container = svc.get_container_client.return_value
    container.delete_blob = AsyncMock()
    store = AzureBlobStore(client=svc, container_name="c")
    assert await store._delete_managed_entry(collection="col", key="k") is True

    container.delete_blob = AsyncMock(side_effect=ResourceNotFoundError())
    assert await store._delete_managed_entry(collection="col", key="k") is False


@pytest.mark.anyio
async def test_blob_delete_quiet_swallows_missing():
    svc = _make_blob_service()
    container = svc.get_container_client.return_value
    container.delete_blob = AsyncMock(side_effect=ResourceNotFoundError())
    store = AzureBlobStore(client=svc, container_name="c")
    await store._delete_blob_quiet("some/blob")


@pytest.mark.anyio
async def test_blob_get_missing_returns_none():
    svc = _make_blob_service()
    container = svc.get_container_client.return_value
    container.download_blob = AsyncMock(side_effect=ResourceNotFoundError())
    store = AzureBlobStore(client=svc, container_name="c")
    assert await store._get_managed_entry(collection="col", key="k") is None


@pytest.mark.anyio
async def test_blob_put_and_get_roundtrip():
    svc = _make_blob_service()
    container = svc.get_container_client.return_value
    stored: dict[str, bytes] = {}

    async def upload_blob(*, name, data, metadata, overwrite):
        stored[name] = data

    async def download_blob(blob_name):
        dl = AsyncMock()
        dl.readall = AsyncMock(return_value=stored[blob_name])
        return dl

    container.upload_blob = AsyncMock(side_effect=upload_blob)
    container.download_blob = AsyncMock(side_effect=download_blob)

    store = AzureBlobStore(client=svc, container_name="c", default_collection="col")
    await store.put(key="k", value={"v": 1})
    assert await store.get(key="k") == {"v": 1}


@pytest.mark.anyio
async def test_blob_collection_keys():
    svc = _make_blob_service()
    container = svc.get_container_client.return_value

    class _Blob:
        def __init__(self, name: str) -> None:
            self.name = name

    async def gen(name_starts_with):
        for k in ("a", "b", "c"):
            yield _Blob(f"{name_starts_with}{k}")

    container.list_blobs = MagicMock(side_effect=lambda name_starts_with: gen(name_starts_with))
    store = AzureBlobStore(client=svc, container_name="c")
    keys = await store._get_collection_keys(collection="col", limit=2)
    assert len(keys) == 2


def test_blob_connected_client_raises_without_client():
    svc = _make_blob_service()
    store = AzureBlobStore(client=svc, container_name="c")
    store._client = None
    with pytest.raises(ValueError, match="Client not connected"):
        _ = store._connected_client


def test_blob_requires_blob_service_client():
    with pytest.raises(AssertionError):
        AzureBlobStore(client="not-a-client", container_name="c")  # type: ignore[arg-type]
