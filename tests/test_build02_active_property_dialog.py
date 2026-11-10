from pathlib import Path
A=Path("app.py").read_text(encoding="utf-8")

def test_missing_property_uses_modal_dialog():
    assert '@st.dialog("Inmueble requerido", dismissible=False)' in A
    assert 'No hay un inmueble activo.' in A
    assert 'Selecciona un inmueble para continuar.' in A
    assert 'st.button("OK"' in A

def test_dialog_redirects_to_properties():
    assert 'st.session_state.cs_nav = "inmuebles"' in A
    assert 'st.rerun()' in A

def test_context_guard_runs_before_sidebar_navigation():
    guard=A.index("if nav in PROPERTY_REQUIRED")
    sidebar=A.index("selected=sidebar_nav")
    assert guard < sidebar

def test_global_sections_do_not_require_property():
    for key in ["portafolio", "inmuebles", "configuracion", "reportes", "notificaciones", "soporte"]:
        assert f"'{key}'" in A.split("PROPERTY_REQUIRED",1)[1].split("}",1)[0]

def test_context_guard_checks_active_property():
    assert "not st.session_state.get('condominio_id')" in A
