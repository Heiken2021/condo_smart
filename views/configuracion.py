import streamlit as st
from components.ui import title, clickable_image
from core.auth import audit
from services.media import validate
from services.system_settings import get_system_identity, get_setting, set_setting, update_system_logo, delete_system_logo
from views.performance_dashboard import render as render_performance
from components.processing_status import processing
from views.usuarios import render_embedded as render_users_access
from services.root_security import (
    grant_delegated_root,
    is_root_principal,
    list_root_candidates,
    list_roots,
    revoke_delegated_root,
)

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
            st.markdown("### Gobierno De Seguridad Root")

            if not is_root_principal(user):
                st.info(
                    "Tu cuenta dispone de acceso global como Root Delegado. "
                    "La asignación y revocación de privilegios Root está "
                    "reservada al Root Principal."
                )
            else:
                st.warning(
                    "Los privilegios Root conceden acceso global al sistema. "
                    "Asigna este nivel únicamente a usuarios autorizados."
                )

                roots = list_roots(user["id"])

                root_rows = [
                    {
                        "Usuario": item.get("username"),
                        "Nombre": item.get("nombre"),
                        "Correo": item.get("email"),
                        "Autoridad": item.get("autoridad_root"),
                        "Estado": "Activo" if item.get("activo") else "Inactivo",
                        "Asignado Por": item.get("asignado_por_username"),
                        "Asignado En": item.get("root_asignado_en"),
                    }
                    for item in roots
                ]

                st.markdown("#### Autoridades Root")

                if root_rows:
                    st.dataframe(
                        root_rows,
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("No se encontraron autoridades Root.")

                candidates = list_root_candidates(user["id"])

                st.markdown("#### Conceder Acceso Root Delegado")

                if not candidates:
                    st.info(
                        "No hay usuarios activos elegibles para recibir "
                        "privilegios Root."
                    )
                else:
                    candidate_map = {
                        (
                            f"{item['nombre']} · {item['username']}"
                            + (
                                f" · {item['email']}"
                                if item.get("email")
                                else ""
                            )
                        ): item
                        for item in candidates
                    }

                    selected_candidate_label = st.selectbox(
                        "Usuario Elegible",
                        list(candidate_map),
                        key="root_security_candidate",
                    )

                    selected_candidate = candidate_map[
                        selected_candidate_label
                    ]

                    confirmation = st.text_input(
                        "Escribe el nombre de usuario para confirmar",
                        key="root_security_grant_confirmation",
                    )

                    grant_confirmed = (
                        confirmation.strip()
                        == selected_candidate["username"]
                    )

                    if st.button(
                        "Conceder Acceso Root Delegado",
                        type="primary",
                        disabled=not grant_confirmed,
                        key="root_security_grant",
                    ):
                        before = {
                            "rol_global": "USUARIO",
                            "autoridad_root": None,
                        }

                        try:
                            granted = grant_delegated_root(
                                selected_candidate["id"],
                                user["id"],
                            )

                            audit(
                                "ROOT_DELEGADO_ASIGNAR",
                                "usuarios",
                                selected_candidate["id"],
                                detail=(
                                    "Acceso Root Delegado autorizado "
                                    "por Root Principal"
                                ),
                                before=before,
                                after={
                                    "rol_global": granted.get("rol_global"),
                                    "autoridad_root": granted.get(
                                        "autoridad_root"
                                    ),
                                    "root_asignado_por": user["id"],
                                },
                                module="SEGURIDAD",
                            )

                            st.success(
                                "El acceso Root Delegado fue concedido "
                                "correctamente."
                            )
                            st.rerun()

                        except (PermissionError, ValueError, RuntimeError) as exc:
                            audit(
                                "ROOT_PRIVILEGE_DENIED",
                                "usuarios",
                                selected_candidate["id"],
                                detail=str(exc),
                                result="DENEGADO",
                                module="SEGURIDAD",
                            )
                            st.error(
                                "No fue posible conceder el privilegio Root: "
                                f"{exc}"
                            )

                delegated = [
                    item
                    for item in roots
                    if item.get("autoridad_root") == "DELEGADO"
                    and item.get("activo")
                ]

                st.markdown("#### Revocar Acceso Root Delegado")

                if not delegated:
                    st.info("No hay Root Delegados activos para revocar.")
                else:
                    delegate_map = {
                        (
                            f"{item['nombre']} · {item['username']}"
                            + (
                                f" · {item['email']}"
                                if item.get("email")
                                else ""
                            )
                        ): item
                        for item in delegated
                    }

                    selected_delegate_label = st.selectbox(
                        "Root Delegado",
                        list(delegate_map),
                        key="root_security_delegate",
                    )

                    selected_delegate = delegate_map[
                        selected_delegate_label
                    ]

                    revoke_confirmation = st.text_input(
                        "Escribe REVOKE seguido del usuario",
                        key="root_security_revoke_confirmation",
                        help=(
                            "Ejemplo: REVOKE usuario"
                        ),
                    )

                    expected_confirmation = (
                        f"REVOKE {selected_delegate['username']}"
                    )

                    revoke_confirmed = (
                        revoke_confirmation.strip()
                        == expected_confirmation
                    )

                    if st.button(
                        "Revocar Acceso Root Delegado",
                        disabled=not revoke_confirmed,
                        key="root_security_revoke",
                    ):
                        before = {
                            "rol_global": selected_delegate.get("rol_global"),
                            "autoridad_root": selected_delegate.get(
                                "autoridad_root"
                            ),
                        }

                        try:
                            revoked = revoke_delegated_root(
                                selected_delegate["id"],
                                user["id"],
                            )

                            audit(
                                "ROOT_DELEGADO_REVOCAR",
                                "usuarios",
                                selected_delegate["id"],
                                detail=(
                                    "Acceso Root Delegado revocado "
                                    "por Root Principal"
                                ),
                                before=before,
                                after={
                                    "rol_global": revoked.get("rol_global"),
                                    "autoridad_root": revoked.get(
                                        "autoridad_root"
                                    ),
                                    "root_revocado_por": user["id"],
                                },
                                module="SEGURIDAD",
                            )

                            st.success(
                                "El acceso Root Delegado fue revocado "
                                "correctamente."
                            )
                            st.rerun()

                        except (PermissionError, ValueError, RuntimeError) as exc:
                            action = (
                                "ROOT_PRINCIPAL_PROTECTED"
                                if str(exc) == "ROOT_PRINCIPAL_PROTECTED"
                                else "ROOT_PRIVILEGE_DENIED"
                            )

                            audit(
                                action,
                                "usuarios",
                                selected_delegate["id"],
                                detail=str(exc),
                                result="DENEGADO",
                                module="SEGURIDAD",
                            )

                            st.error(
                                "No fue posible revocar el privilegio Root: "
                                f"{exc}"
                            )
    if users_tab.open:
        with users_tab:
            render_users_access()
    if performance_tab.open:
        with performance_tab:
            render_performance()
