from pathlib import Path
def r(p):return Path(p).read_text(encoding="utf-8")
def test_no_query_param_navigation():assert "st.query_params" not in r("app.py")
def test_session_state_navigation():assert "st.session_state.get('cs_nav'" in r("app.py")
def test_native_button_navigation():
 s=r("components/brand.py");assert "st.button(label" in s and "return selected" in s
def test_nav_no_anchor_reload():
 s=r("components/brand.py");assert 'href="?nav=' not in s
