from pathlib import Path
APP=Path("app.py").read_text(encoding="utf-8")

def test_property_bar_has_explicit_global_state():
    assert "no_property_label='Sin inmueble activo'" in APP
    assert "quick_names=[no_property_label,*list(quick_labels)]" in APP

def test_close_uses_pre_widget_callback():
    assert "def _close_active_property():" in APP
    assert "on_click=_close_active_property" in APP

def test_close_callback_updates_selector_and_context():
    callback=APP[APP.index("def _close_active_property():"):APP.index("def _change_quick_property():")]
    assert "_clear_property_context()" in callback
    assert "st.session_state.quick_property_selector=no_property_label" in callback

def test_button_has_no_post_instantiation_mutation():
    button=APP[APP.index("quick_cols[2].button("):APP.index("with st.sidebar:")]
    assert "st.session_state.quick_property_selector=" not in button
    assert "st.rerun()" not in button
