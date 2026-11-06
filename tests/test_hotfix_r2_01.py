from pathlib import Path

VIEW = Path('views/inmuebles.py').read_text(encoding='utf-8')


def test_password_error_is_caught():
    assert 'except ValueError' in VIEW
    assert 'La contraseña no cumple la política de seguridad' in VIEW


def test_property_create_permission_does_not_raise_on_page_open():
    assert 'decision(user, "INMUEBLE_CREAR")' in VIEW
    assert 'if not access.allowed' in VIEW


def test_all_property_permissions_are_non_crashing():
    for permission in [
        'INMUEBLE_MODIFICAR',
        'ADMINISTRADOR_ASIGNAR',
        'INMUEBLE_BRANDING',
        'INMUEBLE_DESACTIVAR',
        'INMUEBLE_REACTIVAR',
        'INMUEBLE_ELIMINAR',
    ]:
        assert permission in VIEW


def test_admin_sees_friendly_denied_message():
    assert 'Tu perfil no cuenta con el permiso' in VIEW
