from __future__ import annotations

import contextlib
import os
from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

_requests_instrumentor: Any = None
_urllib3_instrumentor: Any = None
try:
    from opentelemetry.instrumentation.requests import RequestsInstrumentor as _ReqInst
    from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor as _UrlInst
except ImportError:  # pragma: no cover
    pass
else:
    _requests_instrumentor = _ReqInst
    _urllib3_instrumentor = _UrlInst

_CONFIGURED: list[bool] = [False]


def _parse_otlp_headers(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    out: dict[str, str] = {}
    # OTEL_EXPORTER_OTLP_HEADERS commonly looks like: "k1=v1,k2=v2"
    for segment in raw.split(","):
        part = segment.strip()
        if not part or "=" not in part:
            continue
        k, v = part.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def configure_tracing(service_name: str) -> None:
    """
    Configure a process-wide tracer provider.

    Export behavior:
    - If OTEL_EXPORTER_OTLP_ENDPOINT is set: export spans via OTLP/HTTP.
    - Otherwise: export to console (dev-friendly).
    """
    if _CONFIGURED[0]:
        return

    resource_attrs = {"service.name": service_name}
    sha = (os.getenv("GITHUB_SHA") or os.getenv("GIT_SHA") or "").strip()
    if sha:
        resource_attrs["git.sha"] = sha
    suite = (os.getenv("OTEL_TEST_SUITE") or "").strip()
    if suite:
        resource_attrs["test.suite"] = suite

    resource = Resource.create(resource_attrs)
    provider = TracerProvider(resource=resource)

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        headers = _parse_otlp_headers(os.getenv("OTEL_EXPORTER_OTLP_HEADERS"))
        provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(endpoint=otlp_endpoint, headers=headers or None)
            )
        )
    else:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)

    # Auto-instrumentation (best-effort). This makes outbound HTTP calls show up
    # as child spans under the per-test parent span.
    if _requests_instrumentor is not None:
        with contextlib.suppress(Exception):
            _requests_instrumentor().instrument()

    if _urllib3_instrumentor is not None:
        with contextlib.suppress(Exception):
            _urllib3_instrumentor().instrument()

    _CONFIGURED[0] = True


def get_tracer(name: str = "qa-tests"):
    return trace.get_tracer(name)


def current_trace_id() -> str | None:
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if not ctx or not ctx.is_valid:
        return None
    return format(ctx.trace_id, "032x")
