from __future__ import annotations

import contextlib
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

try:
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
except ImportError:  # pragma: no cover
    RequestsInstrumentor = None
    URLLib3Instrumentor = None

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

    resource = Resource.create({"service.name": service_name})
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
    if RequestsInstrumentor is not None:
        with contextlib.suppress(Exception):
            RequestsInstrumentor().instrument()

    if URLLib3Instrumentor is not None:
        with contextlib.suppress(Exception):
            URLLib3Instrumentor().instrument()

    _CONFIGURED[0] = True


def get_tracer(name: str = "qa-tests"):
    return trace.get_tracer(name)


def current_trace_id() -> str | None:
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if not ctx or not ctx.is_valid:
        return None
    return format(ctx.trace_id, "032x")
