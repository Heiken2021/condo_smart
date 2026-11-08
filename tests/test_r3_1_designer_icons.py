from pathlib import Path
N=["portafolio","dashboard","inmuebles","espacios","personas","usuarios","finanzas","catalogos","configuracion","auditoria"]
def test_exact_designer_icon_assets_exist():
 for n in N: assert (Path("assets/brand/icons")/f"{n}.png").exists()
def test_designer_reference_versioned(): assert Path("assets/brand/Designer.png").exists()
def test_sidebar_uses_png_asset_library():
 s=Path("components/brand.py").read_text(encoding="utf-8"); assert "menu_icon_uri(key)" in s and "cs-designer-icon" in s
