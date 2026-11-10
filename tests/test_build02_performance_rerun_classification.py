import pytest

import services.performance as performance


class RerunException(Exception):
    pass


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
            "duration_ms": 40.0,
            "count": 3,
            "slowest_ms": 20.0,
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


def test_rerun_is_recorded_separately_and_propagates(
    monkeypatch,
):
    events = _install_fakes(monkeypatch)

    with pytest.raises(RerunException):
        with performance.measure(
            "inmuebles",
            "module_render",
            101,
            {"module_path": "views.inmuebles"},
        ):
            raise RerunException()

    assert len(events) == 1

    event = events[0]

    assert event["status"] == "RERUN"
    assert (
        event["metadata"]["exception_type"]
        == "RerunException"
    )
    assert event["module"] == "inmuebles"
    assert event["operation"] == "module_render"


def test_real_exception_remains_error(monkeypatch):
    events = _install_fakes(monkeypatch)

    with pytest.raises(TypeError):
        with performance.measure(
            "inmuebles",
            "module_render",
        ):
            raise TypeError("simulado")

    assert len(events) == 1
    assert events[0]["status"] == "ERROR"
    assert (
        events[0]["metadata"]["exception_type"]
        == "TypeError"
    )


def test_normal_execution_remains_ok(monkeypatch):
    events = _install_fakes(monkeypatch)

    with performance.measure(
        "inmuebles",
        "module_render",
    ):
        result = 2 + 2

    assert result == 4
    assert len(events) == 1
    assert events[0]["status"] == "OK"
    assert (
        "exception_type"
        not in events[0]["metadata"]
    )


def test_health_queries_count_only_real_errors():
    source = open(
        "services/performance.py",
        encoding="utf-8",
    ).read()

    assert "status='ERROR'" in source
    assert "status='RERUN'" in source
    assert (
        "exc_type.__name__ == 'RerunException'"
        in source
    )

    # RERUN se registra como telemetría, pero las métricas
    # de error contabilizan exclusivamente status='ERROR'.
    assert "COUNT(*) FILTER(WHERE status='ERROR')" in source
    assert "COUNT(*) FILTER(WHERE status='RERUN')" not in source
