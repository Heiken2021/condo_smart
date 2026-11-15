from pathlib import Path


SERVICE = Path(
    "services/financial_governance_commands.py"
).read_text(encoding="utf-8")


def test_service_exposes_fee_commands():
    assert "def create_space_fee_version(" in SERVICE
    assert "def approve_space_fee_version(" in SERVICE


def test_fee_creation_uses_expected_permission():
    assert "FINANZAS_CUOTA_GESTIONAR" in SERVICE


def test_fee_creation_validates_space():
    assert "FROM espacios" in SERVICE
    assert "FINANCIAL_FEE_SPACE_NOT_FOUND" in SERVICE
    assert "FINANCIAL_FEE_SPACE_INACTIVE" in SERVICE


def test_fee_creation_validates_amount():
    assert "INVALID_FINANCIAL_FEE_AMOUNT" in SERVICE


def test_fee_creation_supports_rule_provenance():
    assert "rule_version_id" in SERVICE
    assert (
        "FINANCIAL_FEE_REQUIRES_APPROVED_RULE_VERSION"
        in SERVICE
    )
    assert (
        "FINANCIAL_FEE_RULE_SCOPE_MISMATCH"
        in SERVICE
    )


def test_fee_creation_starts_as_draft():
    assert "INSERT INTO space_fee_history" in SERVICE
    assert "'BORRADOR'" in SERVICE


def test_fee_approval_is_explicit_and_locked():
    assert "def approve_space_fee_version(" in SERVICE
    assert "FROM space_fee_history" in SERVICE
    assert "FOR UPDATE" in SERVICE
    assert (
        "FINANCIAL_FEE_VERSION_NOT_APPROVABLE"
        in SERVICE
    )


def test_service_exposes_exception_commands():
    assert "def request_financial_exception(" in SERVICE
    assert "def resolve_financial_exception(" in SERVICE


def test_exception_request_uses_permission():
    assert "FINANZAS_EXCEPCION_SOLICITAR" in SERVICE


def test_exception_resolution_uses_permission():
    assert "FINANZAS_EXCEPCION_RESOLVER" in SERVICE


def test_exception_requires_approved_rule():
    assert (
        "FINANCIAL_EXCEPTION_REQUIRES_APPROVED_RULE"
        in SERVICE
    )


def test_exception_respects_rule_capability():
    assert (
        "FINANCIAL_RULE_EXCEPTION_NOT_ALLOWED"
        in SERVICE
    )


def test_exception_starts_pending():
    assert (
        "INSERT INTO financial_rule_exceptions"
        in SERVICE
    )
    assert "'PENDIENTE'" in SERVICE


def test_exception_resolution_only_accepts_two_decisions():
    assert '"APROBADA"' in SERVICE
    assert '"RECHAZADA"' in SERVICE
    assert (
        "INVALID_FINANCIAL_EXCEPTION_DECISION"
        in SERVICE
    )


def test_exception_resolution_requires_detail():
    assert (
        "FINANCIAL_EXCEPTION_DECISION_DETAIL_REQUIRED"
        in SERVICE
    )


def test_exception_resolution_uses_row_lock():
    assert "FINANCIAL_EXCEPTION_NOT_RESOLVABLE" in SERVICE
    assert SERVICE.count("FOR UPDATE") >= 4


def test_fee_and_exception_commands_are_audited():
    for token in [
        "FINANCIAL_SPACE_FEE_CREATED",
        "FINANCIAL_SPACE_FEE_APPROVED",
        "FINANCIAL_EXCEPTION_REQUESTED",
        "FINANCIAL_EXCEPTION_RESOLVED",
    ]:
        assert token in SERVICE


def test_fee_and_exception_commands_are_atomic():
    assert "connection.commit()" in SERVICE
    assert "connection.rollback()" in SERVICE


def test_fee_and_exception_commands_return_traceability():
    assert '["audit_event_id"]' in SERVICE
    assert '["trace_id"]' in SERVICE


def test_fee_exception_commands_do_not_modify_movements():
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


def test_fee_exception_commands_have_no_ui_dependency():
    assert "import streamlit" not in SERVICE
    assert "st." not in SERVICE
