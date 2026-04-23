"""Tests for logging configuration."""

from __future__ import annotations

import importlib

import fca_mcp.logging as logging_mod


def test_get_config_json_default():
    cfg = logging_mod.get_config()
    assert cfg["version"] == 1
    assert cfg["disable_existing_loggers"] is False
    assert "console" in cfg["handlers"]


def test_get_config_human_logs(monkeypatch):
    monkeypatch.setenv("HUMAN_LOGS", "true")
    reloaded = importlib.reload(logging_mod)
    try:
        cfg = reloaded.get_config()
        assert "%(asctime)s" in cfg["formatters"]["default"]["format"]
    finally:
        monkeypatch.delenv("HUMAN_LOGS", raising=False)
        importlib.reload(logging_mod)


def test_configure_runs():
    logging_mod.configure()
