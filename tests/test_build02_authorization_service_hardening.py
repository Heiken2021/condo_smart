from pathlib import Path


SERVICE = Path("services/property_admins.py").read_text(
    encoding="utf-8"
)
VIEW = Path("views/inmuebles.py").read_text(
    encoding="utf-8"
)


def test_admin_service_uses_central_authorization():
    assert "from core.authorization import require" in SERVICE
    assert "def _require_actor(" in SERVICE
    assert "return require(" in SERVICE


def test_admin_mutations_validate_permissions_in_service():
    for permission in [
        "ADMINISTRADOR_CREAR",
        "ADMINISTRADOR_MODIFICAR",
        "ADMINISTRADOR_ASIGNAR",
        "ADMINISTRADOR_REVOCAR",
    ]:
        assert permission in SERVICE


def test_admin_target_is_scoped_to_property():
    assert "def _property_admin(" in SERVICE
    assert "ui.condominio_id=%s" in SERVICE
    assert "u.id=%s" in SERVICE


def test_password_reset_requires_property_and_actor():
    assert (
        "def reset_password(property_id, user_id, password, actor_id):"
        in SERVICE
    )
    assert (
        'reset_password(\n'
        '                                row["id"],\n'
        '                                admin["id"],\n'
        '                                new_password,\n'
        '                                user["id"],'
        in VIEW
    )


def test_profile_update_requires_property_and_actor():
    assert "def update_admin_profile(" in SERVICE
    assert '"ADMINISTRADOR_MODIFICAR"' in SERVICE
    assert 'row["id"],\n                                admin["id"],' in VIEW


def test_global_identity_enumeration_is_superadmin_only():
    assert "def list_assignable_admins(property_id, actor_id):" in SERVICE
    assert 'GLOBAL_SUPERADMIN_REQUIRED' in SERVICE


def test_permanent_identity_delete_is_superadmin_only():
    block = SERVICE.split(
        "def delete_inactive_admin",
        1,
    )[1]
    assert 'actor.get("rol_global") != "SUPERADMIN"' in block
    assert "GLOBAL_SUPERADMIN_REQUIRED" in block


def test_assignment_updates_are_property_scoped():
    assert "usuario_id=%s" in SERVICE
    assert "condominio_id=%s" in SERVICE
    assert "rol_codigo='ADMINISTRADOR'" in SERVICE
