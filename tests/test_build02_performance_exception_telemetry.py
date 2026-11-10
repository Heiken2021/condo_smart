import pytest

import services.performance as performance


def _install_fakes(monkeypatch):
    events = []

    monkeypatch.setattr(
        performance,
        "reset_query_stats",
        lambda: None,
    )

    monkeypatch.setattr(
        performance,
        "query_stats",
        lambda: {
            "duration_ms": 25.0,
            "count": 2,
            "slowest_ms": 15.0,
        },
    )

    def fake_record_event(
        module,
        operation,
        duration_ms,
        status="OK",
        property_id=None,
        metadata=None,
        sql_duration_ms=0,
        query_count=0,
        slowest_query_ms=0,
    ):
        events.append(
            {
                "module": module,
                "operation": operation,
                "duration_ms": duration_ms,
                "status": status,
                "property_id": property_id,
                "metadata": metadata or {},
                "sql_duration_ms": sql_duration_ms,
                "query_count": query_count,
                "slowest_query_ms": slowest_query_ms,
            }
        )

    monkeypatch.setattr(
        performance,
        "record_event",
        fake_record_event,
    )

    return events


def test_measure_records_exception_type_and_propagates(
    monkeypatch,
):
    events = _install_fakes(monkeypatch)

    with pytest.raises(KeyError):
        with performance.measure(
            "inmuebles",
            "module_render",
            101,
            {"module_path": "views.inmuebles"},
        ):
            raise KeyError("contenido sensible simulado")

    assert len(events) == 1

    event = events[0]

    assert event["module"] == "inmuebles"
    assert event["operation"] == "module_render"
    assert event["status"] == "ERROR"
    assert event["property_id"] == 101

    metadata = event["metadata"]

    assert metadata["module_path"] == "views.inmuebles"
    assert metadata["exception_type"] == "KeyError"
    assert "python_render_ms" in metadata
    assert "sql_share_pct" in metadata

    serialized = repr(metadata)

    assert "contenido sensible simulado" not in serialized
    assert "exception_message" not in metadata
    assert "traceback" not in metadata


def test_measure_records_ok_without_exception_fields(
    monkeypatch,
):
    events = _install_fakes(monkeypatch)

    with performance.measure(
        "espacios",
        "module_render",
        202,
        {"module_path": "views.espacios"},
    ):
        value = 2 + 2

    assert value == 4
    assert len(events) == 1

    event = events[0]

    assert event["status"] == "OK"
    assert event["metadata"]["module_path"] == "views.espacios"
    assert "exception_type" not in event["metadata"]
    assert "exception_message" not in event["metadata"]
    assert "traceback" not in event["metadata"]


def test_measure_keeps_sql_diagnostics_on_error(
    monkeypatch,
):
    events = _install_fakes(monkeypatch)

    with pytest.raises(ValueError):
        with performance.measure(
            "configuracion",
            "module_render",
        ):
            raise ValueError("simulado")

    event = events[0]

    assert event["status"] == "ERROR"
    assert event["metadata"]["exception_type"] == "ValueError"
    assert event["sql_duration_ms"] == 25.0
    assert event["query_count"] == 2
    assert event["slowest_query_ms"] == 15.0
