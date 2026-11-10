from core.db import fetch_all
from core.access import cid
from components.ui import title,table

def render_embedded():
    pid=cid()
    if not pid:
        import streamlit as st
        st.info('Selecciona un inmueble activo para consultar Usuarios Y Accesos.')
        return
    table(fetch_all('SELECT u.username,u.nombre,u.email,ui.rol_codigo,u.activo FROM usuarios u JOIN usuario_inmuebles ui ON ui.usuario_id=u.id WHERE ui.condominio_id=%s',(pid,)),'usuarios',['username','nombre','email','rol_codigo','activo'])

def render():
    title('Usuarios Y Accesos','Módulo Preservado Para Build 04')
    render_embedded()
