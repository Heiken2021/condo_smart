from pathlib import Path


ROOT = Path(__file__).parents[1]


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def test_root_security_migration_exists():
    source = read(
        "database/migrations/018_root_security_governance_build02.sql"
    )

    assert "autoridad_root" in source
    assert "'PRINCIPAL'" in source
    assert "'DELEGADO'" in source
    assert "trg_proteger_gobierno_root" in source
    assert "ROOT_PRINCIPAL_PROTECTED" in source


def test_root_principal_is_database_protected():
    source = read(
        "database/migrations/018_root_security_governance_build02.sql"
    )

    assert "OLD.autoridad_root = 'PRINCIPAL'" in source
    assert "NEW.rol_global IS DISTINCT FROM 'SUPERADMIN'" in source
    assert "NEW.activo IS DISTINCT FROM TRUE" in source


def test_only_root_principal_can_manage_delegates():
    source = read("services/root_security.py")

    assert "def require_root_principal" in source
    assert 'actor.get("autoridad_root") != ROOT_PRINCIPAL' in source
    assert 'raise PermissionError("ROOT_PRINCIPAL_REQUIRED")' in source
    assert "require_root_principal(actor_id)" in source


def test_root_principal_cannot_be_revoked():
    source = read("services/root_security.py")

    assert 'target.get("autoridad_root") == ROOT_PRINCIPAL' in source
    assert 'raise ValueError("ROOT_PRINCIPAL_PROTECTED")' in source


def test_delegate_grant_and_revoke_are_explicit():
    source = read("services/root_security.py")

    assert "def grant_delegated_root" in source
    assert "def revoke_delegated_root" in source
    assert "autoridad_root='DELEGADO'" in source
    assert "autoridad_root=NULL" in source


def test_root_security_ui_is_under_configuration_security():
    source = read("views/configuracion.py")

    assert "Gobierno De Seguridad Root" in source
    assert "Conceder Acceso Root Delegado" in source
    assert "Revocar Acceso Root Delegado" in source
    assert "is_root_principal(user)" in source


def test_root_security_actions_are_audited():
    source = read("views/configuracion.py")

    assert '"ROOT_DELEGADO_ASIGNAR"' in source
    assert '"ROOT_DELEGADO_REVOCAR"' in source
    assert '"ROOT_PRIVILEGE_DENIED"' in source
    assert 'module="SEGURIDAD"' in source


def test_root_actions_are_critical_tokens():
    source = read("services/audit_service.py")

    assert '"ROOT_DELEGADO_ASIGNAR"' in source
    assert '"ROOT_DELEGADO_REVOCAR"' in source
    assert '"ROOT_PRIVILEGE_DENIED"' in source
    assert '"ROOT_PRINCIPAL_PROTECTED"' in source
