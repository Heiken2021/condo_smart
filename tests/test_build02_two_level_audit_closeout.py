
from pathlib import Path


P = Path("core/permissions.py").read_text(encoding="utf-8")
M = Path(
    "database/migrations/016_two_level_audit_build02.sql"
).read_text(encoding="utf-8")
S = Path("services/audit_service.py").read_text(encoding="utf-8")


def test_audit_is_not_globally_hidden_from_local_roles():
    assert "{'configuracion','catalogos','auditoria'}" not in P
    assert "{'configuracion','catalogos'}" in P


def test_property_administrators_can_navigate_to_audit():
    admin_block = P.split(
        "if roles & {'ADMINISTRADOR','GERENTE','COMITE'}:",
        1,
    )[1].split("if 'CONTABILIDAD'", 1)[0]

    assert "'auditoria'" in admin_block


def test_accounting_can_navigate_to_financial_audit():
    accounting_block = P.split(
        "if 'CONTABILIDAD' in roles:",
        1,
    )[1].split("if roles &", 1)[0]

    assert "'auditoria'" in accounting_block


def test_financial_ledger_has_database_immutability():
    assert "prevent_auditoria_financiera_mutation" in M
    assert "BEFORE UPDATE OR DELETE" in M
    assert "AUDITORIA_FINANCIERA_IS_APPEND_ONLY" in M


def test_financial_service_remains_append_only():
    assert "INSERT INTO auditoria_financiera" in S
    assert "UPDATE auditoria_financiera" not in S
    assert "DELETE FROM auditoria_financiera" not in S
