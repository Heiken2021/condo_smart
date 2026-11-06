from pathlib import Path

UI = Path('components/ui.py').read_text(encoding='utf-8')


def test_property_cover_is_discrete():
    assert 'width=220' in UI
    assert 'max_height=125' in UI


def test_property_logo_is_discrete():
    assert 'width=120' in UI
    assert 'max_height=90' in UI


def test_identity_images_are_clickable():
    assert 'target="_blank"' in UI
    assert 'cursor:zoom-in' in UI


def test_identity_full_size_instruction_exists():
    assert 'Haz clic en la imagen para verla en tamaño completo.' in UI
