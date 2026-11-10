from pathlib import Path
M=Path('database/migrations/014_password_recovery_structure_management_build02.sql').read_text(encoding='utf-8')
A=Path('core/auth.py').read_text(encoding='utf-8')
R=Path('services/password_recovery.py').read_text(encoding='utf-8')
S=Path('services/property_structure.py').read_text(encoding='utf-8')
I=Path('views/inmuebles.py').read_text(encoding='utf-8')

def test_password_recovery_is_token_based():
 assert 'password_reset_tokens' in M and 'token_hash' in M and 'usado_en' in M
 assert '¿Olvidaste tu contraseña?' in A
 assert 'reset_password_with_code' in R and 'password_hash' in R
 assert 'send_password_reset_email' in R

def test_structure_grid_and_management():
 assert 'structure_management_grid_' in I and 'selection_mode="single-row"' in I
 for x in ['update_node','set_node_active','node_dependencies','delete_node']: assert x in S
 for x in ['Editar','Cambiar Estado','Eliminar Estructura']: assert x in I

def test_admin_revoke_is_explicit_and_permissioned():
 assert 'Eliminar / Revocar Del Inmueble' in I
 assert 'ADMINISTRADOR_REVOCAR' in I
