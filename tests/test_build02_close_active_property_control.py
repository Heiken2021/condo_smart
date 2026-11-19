from pathlib import Path
APP=Path("app.py").read_text(encoding="utf-8")

def test_global_bar_can_close_active_property():
    assert "'Cerrar inmueble'" in APP
    assert "key='close_active_property'" in APP
    assert "disabled=not bool(active_id)" in APP

def test_close_only_clears_session_context():
    for key in ["condominio_id","condominio","inmueble_gestion_id"]:
        assert f"st.session_state.pop('{key}',None)" in APP
    assert "st.session_state.quick_property_selector=no_property_label" in APP
    block=APP[APP.index("quick_cols[2].button("):APP.index("with st.sidebar:")]
    for forbidden in ['DELETE FROM','delete_property(','UPDATE condominios','execute(']:
        assert forbidden not in block

def test_business_help_is_explicitly_non_destructive():
    assert 'No elimina ni modifica el inmueble.' in APP
