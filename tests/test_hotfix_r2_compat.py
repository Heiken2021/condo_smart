from pathlib import Path


def test_public_datauri_compatibility():
    ui = Path('components/ui.py').read_text(encoding='utf-8')
    assert 'def datauri(' in ui


def test_r2_01_uses_central_authorization():
    view = Path('views/inmuebles.py').read_text(encoding='utf-8')
    assert 'from core.authorization import authorize' in view
    assert 'decision(user, "INMUEBLE_CREAR")' in view


def test_r2_01_catalog_contract():
    view = Path('views/inmuebles.py').read_text(encoding='utf-8')
    assert 'options("TIPO_INMUEBLE")' in view


def test_r2_01_image_contract():
    view = Path('views/inmuebles.py').read_text(encoding='utf-8')
    for ext in ['"jpg"', '"jpeg"', '"png"', '"bmp"']:
        assert ext in view


def test_r2_01_tabs_preserved():
    view = Path('views/inmuebles.py').read_text(encoding='utf-8')
    assert '"Datos Generales"' in view
    assert '"Administradores"' in view
