from pathlib import Path
V=Path("views/espacios.py").read_text(encoding="utf-8")
def test_search_filter_selection_is_bounds_checked():
    assert "0 <= selected_index < len(filtered)" in V
    assert "selected=filtered[indexes[0]]" not in V
def test_stale_selection_resolves_to_none():
    assert "else None" in V
