from pathlib import Path
B=Path("components/brand.py").read_text(encoding="utf-8")
def test_logo_has_spacing_below_for_version():
    assert 'margin:{logo_y}px auto 1.15rem' in B
