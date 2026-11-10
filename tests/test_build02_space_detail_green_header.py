from pathlib import Path
V=Path("views/espacios.py").read_text(encoding="utf-8")

def test_selected_space_uses_green_context_card():
    assert "cs-selected-space" in V
    assert "background:#D9F5E5" in V
    assert "color:#087D45" in V
    assert "border-radius:11px" in V

def test_selected_space_header_keeps_code_and_name():
    assert "row.get('clave')" in V and "row.get('nombre')" in V
