from pathlib import Path
B=Path("components/brand.py").read_text(encoding="utf-8")
def test_sidebar_logo_can_scale_above_intrinsic_size():
    assert 'width:min(100%,{int(max_width)}px);max-width:none' in B
    assert 'width:min(100%,{logo_width}px)!important' in B
    assert 'max-width:none!important' in B
def test_sidebar_logo_keeps_aspect_ratio():
    assert 'height:auto!important' in B
    assert 'object-fit:contain!important' in B
