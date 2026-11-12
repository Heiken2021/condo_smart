from pathlib import Path


S = Path(
    "services/audit_service.py"
).read_text(encoding="utf-8")

V = Path(
    "views/auditoria.py"
).read_text(encoding="utf-8")


def test_system_severity_engine_exists():
    assert "def system_severity(" in S
    assert "SYSTEM_CRITICAL_TOKENS" in S
    assert "SYSTEM_WARNING_TOKENS" in S


def test_financial_severity_engine_exists():
    assert "def financial_severity(" in S
    assert "FINANCIAL_CRITICAL_TOKENS" in S
    assert "FINANCIAL_WARNING_TOKENS" in S


def test_overall_severity_uses_traffic_light_priority():
    assert "def overall_severity(" in S
    assert '"CRITICO" in severities' in S
    assert '"ATENCION" in severities' in S


def test_system_dashboard_has_executive_metrics():
    for label in [
        "Estado General Del Sistema",
        "Eventos",
        "Correctos",
        "Atención",
        "Críticos",
    ]:
        assert label in V


def test_financial_dashboard_has_executive_metrics():
    for label in [
        "Estado De Auditoría Financiera",
        "Movimientos",
        "Importe Auditado",
        "Revisión",
        "Críticos",
    ]:
        assert label in V


def test_audit_dashboard_has_visual_analysis():
    assert "st.line_chart(" in V
    assert "st.bar_chart(" in V
    assert "Distribución Por Severidad" in V


def test_system_dashboard_has_incident_panel():
    assert "Incidentes Que Requieren Atención" in V


def test_financial_dashboard_has_review_panel():
    assert "Operaciones Que Requieren Revisión" in V


def test_existing_detail_tables_are_preserved():
    assert "Explorador De Eventos" in V
    assert "Explorador De Movimientos" in V
    assert "st.dataframe(" in V


def test_system_filters_include_severity():
    assert "audit_system_severity_filter" in V


def test_financial_filters_include_severity():
    assert "audit_fin_severity_filter" in V


def test_financial_empty_state_is_supported():
    assert "El ledger financiero está activo" in V


def test_incident_rules_include_access_denials():
    assert "ACCESS_DENIED" in S
    assert "PERMISSION_DENIED" in S


def test_financial_rules_include_reversals_and_cancellations():
    assert '"REVERS"' in S
    assert '"CANCEL"' in S
