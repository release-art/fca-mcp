"""Tests for OpenTelemetry configuration."""

from __future__ import annotations

import fca_mcp.telemetry as telemetry


def test_noop_when_endpoint_unset(monkeypatch):
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    # Must not raise or try to import OTel libraries.
    telemetry.configure()


def test_configures_when_endpoint_set(monkeypatch, mocker):
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

    set_tracer_provider = mocker.patch("opentelemetry.trace.set_tracer_provider")
    mocker.patch("opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter")
    starlette_instr = mocker.patch("opentelemetry.instrumentation.starlette.StarletteInstrumentor")
    httpx_instr = mocker.patch("opentelemetry.instrumentation.httpx.HTTPXClientInstrumentor")
    logging_instr = mocker.patch("opentelemetry.instrumentation.logging.LoggingInstrumentor")

    telemetry.configure()

    set_tracer_provider.assert_called_once()
    starlette_instr.return_value.instrument.assert_called_once()
    httpx_instr.return_value.instrument.assert_called_once()
    logging_instr.return_value.instrument.assert_called_once_with(set_logging_format=True)
