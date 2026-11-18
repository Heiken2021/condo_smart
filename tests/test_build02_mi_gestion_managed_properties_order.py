from pathlib import Path

VIEW=Path("views/portafolio.py").read_text(encoding="utf-8")

def test_snapshot_grid_is_separate_renderer():
    assert "def _render_managed_properties_grid(rows):" in VIEW
    management=VIEW.split("def _render_management_snapshot(rows):",1)[1].split("def render():",1)[0]
    assert "Snapshot De Inmuebles Administrados" not in management

def test_snapshot_grid_renders_before_cards_financial_summary_and_management_snapshot():
    render=VIEW.split("def render():",1)[1]
    grid=render.index("_render_managed_properties_grid(")
    cards=render.index("_render_property_cards(")
    financial=render.index("_render_financial_summary(")
    management=render.index("_render_management_snapshot(")
    assert grid < cards < financial < management

def test_snapshot_grid_content_is_preserved():
    assert 'st.markdown("#### Snapshot De Inmuebles Administrados")' in VIEW
    assert "_portfolio_grid(rows)" in VIEW
