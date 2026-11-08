from pathlib import Path
def r(p): return Path(p).read_text(encoding="utf-8")
def test_brand_icon_gradients():
 s=r("components/brand.py"); assert "linearGradient" in s and "feDropShadow" in s and "stroke-width=\"2.6\"" in s
def test_brand_blue_green_palette():
 s=r("components/brand.py")
 for c in ["#082F5B","#0878C9","#20AA58","#59D85D"]: assert c in s
def test_menu_business_titles_preserved():
 s=r("app.py")
 for x in ["Portafolio","Dashboard","Inmuebles","Espacios","Propietarios / Inquilinos","Finanzas","Catálogos","Configuración General","Auditoría"]: assert x in s
