from pathlib import Path


S = Path("services/spaces.py").read_text(encoding="utf-8")
V = Path("views/espacios.py").read_text(encoding="utf-8")


def test_spaces_use_central_authorization():
    assert "from core.authorization import require" in S
    assert "def _require_actor(" in S


def test_space_create_permission():
    assert '"ESPACIO_CREAR"' in S


def test_space_modify_permission():
    assert '"ESPACIO_MODIFICAR"' in S


def test_space_state_permissions():
    assert '"ESPACIO_DESACTIVAR"' in S
    assert '"ESPACIO_REACTIVAR"' in S


def test_space_delete_permission():
    assert '"ESPACIO_ELIMINAR"' in S


def test_space_update_is_resource_scoped():
    assert "WHERE id=%s AND condominio_id=%s" in S


def test_space_delete_is_resource_scoped():
    assert "DELETE FROM espacios WHERE id=%s AND condominio_id=%s" in S


def test_history_is_modify_protected():
    block = S.split("def sync_responsible_history",1)[1].split(
        "def set_active",1
    )[0]
    assert '"ESPACIO_MODIFICAR"' in block


def test_view_passes_authenticated_actor():
    assert 'actor_id=user["id"]' in V
    assert 'target,user["id"])' in V
