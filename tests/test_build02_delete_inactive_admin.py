from pathlib import Path
M=Path('database/migrations/015_delete_inactive_admin_build02.sql').read_text(encoding='utf-8')
S=Path('services/property_admins.py').read_text(encoding='utf-8')
I=Path('views/inmuebles.py').read_text(encoding='utf-8')

def test_delete_permission_is_superadmin_only():
 assert 'ADMINISTRADOR_ELIMINAR' in M
 assert "r.codigo='SUPERADMIN'" in M

def test_delete_service_has_guards_and_cleanup():
 for value in ['CANNOT_DELETE_CURRENT_USER','CANNOT_DELETE_SUPERADMIN','ACTIVE_PROPERTY_ASSIGNMENTS','ACTIVE_SPACE_ASSIGNMENTS']:
  assert value in S
 assert 'admin_delete_dependencies' in S and 'delete_inactive_admin' in S
 assert 'DELETE FROM usuarios' in S

def test_delete_ui_requires_explicit_confirmation():
 assert 'Eliminar Administrador De La Base De Datos' in I
 assert 'Eliminar Administrador Definitivamente' in I
 assert 'confirmation == admin["username"]' in I
 assert 'ADMINISTRADOR_ELIMINAR' in I
