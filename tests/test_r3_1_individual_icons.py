from pathlib import Path
from PIL import Image
N=["portafolio","dashboard","inmuebles","espacios","personas","usuarios","finanzas","catalogos","configuracion","auditoria"]
def test_individual_png_icons():
 for n in N:
  p=Path("assets/brand/icons")/f"{n}.png"; assert p.exists(); assert Image.open(p).size==(256,256)
def test_individual_ico_icons():
 for n in N: assert (Path("assets/brand/icons_ico")/f"{n}.ico").exists()
