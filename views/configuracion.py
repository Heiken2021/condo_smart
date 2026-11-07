import streamlit as st
from components.ui import title, clickable_image
from core.auth import audit
from services.media import validate
from services.system_settings import get_system_identity, get_setting, set_setting, update_system_logo, delete_system_logo

def _require_superadmin():
    user = st.session_state.get('user') or {}
    if user.get('rol_global') != 'SUPERADMIN':
        st.error('Acceso denegado. Esta función está reservada al Administrador Global.')
        st.stop()
    return user

def render():
    user = _require_superadmin()
    title('Configuración General', 'Parámetros globales e identidad de Condo-Smart')
    identity_tab, settings_tab, security_tab = st.tabs(['Identidad Del Sistema', 'Parámetros Generales', 'Seguridad'])
    with identity_tab:
        identity = get_system_identity()
        if identity.get('logo_data'):
            clickable_image(identity['logo_data'], identity.get('logo_mime') or 'image/png', 'Logo Condo-Smart', width=180, max_height=110)
        upload = st.file_uploader('Logo Del Sistema', type=['jpg','jpeg','png','bmp'])
        col1, col2 = st.columns(2)
        if col1.button('Guardar / Cambiar Logo', type='primary', disabled=upload is None):
            try:
                media = validate(upload, 2)
                action = 'SYSTEM_LOGO_CAMBIO' if identity.get('logo_data') else 'SYSTEM_LOGO_ALTA'
                update_system_logo(media['data'], media['mime'], user['id'])
                audit(action, 'identidad_sistema', 1, after={'mime': media['mime'], 'name': media['name']})
                st.success('Logo actualizado correctamente.')
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
        confirm = col2.checkbox('Confirmo eliminar el logo', key='confirm_system_logo_delete')
        if col2.button('Eliminar Logo', disabled=not (confirm and identity.get('logo_data'))):
            delete_system_logo(user['id'])
            audit('SYSTEM_LOGO_BAJA', 'identidad_sistema', 1)
            st.success('Logo eliminado correctamente.')
            st.rerun()
    with settings_tab:
        with st.form('general_settings'):
            product_name = st.text_input('Nombre Del Producto', get_setting('PRODUCT_NAME', 'Condo_Smart'))
            currency = st.selectbox('Moneda Predeterminada', ['MXN','USD','EUR','CAD'], index=['MXN','USD','EUR','CAD'].index(get_setting('DEFAULT_CURRENCY','MXN')))
            timezone = st.text_input('Zona Horaria Predeterminada', get_setting('DEFAULT_TIMEZONE','America/Mexico_City'))
            submitted = st.form_submit_button('Guardar Parámetros', type='primary')
        if submitted:
            before = {'PRODUCT_NAME': get_setting('PRODUCT_NAME'), 'DEFAULT_CURRENCY': get_setting('DEFAULT_CURRENCY'), 'DEFAULT_TIMEZONE': get_setting('DEFAULT_TIMEZONE')}
            set_setting('PRODUCT_NAME', product_name.strip() or 'Condo_Smart', user['id'])
            set_setting('DEFAULT_CURRENCY', currency, user['id'])
            set_setting('DEFAULT_TIMEZONE', timezone.strip() or 'America/Mexico_City', user['id'])
            audit('CONFIGURACION_GLOBAL_CAMBIO', 'configuracion_sistema', detail='Parámetros generales', before=before, after={'PRODUCT_NAME': product_name, 'DEFAULT_CURRENCY': currency, 'DEFAULT_TIMEZONE': timezone})
            st.success('Parámetros guardados correctamente.')
            st.rerun()
    with security_tab:
        st.info('Los parámetros de seguridad sensibles permanecen gobernados por el modelo central de autorización. Su administración se ampliará en un Build posterior.')
