from pathlib import Path
APP=Path("app.py").read_text(encoding="utf-8")

def test_selector_has_explicit_global_context():
    assert "no_property_label='Sin inmueble activo'" in APP
    assert "quick_names=[no_property_label,*list(quick_labels)]" in APP
    assert "else 0" in APP

def test_close_updates_widget_state_and_context_keys():
    assert "st.session_state.quick_property_selector=no_property_label" in APP
    for key in ["condominio_id", "condominio", "inmueble_gestion_id"]:
        assert f"st.session_state.pop('{key}',None)" in APP

def test_manual_global_option_clears_context():
    assert "if selected_label == no_property_label:" in APP
    assert "expected_quick_label=active_label or no_property_label" in APP
