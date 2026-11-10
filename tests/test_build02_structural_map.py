from pathlib import Path
import hashlib

A=Path("app.py").read_text(encoding="utf-8")
I=Path("views/inmuebles.py").read_text(encoding="utf-8")
M=Path("CONDO_SMART_FUNCTIONAL_MAP.md").read_text(encoding="utf-8")

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def test_general_navigation_is_hierarchical():
    for token in ["reportes","notificaciones","soporte"]:
        assert f"views.{token}" in A
    assert "views.areas_comunes" not in A
    assert "views.planos" not in A

def test_inmuebles_contains_nested_children():
    for section in ["Áreas Comunes","Planos"]:
        assert f'if section == "{section}":' in I

def test_general_icons_derive_from_validated_designer_crops_with_white_background():
    from PIL import Image
    for name in ["portafolio","personas","inmuebles","dashboard","reportes","notificaciones","configuracion","soporte"]:
        active=Image.open(f"assets/brand/icons/{name}.png").convert("RGBA")
        source=Image.open(f"assets/brand/icon_candidates_general/{name}.png").convert("RGBA")
        assert active.size == source.size
        w,h=active.size
        for xy in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]: assert active.getpixel(xy)[:3] == (255,255,255)

def test_inmuebles_icons_are_exact_validated_designer_crops():
    for name in ["areas_comunes","planos"]:
        assert sha(f"assets/brand/icons_inmuebles/{name}.png") == sha(f"assets/brand/icon_candidates/{name}.png")

def test_functional_map_preserves_exact_icon_rule_and_builds():
    assert "extracciones exactas" in M
    assert "NO entradas del menu principal" in M
    assert "Build 03" in M and "Build 04" in M and "Por asignar" in M
