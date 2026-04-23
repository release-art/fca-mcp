"""Tests for the typer CLI."""

from __future__ import annotations

from typer.testing import CliRunner

import fca_mcp.cli as cli_mod


def test_serve_invokes_uvicorn(mocker):
    uv_run = mocker.patch("fca_mcp.cli.uvicorn.run")
    mocker.patch("fca_mcp.logging.configure")
    mocker.patch("fca_mcp.telemetry.configure")

    runner = CliRunner()
    result = runner.invoke(cli_mod.app, ["serve", "--host", "127.0.0.1", "--port", "1234"])
    assert result.exit_code == 0, result.output
    uv_run.assert_called_once()
    args, kwargs = uv_run.call_args
    assert args[0] == "fca_mcp.uvcorn_app:get_http_app"
    assert kwargs["host"] == "127.0.0.1"
    assert kwargs["port"] == 1234
    assert kwargs["factory"] is True


def test_stdio_invokes_run(mocker):
    mock_mcp = mocker.MagicMock()
    mocker.patch("fca_mcp.server.get_server", return_value=mock_mcp)
    mocker.patch("fca_mcp.logging.configure")
    mocker.patch("fca_mcp.telemetry.configure")

    runner = CliRunner()
    result = runner.invoke(cli_mod.app, ["stdio"])
    assert result.exit_code == 0, result.output
    mock_mcp.run.assert_called_once()
