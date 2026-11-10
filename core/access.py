import streamlit as st
from core.db import fetch_all, fetch_one

def authorized_properties(user, include_inactive=False):
    active = '' if include_inactive else ' AND c.activo=TRUE'
    if user.get('rol_global') == 'SUPERADMIN':
        return fetch_all('SELECT c.* FROM condominios c WHERE 1=1' + active + ' ORDER BY c.nombre')
    return fetch_all('SELECT DISTINCT c.* FROM condominios c JOIN usuario_inmuebles ui ON ui.condominio_id=c.id WHERE ui.usuario_id=%s AND ui.activo=TRUE' + active + ' ORDER BY c.nombre', (user['id'],))

def ensure_property_context(user):
    rows = authorized_properties(user)
    allowed_ids = {row['id'] for row in rows}
    selected_id = st.session_state.get('condominio_id')
    if selected_id not in allowed_ids:
        st.session_state.pop('condominio_id', None)
        st.session_state.pop('condominio', None)
        st.session_state.pop('inmueble_gestion_id', None)
        if user.get('rol_global') != 'SUPERADMIN' and len(rows) == 1:
            current = rows[0]
            st.session_state.condominio_id = current['id']
            st.session_state.condominio = dict(current)
            st.session_state.inmueble_gestion_id = current['id']
    return rows


def refresh_current_property(property_id=None, user=None):
    user = user or st.session_state.get('user') or {}
    property_id = property_id or st.session_state.get('condominio_id')
    if not property_id or not user:
        st.session_state.pop('condominio', None)
        return None
    if user.get('rol_global') == 'SUPERADMIN':
        row = fetch_one('SELECT * FROM condominios WHERE id=%s', (property_id,))
    else:
        row = fetch_one('SELECT c.* FROM condominios c JOIN usuario_inmuebles ui ON ui.condominio_id=c.id WHERE c.id=%s AND ui.usuario_id=%s AND ui.activo=TRUE', (property_id, user['id']))
    if row:
        st.session_state.condominio_id = row['id']
        st.session_state.condominio = dict(row)
        return st.session_state.condominio
    st.session_state.pop('condominio_id', None)
    st.session_state.pop('condominio', None)
    st.session_state.pop('inmueble_gestion_id', None)
    return None

def select_property(user):
    rows = authorized_properties(user)
    if not rows:
        st.sidebar.warning('Sin Inmuebles Asignados')
        st.session_state.pop('condominio_id', None)
        st.session_state.pop('condominio', None)
        st.session_state.pop('inmueble_gestion_id', None)
        return None

    allowed_ids = {x['id'] for x in rows}
    selected_id = st.session_state.get('condominio_id')

    # Never choose a property by default. The active context only exists after
    # the user selects a row in Inmuebles.
    if selected_id not in allowed_ids:
        st.session_state.pop('condominio_id', None)
        st.session_state.pop('condominio', None)
        # Keep inmueble_gestion_id: an offline property must remain manageable
        # from Inmuebles so it can be reactivated.
        st.sidebar.caption('Inmueble Activo')
        st.sidebar.markdown('''<div style="background:#EEF3F7;color:#61758A;border-radius:8px;padding:5px 10px;font-size:0.80rem;line-height:1.1;font-weight:700;margin:1px 0 2px 0;">Ninguno seleccionado</div>''', unsafe_allow_html=True)
        return None

    current = next(x for x in rows if x['id'] == selected_id)
    st.session_state.condominio_id = current['id']
    st.session_state.condominio = dict(current)
    st.session_state.inmueble_gestion_id = current['id']
    st.sidebar.caption('Inmueble Activo')
    st.sidebar.markdown(f'''<div style="background:#D9F5E5;color:#087D45;border-radius:11px;padding:12px 14px;font-weight:800;margin:4px 0 10px 0;">{current['nombre']}</div>''', unsafe_allow_html=True)
    return st.session_state.condominio

def cid():
    return st.session_state.get('condominio_id')
