import json,streamlit as st
from core.db import execute,fetch_one
from core.security import hash_password,verify_password
from core.config import secret
def audit(action,entity=None,entity_id=None,detail=None,before=None,after=None,result='OK'):
 u=st.session_state.get('user',{});execute('INSERT INTO auditoria(condominio_id,usuario_id,username,accion,entidad,entidad_id,detalle,valor_anterior,valor_nuevo,resultado) VALUES(%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s)',(st.session_state.get('condominio_id'),u.get('id'),u.get('username','sistema'),action,entity,entity_id,detail,json.dumps(before,default=str) if before else None,json.dumps(after,default=str) if after else None,result))
def bootstrap_admin():
 c=fetch_one('SELECT id FROM condominios ORDER BY id LIMIT 1')
 if not c:c=execute("INSERT INTO condominios(clave,nombre,tipo_codigo) VALUES('PRINCIPAL','Inmueble Principal','VERTICAL') RETURNING id",returning=True)
 u=fetch_one("SELECT id FROM usuarios WHERE username='admin'")
 if not u and secret('ADMIN_INITIAL_PASSWORD'):
  s,h=hash_password(secret('ADMIN_INITIAL_PASSWORD'));u=execute("INSERT INTO usuarios(username,nombre,rol_global,salt,password_hash,debe_cambiar_password) VALUES('admin','Administrador Root','SUPERADMIN',%s,%s,FALSE) RETURNING id",(s,h),True);audit('SUPERADMIN_BOOTSTRAP','usuarios',u['id'])
def login():
 st.title('🏢 Condo_Smart');st.caption('Gobierno Multi-Inmueble')
 with st.form('login'):username=st.text_input('Usuario');password=st.text_input('Contraseña',type='password');ok=st.form_submit_button('Iniciar Sesión',type='primary',use_container_width=True)
 if ok:
  u=fetch_one('SELECT * FROM usuarios WHERE username=%s AND activo=TRUE',(username.strip(),))
  if u and verify_password(password,u['salt'],u['password_hash']):execute('UPDATE usuarios SET ultimo_acceso=NOW(),intentos_fallidos=0 WHERE id=%s',(u['id'],));st.session_state.user=dict(u);audit('LOGIN');st.rerun()
  st.error('Credenciales Incorrectas')
def require_login():
 if 'user' not in st.session_state:login();st.stop()
def logout():audit('LOGOUT');st.session_state.clear();st.rerun()
