from pathlib import Path


def read(path):
    return Path(path).read_text(encoding="utf-8")


def test_sidebar_is_display_only():
    s = read("core/access.py")
    assert "selectbox('Inmueble Activo'" not in s
    assert "Ninguno seleccionado" in s
    assert "Inmueble Activo" in s
    assert "st.sidebar.markdown" in s
    assert "current['nombre']" in s


def test_no_default_property_selection():
    access = read("core/access.py")
    inmuebles = read("views/inmuebles.py")

    assert "rows[0]['id']" not in access
    assert 'selected_id = rows[0]["id"]' not in inmuebles


def test_grid_establishes_global_context():
    s = read("views/inmuebles.py")

    assert "st.session_state.condominio_id = newly_selected_id" in s
    assert "refresh_current_property(newly_selected_id)" in s


def test_management_tabs_require_property_selection():
    s = read("views/inmuebles.py")

    assert s.count(
        "Selecciona primero un inmueble en el grid superior."
    ) == 5
