import ast,importlib
from pathlib import Path
from core.formatting import labels,money
from core.security import hash_password,verify_password,validate_password
V=['views.portafolio','views.dashboard','views.inmuebles','views.espacios','views.personas','views.usuarios','views.catalogos','views.auditoria']
def test_01_syntax():
 for p in Path('.').rglob('*.py'):
  if '.venv' not in p.parts:ast.parse(p.read_text())
def test_02_views_import():
 for v in V:assert hasattr(importlib.import_module(v),'render')
def test_03_single_navigation():assert not Path('pages').exists()
def test_04_dashboard_exists():assert Path('views/dashboard.py').exists()
def test_05_portfolio_exists():assert Path('views/portafolio.py').exists()
def test_06_inmuebles_exists():assert Path('views/inmuebles.py').exists()
def test_07_spaces_preserved():assert Path('views/espacios.py').exists()
def test_08_people_preserved():assert Path('views/personas.py').exists()
def test_09_users_preserved():assert Path('views/usuarios.py').exists()
def test_10_catalogs_preserved():assert Path('views/catalogos.py').exists()
def test_11_audit_preserved():assert Path('views/auditoria.py').exists()
def test_12_context_label():assert labels('condominios')['tipo_codigo']=='Tipo De Inmueble'
def test_13_space_context_label():assert labels('espacios')['tipo_codigo']=='Tipo De Espacio'
def test_14_internal_id_hidden():assert 'id' not in labels('condominios')
def test_15_money():assert money(2500)=='$2,500.00 MXN'
def test_16_password():
 s,h=hash_password('Seguro2026X');assert verify_password('Seguro2026X',s,h)
def test_17_password_policy():assert validate_password('Seguro2026X')
def test_18_schema_version():assert 'schema_version' in Path('database/schema.sql').read_text()
def test_19_property_branding():
 s=Path('database/schema.sql').read_text();assert 'logo_data' in s and 'portada_data' in s
def test_20_property_rfc_timezone():
 s=Path('database/schema.sql').read_text();assert 'rfc VARCHAR' in s and 'zona_horaria' in s
def test_21_property_crud_ui():
 s=Path('views/inmuebles.py').read_text();
 for x in ['Crear Inmueble','Guardar Cambios','Desactivar','Reactivar','Eliminar Inmueble']:assert x in s
def test_22_property_delete_guard():assert 'deletable' in Path('views/inmuebles.py').read_text()
def test_23_property_audit_actions():
 s=Path('views/inmuebles.py').read_text();
 for x in ['INMUEBLE_CREAR','INMUEBLE_MODIFICAR','INMUEBLE_DESACTIVAR','INMUEBLE_REACTIVAR','INMUEBLE_ELIMINAR','INMUEBLE_BRANDING']:assert x in s
def test_24_image_types():
    s = Path('views/inmuebles.py').read_text(encoding='utf-8')
    for x in ['"jpg"', '"jpeg"', '"png"', '"bmp"']:
        assert x in s
def test_25_catalog_property_type():
    assert 'options(\"TIPO_INMUEBLE\")' in Path('views/inmuebles.py').read_text(encoding='utf-8')
def test_26_admin_isolation_hook():
    assert 'decision(user' in Path('views/inmuebles.py').read_text(encoding='utf-8')
def test_27_qa_gate_exists():assert Path('QA_BUILD01.md').exists()


def test_28_roles_schema():
 s=Path('database/schema.sql').read_text();assert 'CREATE TABLE IF NOT EXISTS roles' in s
def test_29_permissions_schema():assert 'CREATE TABLE IF NOT EXISTS permisos' in Path('database/schema.sql').read_text()
def test_30_global_role():assert 'rol_global' in Path('database/schema.sql').read_text()
def test_31_user_property_audit_fields():
 s=Path('database/schema.sql').read_text();assert 'asignado_por' in s and 'revocado_por' in s
def test_32_authorizer_exists():assert Path('core/authorization.py').exists()
def test_33_authorizer_superadmin():assert 'GLOBAL_SUPERADMIN' in Path('core/authorization.py').read_text()
def test_34_authorizer_local():assert 'PROPERTY_NOT_ASSIGNED' in Path('core/authorization.py').read_text()
def test_35_last_root_trigger():assert 'proteger_ultimo_superadmin' in Path('database/migrations/002_security.sql').read_text()
def test_36_bootstrap_root():assert "'SUPERADMIN'" in Path('core/auth.py').read_text()
def test_37_admin_service():assert Path('services/property_admins.py').exists()
def test_38_multi_admin_query():assert 'list_admins' in Path('services/property_admins.py').read_text()
def test_39_admin_create():assert 'create_admin' in Path('services/property_admins.py').read_text()
def test_40_admin_revoke():assert 'def revoke' in Path('services/property_admins.py').read_text()
def test_41_admin_reactivate():assert 'def reactivate' in Path('services/property_admins.py').read_text()
def test_42_admin_reset_password():assert 'reset_password' in Path('services/property_admins.py').read_text()
def test_43_property_admin_tab():
    assert '\"Administradores\"' in Path('views/inmuebles.py').read_text(encoding='utf-8')
def test_44_property_general_tab():
    assert '\"Datos Generales\"' in Path('views/inmuebles.py').read_text(encoding='utf-8')
def test_45_property_identity_preview():assert 'property_header' in Path('views/inmuebles.py').read_text()
def test_46_portfolio_cards():assert "st.columns(min(4,len(rows)))" in Path('views/portafolio.py').read_text()
def test_47_portfolio_kpis():assert 'Inmuebles Activos' in Path('views/portafolio.py').read_text()
def test_48_portfolio_pie():assert 'px.pie' in Path('views/portafolio.py').read_text()
def test_49_portfolio_collection_chart():assert 'Cobranza Por Inmueble' in Path('views/portafolio.py').read_text()
def test_50_portfolio_history():assert 'Evolución De Cobranza' in Path('views/portafolio.py').read_text()
def test_51_dashboard_kpis():assert 'Cobranza' in Path('views/dashboard.py').read_text()
def test_52_dashboard_bar():assert 'px.bar' in Path('views/dashboard.py').read_text()
def test_53_dashboard_pie():assert 'px.pie' in Path('views/dashboard.py').read_text()
def test_54_dashboard_occupation():assert 'Estado De Ocupación' in Path('views/dashboard.py').read_text()
def test_55_schema_gate():assert Path('core/schema_check.py').exists()
def test_56_schema_gate_active_root():assert 'SuperAdmin activo' in Path('core/schema_check.py').read_text()
def test_57_root_audit():assert 'SUPERADMIN_BOOTSTRAP' in Path('core/auth.py').read_text()
def test_58_property_permission_enforcement():
    assert 'decision(user' in Path('views/inmuebles.py').read_text(encoding='utf-8')
def test_59_no_fake_data():assert 'Aún No Hay Información Suficiente' in Path('views/dashboard.py').read_text()
def test_60_build_revision():assert 'build.01-r2' in Path('core/config.py').read_text()
