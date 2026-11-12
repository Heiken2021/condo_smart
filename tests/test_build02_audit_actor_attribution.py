from pathlib import Path


V = Path(
    "views/auditoria.py"
).read_text(encoding="utf-8")


def attribution_block():
    return V.split(
        "def _incident_attribution(",
        1,
    )[1].split(
        "def _system_dashboard(",
        1,
    )[0]


def test_incident_attribution_component_exists():
    assert "def _incident_attribution(" in V


def test_principal_trigger_card_exists():
    block = attribution_block()

    assert "Principal Detonante" in block
    assert "Usuario" in block
    assert "Entidad afectada:" in block
    assert "Registro:" in block
    assert "Fecha" in block


def test_users_who_generate_incidents_chart_exists():
    block = attribution_block()

    assert "Usuarios Que Generan Incidentes" in block
    assert "horizontal=True" in block


def test_triggering_actions_chart_exists():
    block = attribution_block()

    assert "Acciones Que Generan Incidentes" in block
    assert "Operaciones Que Generan Alertas" in block


def test_user_action_matrix_exists():
    block = attribution_block()

    assert "Matriz Usuario × Detonante" in block
    assert '"Usuario"' in block
    assert "action_column" in block
    assert '"Severidad"' in block


def test_critical_and_attention_are_separated():
    block = attribution_block()

    assert '"Críticos"' in block
    assert '"Atención"' in block
    assert '"CRITICO"' in block
    assert '"ATENCION"' in block


def test_impact_prioritizes_critical_events():
    block = attribution_block()

    assert 'user_summary["Críticos"] * 3' in block
    assert 'action_summary["Críticos"] * 3' in block


def test_incident_drilldown_exists():
    block = attribution_block()

    assert "Investigar Eventos Ponderantes" in block
    assert "Investigar Movimientos Ponderantes" in block
    assert "Usuario Detonante" in block


def test_drilldown_filters_by_user():
    block = attribution_block()

    assert "selected_user" in block
    assert 'key=f"{mode}_incident_user"' in block


def test_drilldown_filters_by_action():
    block = attribution_block()

    assert "selected_action" in block
    assert 'key=f"{mode}_incident_action"' in block


def test_drilldown_filters_by_severity():
    block = attribution_block()

    assert "selected_level" in block
    assert "🔴 Crítico" in block
    assert "🟡 Atención" in block


def test_system_dashboard_uses_attribution():
    system = V.split(
        "def _system_dashboard(",
        1,
    )[1].split(
        "def _financial_dashboard(",
        1,
    )[0]

    assert "_incident_attribution(" in system
    assert 'mode="system"' in system


def test_financial_dashboard_uses_attribution():
    financial = V.split(
        "def _financial_dashboard(",
        1,
    )[1].split(
        "def _system_tab(",
        1,
    )[0]

    assert "_incident_attribution(" in financial
    assert 'mode="financial"' in financial


def test_financial_attribution_supports_amount():
    block = attribution_block()

    assert '"Monto MXN"' in block


def test_no_database_migration_is_required():
    assert "INSERT INTO" not in V
    assert "UPDATE auditoria" not in V
    assert "DELETE FROM auditoria" not in V
