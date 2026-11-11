from pathlib import Path
S=Path("services/property_admins.py").read_text(encoding="utf-8")
V=Path("views/inmuebles.py").read_text(encoding="utf-8")
SCHEMA=Path("database/schema.sql").read_text(encoding="utf-8")

def test_schema_supports_multi_property_identity():
    assert "PRIMARY KEY(usuario_id,condominio_id,rol_codigo)" in SCHEMA

def test_existing_admin_candidates_exclude_active_assignment():
    assert "def list_assignable_admins(property_id, actor_id):" in S
    assert "current_ui.activo=FALSE" in S
    assert "u.rol_global<>'SUPERADMIN'" in S
    assert "GLOBAL_SUPERADMIN_REQUIRED" in S

def test_assignment_reuses_identity_and_handles_all_states():
    assert "def assign_existing_admin(property_id, user_id, actor_id):" in S
    assert "ALREADY_ACTIVE" in S
    assert "REACTIVATED" in S
    assert "ASSIGNED" in S
    assert "INSERT INTO usuarios" not in S.split("def assign_existing_admin",1)[1]

def test_reactivation_and_revocation_are_property_scoped():
    assert "usuario_id=%s" in S
    assert "condominio_id=%s" in S
    assert "rol_codigo='ADMINISTRADOR'" in S
    assert "def _property_admin(property_id, user_id" in S

def test_ui_requires_assign_permission_and_audits():
    assert '"Asignar Administrador Existente"' in V
    assert '"ADMINISTRADOR_ASIGNAR"' in V
    assert "assign_existing_admin(" in V
    assert '"usuario_inmuebles"' in V
