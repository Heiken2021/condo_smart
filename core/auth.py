import json
import streamlit as st
from core.db import execute,fetch_one
from core.security import hash_password,verify_password
from core.config import secret


def audit(action,entity=None,entity_id=None,detail=None,before=None,after=None,result='OK'):
    u=st.session_state.get('user',{})
    execute('INSERT INTO auditoria(condominio_id,usuario_id,username,accion,entidad,entidad_id,detalle,valor_anterior,valor_nuevo,resultado) VALUES(%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s)',(st.session_state.get('condominio_id'),u.get('id'),u.get('username','sistema'),action,entity,entity_id,detail,json.dumps(before,default=str) if before else None,json.dumps(after,default=str) if after else None,result))


def bootstrap_admin():
    c=fetch_one('SELECT id FROM condominios ORDER BY id LIMIT 1')
    if not c: c=execute("INSERT INTO condominios(clave,nombre,tipo_codigo) VALUES('PRINCIPAL','Inmueble Principal','VERTICAL') RETURNING id",returning=True)
    u=fetch_one("SELECT id FROM usuarios WHERE username='admin'")
    if not u and secret('ADMIN_INITIAL_PASSWORD'):
        s,h=hash_password(secret('ADMIN_INITIAL_PASSWORD'))
        u=execute("INSERT INTO usuarios(username,nombre,rol_global,salt,password_hash,debe_cambiar_password) VALUES('admin','Administrador Root','SUPERADMIN',%s,%s,FALSE) RETURNING id",(s,h),True)
        audit('SUPERADMIN_BOOTSTRAP','usuarios',u['id'])


def _recovery_ui():
    from services.password_recovery import request_password_reset,reset_password_with_code
    st.markdown('#### Recuperar contraseña')
    email=st.text_input('Correo electrónico registrado',key='recovery_email')
    if st.button('Enviar código de recuperación',use_container_width=True,key='request_recovery'):
        try:
            st.info(request_password_reset(email))
            st.session_state.recovery_requested=True
        except RuntimeError as exc:
            if str(exc)=='SMTP_NOT_CONFIGURED': st.error('El servicio de correo todavía no está configurado. Contacta al administrador del sistema.')
            else: st.error('No fue posible procesar la recuperación en este momento.')
    if st.session_state.get('recovery_requested'):
        with st.form('confirm_password_recovery'):
            code=st.text_input('Código temporal')
            password=st.text_input('Nueva contraseña',type='password')
            confirmation=st.text_input('Confirmar nueva contraseña',type='password')
            ok=st.form_submit_button('Actualizar contraseña',type='primary',use_container_width=True)
        if ok:
            if password!=confirmation: st.error('Las contraseñas no coinciden.')
            else:
                try:
                    reset_password_with_code(email,code,password)
                    st.success('Contraseña actualizada. Ya puedes iniciar sesión.')
                    st.session_state.recovery_mode=False
                    st.session_state.recovery_requested=False
                except ValueError as exc:
                    st.error('El código no es válido o ha vencido.' if str(exc)=='INVALID_OR_EXPIRED_CODE' else 'Usa al menos 10 caracteres, una mayúscula y un número.')
    if st.button('Volver al inicio de sesión',use_container_width=True,key='back_login'):
        st.session_state.recovery_mode=False; st.rerun()


def login():
    from components.brand import inject_theme,logo
    from services.system_settings import get_system_identity
    inject_theme(); identity=get_system_identity()
    _,center,_=st.columns([1.2,1,1.2])
    with center:
        if identity.get('logo_data'): logo(identity['logo_data'],identity.get('logo_mime') or 'image/png',max_width=380,alt='Condo-Smart')
        else: st.markdown('<div class="cs-login-title">Condo-Smart</div>',unsafe_allow_html=True)
        st.markdown('<div class="cs-login-title">Bienvenido</div><div class="cs-login-sub">Ingresa a tu cuenta para continuar</div>',unsafe_allow_html=True)
        if st.session_state.get('recovery_mode'):
            _recovery_ui(); return
        with st.form('login'):
            username=st.text_input('Usuario',placeholder='Usuario')
            password=st.text_input('Contraseña',type='password',placeholder='Contraseña')
            ok=st.form_submit_button('Iniciar Sesión  →',type='primary',use_container_width=True)
        if st.button('¿Olvidaste tu contraseña?',use_container_width=True,key='open_recovery'):
            st.session_state.recovery_mode=True; st.rerun()
        st.markdown('<div class="cs-login-foot"><b>Condo-Smart</b><br>Residencias más conectadas, comunidades más fuertes</div>',unsafe_allow_html=True)
    if ok:
        u=fetch_one('SELECT * FROM usuarios WHERE username=%s AND activo=TRUE',(username.strip(),))
        if u and verify_password(password,u['salt'],u['password_hash']):
            execute('UPDATE usuarios SET ultimo_acceso=NOW(),intentos_fallidos=0 WHERE id=%s',(u['id'],)); st.session_state.user=dict(u); audit('LOGIN'); st.rerun()
        st.error('Credenciales Incorrectas')


def require_login():
    if 'user' not in st.session_state: login(); st.stop()


def logout(): audit('LOGOUT'); st.session_state.clear(); st.rerun()
