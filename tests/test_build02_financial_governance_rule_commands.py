from pathlib import Path


SERVICE = Path(
    "services/financial_governance_commands.py"
).read_text(encoding="utf-8")


def test_service_exposes_rule_creation():
    assert "def create_financial_rule(" in SERVICE
    assert "INSERT INTO financial_rules" in SERVICE


def test_rule_creation_uses_governance_permission():
    assert "FINANZAS_REGLA_GESTIONAR" in SERVICE


def test_rule_creation_supports_scopes():
    for token in [
        '"GLOBAL"',
        '"INMUEBLE"',
        '"ESTRUCTURA"',
        '"ESPACIO"',
    ]:
        assert token in SERVICE


def test_rule_creation_validates_scope_shape():
    for token in [
        "INVALID_PROPERTY_RULE_SCOPE",
        "INVALID_STRUCTURE_RULE_SCOPE",
        "INVALID_SPACE_RULE_SCOPE",
    ]:
        assert token in SERVICE


def test_rule_requires_active_definition():
    assert (
        "FINANCIAL_RULE_DEFINITION_NOT_FOUND"
        in SERVICE
    )


def test_rule_requires_approved_policy():
    assert (
        "FINANCIAL_RULE_REQUIRES_APPROVED_POLICY"
        in SERVICE
    )


def test_service_exposes_version_creation():
    assert "def create_rule_version(" in SERVICE
    assert (
        "INSERT INTO financial_rule_versions"
        in SERVICE
    )


def test_new_version_starts_as_draft():
    assert "'BORRADOR'" in SERVICE


def test_service_exposes_version_approval():
    assert "def approve_rule_version(" in SERVICE
    assert "FINANZAS_REGLA_APROBAR" in SERVICE


def test_version_approval_uses_row_lock():
    assert "FOR UPDATE" in SERVICE
    assert (
        "FINANCIAL_RULE_VERSION_NOT_APPROVABLE"
        in SERVICE
    )


def test_service_exposes_controlled_closure():
    assert "def close_rule_version(" in SERVICE

    for token in [
        "cerrado_por",
        "cerrado_en",
        "motivo_cierre",
    ]:
        assert token in SERVICE


def test_version_closure_requires_reason():
    assert (
        "FINANCIAL_RULE_CLOSURE_REASON_REQUIRED"
        in SERVICE
    )


def test_version_closure_validates_date():
    assert (
        "INVALID_EFFECTIVE_DATE_RANGE"
        in SERVICE
    )


def test_rule_commands_write_financial_audit():
    for token in [
        "FINANCIAL_RULE_CREATED",
        "FINANCIAL_RULE_VERSION_CREATED",
        "FINANCIAL_RULE_VERSION_APPROVED",
        "FINANCIAL_RULE_VERSION_CLOSED",
    ]:
        assert token in SERVICE


def test_rule_commands_are_atomic():
    assert "connection.commit()" in SERVICE
    assert "connection.rollback()" in SERVICE


def test_rule_commands_return_traceability():
    assert '["audit_event_id"]' in SERVICE
    assert '["trace_id"]' in SERVICE


def test_rule_commands_do_not_modify_movements():
    for token in [
        "INSERT INTO cargos",
        "UPDATE cargos",
        "DELETE FROM cargos",
        "INSERT INTO pagos",
        "UPDATE pagos",
        "DELETE FROM pagos",
    ]:
        assert token not in SERVICE


def test_rule_commands_have_no_ui_dependency():
    assert "import streamlit" not in SERVICE
    assert "st." not in SERVICE


def test_global_rule_creation_is_explicit_and_governed():
    assert 'INVALID_GLOBAL_RULE_SCOPE' in SERVICE
    assert 'GLOBAL_FINANCIAL_RULE_REQUIRES_GLOBAL_ADMIN' in SERVICE
    assert '(None if scope_level == "GLOBAL" else property_id)' in SERVICE
