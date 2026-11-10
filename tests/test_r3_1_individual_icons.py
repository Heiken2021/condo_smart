from pathlib import Path
from PIL import Image
import hashlib

N=["portafolio","dashboard","inmuebles","espacios","personas","usuarios","finanzas","catalogos","configuracion","auditoria"]
GENERAL_EXACT=["portafolio","dashboard","inmuebles","personas","configuracion"]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def test_individual_png_icons():
 for n in N:
  p=Path("assets/brand/icons")/f"{n}.png"
  assert p.exists()
  w,h=Image.open(p).size
  assert w>0 and h>0

def test_general_icons_keep_designer_geometry_with_white_background():
 for n in GENERAL_EXACT:
  active=Image.open(Path("assets/brand/icons")/f"{n}.png").convert("RGBA")
  source=Image.open(Path("assets/brand/icon_candidates_general")/f"{n}.png").convert("RGBA")
  assert active.size == source.size
  w,h=active.size
  assert active.getpixel((0,0))[:3] == (255,255,255)
  assert active.getpixel((w-1,h-1))[:3] == (255,255,255)

def test_individual_ico_icons():
 for n in N: assert (Path("assets/brand/icons_ico")/f"{n}.ico").exists()
