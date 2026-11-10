from pathlib import Path
import ast
B=Path("components/brand.py").read_text(encoding="utf-8")
def test_brand_module_ast_parses():
 ast.parse(B)
def test_dynamic_css_has_escaped_root_braces():
 assert ":root{{--cs-navy:" in B
def test_dynamic_values_remain_fstring_placeholders():
 for x in ["{logo_y}","{logo_width}","{logo_height}"]: assert x in B

def test_menu_offset_does_not_translate_entire_sidebar():
 assert "translateY({menu_y}px)" not in B
 assert "menu_spacing = 24" in B
