from pathlib import Path

def read(p):return Path(p).read_text(encoding='utf-8')
def test_r31_version(): assert 'r3.1-visual' in read('core/config.py')
def test_brand_tokens():
 s=read('components/brand.py')
 for c in ['#082F5B','#0878C9','#22C8C8','#20AA58','#54D65C']:assert c in s
def test_login_is_centered_compact():
 s=read('core/auth.py');assert 'st.columns([1.2,1,1.2])' in s
def test_login_uses_system_logo():
 s=read('core/auth.py');assert 'get_system_identity' in s and 'max_width=380' in s
def test_sidebar_logo_contain_no_crop():
 s=read('components/brand.py');assert 'object-fit:contain' in s
def test_no_duplicate_sidebar_legend():
 s=read('app.py');assert "sidebar.title" not in s and "Gobierno Multi-Inmueble" not in s
def test_click_image_dialog():
 s=read('components/ui.py');assert 'showModal()' in s and '<dialog id="dlg">' in s
def test_custom_icon_library():
 s=read('components/brand.py')
 for k in ['portafolio','dashboard','inmuebles','espacios','personas','usuarios','finanzas','catalogos','configuracion','auditoria']:assert f'"{k}"' in s
def test_menu_has_no_os_emoji():
 s=read('app.py'); assert "('🏠" not in s and "('📊" not in s and "('🏢" not in s
def test_brand_readme():assert Path('assets/brand/README.md').exists()
