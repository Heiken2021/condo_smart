from pathlib import Path
from PIL import Image
A=Path("app.py").read_text(encoding="utf-8")
C=Path("views/configuracion.py").read_text(encoding="utf-8")

def test_menu_order_and_no_users_top_level():
    expected=["portafolio","dashboard","inmuebles","espacios","personas","finanzas","reportes","catalogos","notificaciones","auditoria","configuracion","soporte"]
    line=next(x for x in A.splitlines() if x.startswith("P=["))
    positions=[line.index(f"'{x}'") for x in expected]
    assert positions==sorted(positions)
    assert "'usuarios','views.usuarios'" not in line

def test_users_access_nested_in_configuration():
    assert "Usuarios Y Accesos" in C
    assert "render_users_access()" in C

def test_general_icon_corners_are_white():
    for name in ["portafolio","dashboard","inmuebles","personas","reportes","notificaciones","configuracion","soporte"]:
        im=Image.open(Path("assets/brand/icons")/f"{name}.png").convert("RGBA")
        w,h=im.size
        for xy in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]:
            assert im.getpixel(xy)[:3]==(255,255,255)
