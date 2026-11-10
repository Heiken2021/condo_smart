from pathlib import Path
A=Path("app.py").read_text(encoding="utf-8")
def test_quick_selector_has_dedicated_top_container():
 assert "st.container(key='quick_property_bar')" in A
 assert ".st-key-quick_property_bar" in A
def test_quick_selector_is_shifted_up():
 assert "top:-2.65rem" in A
 assert "margin-bottom:-2.25rem" in A
def test_quick_selector_functionality_is_preserved():
 assert "key='quick_property_selector'" in A
 assert "on_change=_change_quick_property" in A
 assert "refresh_current_property(selected_id)" in A
