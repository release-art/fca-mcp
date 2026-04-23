"""Unit tests for Azure Table Storage chunking helpers."""

from __future__ import annotations

from fca_mcp.azure.table_key_value import (
    _CHUNK_CHARS,
    _VALUE_CHUNK_COUNT,
    _VALUE_CHUNK_PREFIX,
    AzureTableStore,
)


def test_split_empty():
    assert AzureTableStore._split_value("") == {_VALUE_CHUNK_COUNT: 0}


def test_split_single_chunk():
    payload = AzureTableStore._split_value("hello")
    assert payload == {_VALUE_CHUNK_COUNT: 1, f"{_VALUE_CHUNK_PREFIX}0": "hello"}


def test_split_multi_chunk():
    value = "a" * (_CHUNK_CHARS * 2 + 10)
    payload = AzureTableStore._split_value(value)
    assert payload[_VALUE_CHUNK_COUNT] == 3
    assert payload[f"{_VALUE_CHUNK_PREFIX}0"] == "a" * _CHUNK_CHARS
    assert payload[f"{_VALUE_CHUNK_PREFIX}1"] == "a" * _CHUNK_CHARS
    assert payload[f"{_VALUE_CHUNK_PREFIX}2"] == "a" * 10


def test_split_join_roundtrip():
    value = "x" * (_CHUNK_CHARS + 1) + "y" * (_CHUNK_CHARS - 5)
    payload = AzureTableStore._split_value(value)
    entity = {"PartitionKey": "p", "RowKey": "r", **payload}
    assert AzureTableStore._join_value(entity) == value


def test_join_missing_count():
    assert AzureTableStore._join_value({}) is None


def test_join_zero_count():
    assert AzureTableStore._join_value({_VALUE_CHUNK_COUNT: 0}) is None


def test_join_non_int_count():
    assert AzureTableStore._join_value({_VALUE_CHUNK_COUNT: "2"}) is None


def test_join_missing_chunk():
    entity = {_VALUE_CHUNK_COUNT: 2, f"{_VALUE_CHUNK_PREFIX}0": "a"}
    assert AzureTableStore._join_value(entity) is None


def test_join_non_string_chunk():
    entity = {_VALUE_CHUNK_COUNT: 1, f"{_VALUE_CHUNK_PREFIX}0": 123}
    assert AzureTableStore._join_value(entity) is None
