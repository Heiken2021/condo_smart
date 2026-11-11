from pathlib import Path


SERVICE = Path("services/properties.py").read_text(
    encoding="utf-8"
)

VIEW = Path("views/inmuebles.py").read_text(
    encoding="utf-8"
)


def test_property_service_uses_central_authorization():
    assert "from core.authorization import require" in SERVICE
    assert "def _require_actor(" in SERVICE
    assert "return require(" in SERVICE


def test_create_property_is_service_protected():
    assert "def create_property(actor_id, values):" in SERVICE
    assert '"INMUEBLE_CREAR"' in SERVICE
    assert "create_property(" in VIEW


def test_property_update_is_service_protected():
    assert "def update_property(pid, values, actor_id):" in SERVICE
    assert '"INMUEBLE_MODIFICAR"' in SERVICE
    assert "update_property(" in VIEW


def test_branding_is_service_protected():
    assert "def update_logo(pid, data, mime, actor_id):" in SERVICE
    assert "def delete_logo(pid, actor_id):" in SERVICE
    assert "def update_cover(pid, data, mime, actor_id):" in SERVICE
    assert "def delete_cover(pid, actor_id):" in SERVICE
    assert '"INMUEBLE_BRANDING"' in SERVICE


def test_property_status_is_service_protected():
    assert "def set_property_active(pid, active, actor_id):" in SERVICE
    assert '"INMUEBLE_REACTIVAR"' in SERVICE
    assert '"INMUEBLE_DESACTIVAR"' in SERVICE


def test_property_delete_is_service_protected():
    assert "def delete_property(pid, actor_id):" in SERVICE
    assert '"INMUEBLE_ELIMINAR"' in SERVICE
    assert "PROPERTY_HAS_DEPENDENCIES" in SERVICE


def test_property_dependencies_require_delete_permission():
    assert "def dependencies(pid, actor_id):" in SERVICE
    block = SERVICE.split(
        "def dependencies(pid, actor_id):",
        1,
    )[1].split(
        "def deletable",
        1,
    )[0]
    assert '"INMUEBLE_ELIMINAR"' in block


def test_view_no_longer_writes_property_core_operations_directly():
    assert (
        '"INSERT INTO condominios('
        not in VIEW
    )

    assert (
        '"UPDATE condominios SET clave='
        not in VIEW
    )

    assert (
        '"UPDATE condominios SET activo='
        not in VIEW
    )

    assert (
        '"DELETE FROM condominios WHERE id=%s"'
        not in VIEW
    )


def test_property_service_keeps_user_scoped_list():
    assert "def list_properties(user):" in SERVICE
    assert "JOIN usuario_inmuebles ui" in SERVICE
    assert "ui.usuario_id=%s" in SERVICE
    assert "ui.activo=TRUE" in SERVICE
