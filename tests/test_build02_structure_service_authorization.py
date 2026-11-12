from pathlib import Path


SERVICE = Path(
    "services/property_structure.py"
).read_text(encoding="utf-8")

VIEW = Path(
    "views/inmuebles.py"
).read_text(encoding="utf-8")


def test_structure_service_uses_central_authorization():
    assert "from core.authorization import require" in SERVICE
    assert "def _require_actor(" in SERVICE
    assert "return require(" in SERVICE


def test_structure_create_is_service_protected():
    assert '"ESTRUCTURA_CREAR"' in SERVICE
    assert "actor_id=None" in SERVICE


def test_structure_update_is_service_protected():
    assert '"ESTRUCTURA_MODIFICAR"' in SERVICE
    assert "def update_node(" in SERVICE


def test_structure_state_change_is_service_protected():
    assert '"ESTRUCTURA_REACTIVAR"' in SERVICE
    assert '"ESTRUCTURA_DESACTIVAR"' in SERVICE
    assert "def set_node_active(" in SERVICE


def test_structure_delete_is_service_protected():
    assert '"ESTRUCTURA_ELIMINAR"' in SERVICE
    assert "def delete_node(" in SERVICE


def test_structure_resources_remain_property_scoped():
    assert "WHERE id=%s AND condominio_id=%s" in SERVICE
    assert (
        "DELETE FROM estructura_inmueble "
        in SERVICE
    )
    assert "condominio_id=%s" in SERVICE


def test_view_passes_actor_to_structure_mutations():
    assert (
        'parent_map[p],user["id"])'
        in VIEW
    )
    assert (
        'selected_node["id"],target,user["id"])'
        in VIEW
    )
    assert (
        'selected_node["id"],user["id"])'
        in VIEW
    )


def test_space_structure_validation_stays_property_scoped():
    assert "def validate_space_structure(" in SERVICE
    assert "get_node(property_id, structure_id)" in SERVICE
