from pathlib import Path
A=Path('core/access.py').read_text(encoding='utf-8')
P=Path('services/properties.py').read_text(encoding='utf-8')
AN=Path('services/analytics.py').read_text(encoding='utf-8')
V=Path('views/inmuebles.py').read_text(encoding='utf-8')
S=Path('services/spaces.py').read_text(encoding='utf-8')
PERM=Path('core/permissions.py').read_text(encoding='utf-8')
APP=Path('app.py').read_text(encoding='utf-8')

def test_properties_are_server_filtered():
 assert 'JOIN usuario_inmuebles ui' in P and 'ui.usuario_id=%s' in P and 'list_properties(user)' in V

def test_context_is_assignment_validated():
 assert 'ui.usuario_id=%s AND ui.activo=TRUE' in A and 'ensure_property_context(u)' in APP

def test_property_creation_is_superadmin_only():
 assert 'user.get("rol_global") == "SUPERADMIN"' in V

def test_portfolio_is_user_scoped():
 assert 'def prop_rows(user):' in AN and 'scope.usuario_id=%s' in AN

def test_people_are_property_scoped():
 assert 'def list_people(property_id):' in S and 'e.condominio_id=%s' in S

def test_global_modules_are_superadmin_only():
 assert "{'configuracion','catalogos'}" in PERM
 assert "{'configuracion','catalogos','auditoria'}" not in PERM
 assert "'auditoria'" in PERM
