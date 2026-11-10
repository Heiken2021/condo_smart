from pathlib import Path
A=Path("app.py").read_text(encoding="utf-8")
def test_quick_property_selector_uses_authorized_properties():
 assert "ensure_property_context(u)" in A
 assert "quick_property_selector" in A
def test_quick_selector_updates_active_context_via_callback():
 assert "def _change_quick_property():" in A
 assert "on_change=_change_quick_property" in A
 assert "st.session_state.condominio_id=selected_id" in A
 assert "st.session_state.inmueble_gestion_id=selected_id" in A
 assert "refresh_current_property(selected_id)" in A

def test_quick_selector_does_not_require_manual_rerun():
 assert "selected_id==st.session_state.get('condominio_id')" in A
 assert "if quick_id != active_id:" not in A
