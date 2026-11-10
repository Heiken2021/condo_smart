from pathlib import Path
C=Path("views/configuracion.py").read_text(encoding="utf-8")
B=Path("components/brand.py").read_text(encoding="utf-8")
def test_brand_layout_controls_in_configuration():
    for x in ["SYSTEM_LOGO_WIDTH","SYSTEM_LOGO_MAX_HEIGHT","SYSTEM_LOGO_OFFSET_Y","SYSTEM_MENU_OFFSET_Y","Guardar Ajustes De Presentación"]: assert x in C
def test_brand_layout_is_dynamic_and_bounded():
    assert "def _layout_settings" in B
    assert "max(80,min(width,420))" in B and "max(-80,min(menu_y,80))" in B
def test_logo_preserves_aspect_ratio():
    assert "object-fit:contain" in B and "max-height:{logo_height}px" in B
def test_menu_spacing_avoids_active_property_overlap():
    assert "menu_spacing = 24" in B
    assert ".cs-menu-offset{{margin-top:0!important}}" in B
    assert "translateY({menu_y}px)" not in B
