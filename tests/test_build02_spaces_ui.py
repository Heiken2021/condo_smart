from pathlib import Path
V=Path("views/espacios.py")
def src(): return V.read_text(encoding="utf-8")
def test_b02_spaces_ui_uses_service_layer():
    s=src(); assert "from services.spaces import" in s and "list_spaces" in s and "create_space" in s
def test_b02_spaces_ui_requires_property_context():
    s=src(); assert "pid=cid()" in s and "if not pid:" in s
def test_b02_spaces_ui_uses_catalogs():
    s=src(); assert 'options("TIPO_ESPACIO")' in s and 'options("ESTADO_ESPACIO")' in s and 'options("USO_ESPACIO")' in s and 'options("CONDICION_FISICA")' in s
def test_b02_spaces_ui_permissions():
    s=src()
    for p in ["ESPACIO_CONSULTAR","ESPACIO_CREAR","ESPACIO_MODIFICAR","ESPACIO_DESACTIVAR","ESPACIO_REACTIVAR","ESPACIO_ELIMINAR"]: assert p in s
def test_b02_spaces_ui_has_selectable_grid():
    s=src(); assert 'on_select="rerun"' in s and 'selection_mode="single-row"' in s
def test_b02_spaces_ui_delete_checks_dependencies():
    s=src(); assert 'dependencies(pid,row["id"])' in s and 'deletable(pid,row["id"])' in s
