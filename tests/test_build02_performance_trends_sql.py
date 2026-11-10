from pathlib import Path

SERVICE = Path("services/performance.py").read_text(encoding="utf-8")
VIEW = Path("views/performance_dashboard.py").read_text(encoding="utf-8")


def test_trends_uses_unambiguous_date_alias():
    assert "DATE(recorded_at) AS event_day" in SERVICE
    assert "ORDER BY event_day,module" in SERVICE
    assert "DATE(recorded_at) day" not in SERVICE


def test_performance_chart_uses_event_day():
    assert "x='event_day'" in VIEW
    assert "pivot='day'" not in VIEW
