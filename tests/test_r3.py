from pathlib import Path

def text(path): return Path(path).read_text(encoding='utf-8')

def test_r3_migration_exists(): assert Path('database/migrations/003_general_settings_r3.sql').exists()
def test_global_settings_schema():
    s=text('database/migrations/003_general_settings_r3.sql');assert 'configuracion_sistema' in s and 'identidad_sistema' in s
def test_system_settings_service():
    s=text('services/system_settings.py');
    for name in ['get_system_identity','update_system_logo','delete_system_logo','set_setting']: assert name in s
def test_config_view_exists(): assert Path('views/configuracion.py').exists()
def test_config_has_internal_root_gate(): assert "rol_global') != 'SUPERADMIN'" in text('views/configuracion.py')
def test_menu_hides_config_from_non_root(): assert "{'configuracion','catalogos','auditoria'}" in text('core/permissions.py')
def test_global_logo_abc():
    s=text('views/configuracion.py')
    for action in ['SYSTEM_LOGO_ALTA','SYSTEM_LOGO_CAMBIO','SYSTEM_LOGO_BAJA']: assert action in s
def test_property_branding_abc():
    s=text('views/inmuebles.py')
    for action in ['INMUEBLE_LOGO_ALTA','INMUEBLE_LOGO_CAMBIO','INMUEBLE_LOGO_BAJA','INMUEBLE_PORTADA_ALTA','INMUEBLE_PORTADA_CAMBIO','INMUEBLE_PORTADA_BAJA']: assert action in s
def test_property_refresh(): assert 'refresh_current_property' in text('views/inmuebles.py')
def test_portfolio_compact_clickable_image():
    s=text('views/portafolio.py');assert 'clickable_image' in s and 'width=140' in s and 'max_height=90' in s
def test_finance_placeholder():
    s=text('views/finanzas.py');assert 'Módulo reservado' in s
def test_r3_schema_gate():
    s=text('core/schema_check.py');assert 'configuracion_sistema' in s and 'identidad_sistema' in s
