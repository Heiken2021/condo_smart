import streamlit as st
from core.db import fetch_all, fetch_one

def authorized_properties(user, include_inactive=False):
    active = '' if include_inactive else ' AND c.activo=TRUE'
    if user.get('rol_global') == 'SUPERADMIN':
        return fetch_all('SELECT c.* FROM condominios c WHERE 1=1' + active + ' ORDER BY c.nombre')
    return fetch_all('SELECT DISTINCT c.* FROM condominios c JOIN usuario_inmuebles ui ON ui.condominio_id=c.id WHERE ui.usuario_id=%s AND ui.activo=TRUE' + active + ' ORDER BY c.nombre', (user['id'],))

def refresh_current_property(property_id=None):
    property_id = property_id or st.session_state.get('condominio_id')
    if not property_id:
        st.session_state.pop('condominio', None)
        return None
    row = fetch_one('SELECT * FROM condominios WHERE id=%s', (property_id,))
    if row:
        st.session_state.condominio_id = row['id']
        st.session_state.condominio = dict(row)
        return st.session_state.condominio
    st.session_state.pop('condominio', None)
    return None

def select_property(user):
    rows = authorized_properties(user)
    if not rows:
        st.sidebar.warning('Sin Inmuebles Asignados')
        return None
    names = {x['nombre']: x for x in rows}
    if st.session_state.get('condominio_id') not in {x['id'] for x in rows}:
        st.session_state.condominio_id = rows[0]['id']
    current = next(x['nombre'] for x in rows if x['id'] == st.session_state.condominio_id)
    name = st.sidebar.selectbox('Inmueble Activo', list(names), index=list(names).index(current))
    st.session_state.condominio_id = names[name]['id']
    st.session_state.condominio = dict(names[name])
    return st.session_state.condominio

def cid():
    return st.session_state.get('condominio_id')
