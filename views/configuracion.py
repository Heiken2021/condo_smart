import streamlit as st
from components.ui import title, clickable_image
from core.auth import audit
from services.media import validate
from services.system_settings import get_system_identity, get_setting, set_setting, update_system_logo, delete_system_logo
from views.performance_dashboard import render as render_performance
from components.processing_status import processing
from views.usuarios import render_embedded as render_users_access

def _require_superadmin():
    user = st.session_state.get('user') or {}
    if user.get('rol_global') != 'SUPERADMIN':
        st.error('Acceso denegado. Esta función está reservada al Administrador Global.')
        st.stop()
    return user

def render():
    user = _require_superadmin()
    title('Configuración General', 'Parámetros globales e identidad de Condo-Smart')
    tabs = st.tabs(
        ['Identidad Del Sistema', 'Parámetros Generales', 'Seguridad', 'Usuarios Y Accesos', 'Rendimiento'],
        key='configuration_tabs',
        on_change='rerun',
    )
    identity_tab, settings_tab, security_tab, users_tab, performance_tab = tabs
    if identity_tab.open:
        with identity_tab:
            identity = get_system_identity()
            logo_width = int(get_setting('SYSTEM_LOGO_WIDTH', '180'))
            logo_height = int(get_setting('SYSTEM_LOGO_MAX_HEIGHT', '110'))
            logo_offset = int(get_setting('SYSTEM_LOGO_OFFSET_Y', '-10'))
            menu_offset = int(get_setting('SYSTEM_MENU_OFFSET_Y', '-8'))
            if identity.get('logo_data'):
                clickable_image(identity['logo_data'], identity.get('logo_mime') or 'image/png', 'Logo Condo-Smart', width=logo_width, max_height=logo_height)
            st.markdown('#### Ajuste De Logo Y Menú')
            with st.form('system_brand_layout'):
                a,b=st.columns(2)
                new_width=a.number_input('Ancho Del Logo (px)',min_value=80,max_value=420,value=logo_width,step=5)
                new_height=b.number_input('Alto Máximo Del Logo (px)',min_value=60,max_value=320,value=logo_height,step=5)
                c1,c2=st.columns(2)
                new_logo_offset=c1.number_input('Posición Vertical Del Logo (px)',min_value=-80,max_value=80,value=logo_offset,step=2,help='Valores negativos mueven el logo hacia arriba.')
                new_menu_offset=c2.number_input('Posición Vertical Del Menú (px)',min_value=-80,max_value=80,value=menu_offset,step=2,help='Valores negativos mueven el menú hacia arriba.')
                save_layout=st.form_submit_button('Guardar Ajustes De Presentación',type='primary')
            if save_layout:
                before={'SYSTEM_LOGO_WIDTH':str(logo_width),'SYSTEM_LOGO_MAX_HEIGHT':str(logo_height),'SYSTEM_LOGO_OFFSET_Y':str(logo_offset),'SYSTEM_MENU_OFFSET_Y':str(menu_offset)}
                set_setting('SYSTEM_LOGO_WIDTH',str(int(new_width)),user['id'],'NUMERO','Ancho del logo principal en pixeles')
                set_setting('SYSTEM_LOGO_MAX_HEIGHT',str(int(new_height)),user['id'],'NUMERO','Alto maximo del logo principal en pixeles')
                set_setting('SYSTEM_LOGO_OFFSET_Y',str(int(new_logo_offset)),user['id'],'NUMERO','Desplazamiento vertical del logo principal')
                set_setting('SYSTEM_MENU_OFFSET_Y',str(int(new_menu_offset)),user['id'],'NUMERO','Desplazamiento vertical del menu principal')
                audit('CONFIGURACION_BRAND_LAYOUT','configuracion_sistema',detail='Logo y menu',before=before,after={'SYSTEM_LOGO_WIDTH':new_width,'SYSTEM_LOGO_MAX_HEIGHT':new_height,'SYSTEM_LOGO_OFFSET_Y':new_logo_offset,'SYSTEM_MENU_OFFSET_Y':new_menu_offset})
                st.success('Ajustes visuales guardados correctamente.')
                st.rerun()
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
    if settings_tab.open:
        with settings_tab:
            with st.form('general_settings'):
                product_name = st.text_input('Nombre Del Producto', get_setting('PRODUCT_NAME', 'Condo_Smart'))
                currency = st.selectbox('Moneda Predeterminada', ['MXN','USD','EUR','CAD'], index=['MXN','USD','EUR','CAD'].index(get_setting('DEFAULT_CURRENCY','MXN')))
                timezone = st.text_input('Zona Horaria Predeterminada', get_setting('DEFAULT_TIMEZONE','America/Mexico_City'))
                submitted = st.form_submit_button('Guardar Parámetros', type='primary')
            if submitted:
                with processing("Guardando parámetros generales..."):
                    before = {
                        "PRODUCT_NAME": get_setting("PRODUCT_NAME"),
                        "DEFAULT_CURRENCY": get_setting("DEFAULT_CURRENCY"),
                        "DEFAULT_TIMEZONE": get_setting("DEFAULT_TIMEZONE"),
                    }
                    set_setting("PRODUCT_NAME", product_name.strip() or "Condo_Smart", user["id"])
                    set_setting("DEFAULT_CURRENCY", currency, user["id"])
                    set_setting("DEFAULT_TIMEZONE", timezone.strip() or "America/Mexico_City", user["id"])
                    audit(
                        "CONFIGURACION_GLOBAL_CAMBIO",
                        "configuracion_sistema",
                        detail="Parámetros generales",
                        before=before,
                        after={
                            "PRODUCT_NAME": product_name,
                            "DEFAULT_CURRENCY": currency,
                            "DEFAULT_TIMEZONE": timezone,
                        },
                    )
                    st.success("Parámetros guardados correctamente.")
                    st.rerun()

    if security_tab.open:
        with security_tab:
            st.info('Los parámetros de seguridad sensibles permanecen gobernados por el modelo central de autorización. Su administración se ampliará en un Build posterior.')
    if users_tab.open:
        with users_tab:
            render_users_access()
    if performance_tab.open:
        with performance_tab:
            render_performance()
