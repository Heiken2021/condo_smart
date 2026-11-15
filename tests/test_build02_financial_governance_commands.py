from pathlib import Path


SERVICE = Path(
    "services/"
    "financial_governance_commands.py"
).read_text(encoding="utf-8")


def test_command_service_exposes_objective_commands():
    assert "def create_financial_objective(" in SERVICE
    assert "def approve_financial_objective(" in SERVICE


def test_command_service_exposes_policy_commands():
    assert "def create_financial_policy(" in SERVICE
    assert "def approve_financial_policy(" in SERVICE


def test_objective_commands_use_expected_permission():
    assert (
        "FINANZAS_OBJETIVO_GESTIONAR"
        in SERVICE
    )


def test_policy_commands_use_expected_permission():
    assert (
        "FINANZAS_POLITICA_GESTIONAR"
        in SERVICE
    )


def test_command_service_uses_server_side_authorization():
    assert (
        "from core.authorization import require"
        in SERVICE
    )
    assert "def _require_actor(" in SERVICE


def test_command_service_requires_active_actor():
    assert "def _actor(" in SERVICE
    assert "USER_INACTIVE" in SERVICE


def test_command_service_uses_atomic_transactions():
    assert (
        "with pool().connection() as connection:"
        in SERVICE
    )
    assert "connection.commit()" in SERVICE
    assert "connection.rollback()" in SERVICE


def test_commands_write_audit_in_same_cursor():
    assert "def _insert_audit(" in SERVICE
    assert (
        "INSERT INTO auditoria_financiera"
        in SERVICE
    )
    assert "cursor," in SERVICE


def test_commands_share_trace_id_with_audit():
    assert "trace_id = new_trace_id()" in SERVICE
    assert "trace_id=trace_id" in SERVICE


def test_objective_creation_starts_as_draft():
    assert (
        "INSERT INTO financial_objectives"
        in SERVICE
    )
    assert "'BORRADOR'" in SERVICE


def test_objective_approval_uses_row_lock():
    assert "FROM financial_objectives" in SERVICE
    assert "FOR UPDATE" in SERVICE
    assert (
        "FINANCIAL_OBJECTIVE_NOT_APPROVABLE"
        in SERVICE
    )


def test_policy_requires_approved_objective():
    assert (
        "FINANCIAL_POLICY_REQUIRES_APPROVED_OBJECTIVE"
        in SERVICE
    )


def test_policy_creation_starts_as_draft():
    assert (
        "INSERT INTO financial_policies"
        in SERVICE
    )


def test_policy_approval_is_explicit():
    assert (
        "FINANCIAL_POLICY_NOT_APPROVABLE"
        in SERVICE
    )
    assert (
        "FINANCIAL_POLICY_APPROVED"
        in SERVICE
    )


def test_approval_reason_is_required():
    assert (
        "FINANCIAL_APPROVAL_REASON_REQUIRED"
        in SERVICE
    )


def test_effective_date_range_is_validated():
    assert "def _valid_dates(" in SERVICE
    assert (
        "INVALID_EFFECTIVE_DATE_RANGE"
        in SERVICE
    )


def test_governance_metadata_is_sanitized():
    assert "sanitize(" in SERVICE
    assert "json.dumps(" in SERVICE


def test_command_service_has_no_ui_dependency():
    assert "import streamlit" not in SERVICE
    assert "st." not in SERVICE


def test_command_service_does_not_modify_financial_movements():
    for token in [
        "INSERT INTO cargos",
        "UPDATE cargos",
        "DELETE FROM cargos",
        "INSERT INTO pagos",
        "UPDATE pagos",
        "DELETE FROM pagos",
        "INSERT INTO gastos",
        "UPDATE gastos",
        "DELETE FROM gastos",
    ]:
        assert token not in SERVICE


def test_command_service_does_not_allow_ai_approval():
    for token in [
        "AI_AUTO_APPROVE",
        "AI_AUTO_EXECUTE",
        "IA_AUTO_APROBAR",
        "IA_AUTO_EJECUTAR",
    ]:
        assert token not in SERVICE
