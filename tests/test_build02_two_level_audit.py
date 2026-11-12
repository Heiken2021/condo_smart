from pathlib import Path


M = Path(
    "database/migrations/016_two_level_audit_build02.sql"
).read_text(encoding="utf-8")

S = Path(
    "services/audit_service.py"
).read_text(encoding="utf-8")

A = Path(
    "core/auth.py"
).read_text(encoding="utf-8")

V = Path(
    "views/auditoria.py"
).read_text(encoding="utf-8")


def test_existing_system_audit_is_extended():
    assert "ALTER TABLE auditoria" in M
    assert "modulo" in M
    assert "trace_id" in M


def test_financial_ledger_exists():
    assert "CREATE TABLE IF NOT EXISTS auditoria_financiera" in M
    assert "monto_mxn" in M
    assert "evento_relacionado_id" in M


def test_financial_ledger_is_append_only_in_application_service():
    assert "INSERT INTO auditoria_financiera" in S
    assert "UPDATE auditoria_financiera" not in S
    assert "DELETE FROM auditoria_financiera" not in S


def test_audit_payloads_are_sanitized():
    assert "SENSITIVE_KEYS" in S
    assert "[REDACTED]" in S
    for token in [
        "password",
        "token",
        "api_key",
        "database_url",
    ]:
        assert token in S


def test_system_audit_uses_sanitized_serializer():
    assert "serialize(before)" in A
    assert "serialize(after)" in A


def test_audit_user_scope_is_enforced():
    assert '"AUDITORIA_INMUEBLE"' in S
    assert "condominio_id=%s" in S


def test_financial_audit_user_scope_is_enforced():
    assert '"AUDITORIA_FINANCIERA"' in S
    assert "def list_financial_audit(" in S


def test_superadmin_can_use_global_audit():
    assert 'rol_global") == "SUPERADMIN"' in S


def test_financial_event_is_attributable():
    assert "usuario_id" in S
    assert "username" in S
    assert "trace_id" in S


def test_audit_view_has_two_levels():
    assert '"Actividad Del Sistema"' in V
    assert '"Auditoría Financiera"' in V


def test_financial_view_is_ready_for_business_events():
    for label in [
        "Operación",
        "Entidad",
        "Referencia",
        "Monto MXN",
    ]:
        assert label in V


def test_migration_adds_property_scoped_permissions():
    assert "AUDITORIA_INMUEBLE" in M
    assert "AUDITORIA_FINANCIERA" in M
    assert "ADMINISTRADOR" in M
    assert "CONTABILIDAD" in M


def test_existing_audit_contract_is_preserved():
    assert "def audit(" in A
    assert "resultado" in A
    assert "valor_anterior" in A
    assert "valor_nuevo" in A


def test_financial_core_tables_are_not_mutated_by_audit_service():
    assert "UPDATE cargos" not in S
    assert "UPDATE pagos" not in S
    assert "UPDATE gastos" not in S
    assert "DELETE FROM cargos" not in S
    assert "DELETE FROM pagos" not in S
    assert "DELETE FROM gastos" not in S
