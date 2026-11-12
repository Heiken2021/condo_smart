import streamlit as st


def _require_superadmin():
    user = st.session_state.get("user") or {}

    if user.get("rol_global") != "SUPERADMIN":
        st.error(
            "Acceso denegado. Catálogos está reservado "
            "al Administrador Global."
        )
        st.stop()

    return user
from core.db import fetch_all,execute
from services.catalogs import auto_code,references
from components.ui import title,table
def render():
 _require_superadmin()
 title('Catálogos','Conceptos Sin IDs Técnicos');cats=fetch_all('SELECT * FROM catalogos WHERE activo=TRUE ORDER BY nombre');cm={x['nombre']:x for x in cats};name=st.selectbox('Catálogo',list(cm));cat=cm[name];rows=fetch_all('SELECT id,codigo,nombre,activo FROM catalogo_valores WHERE catalogo_id=%s ORDER BY nombre',(cat['id'],));table(rows,'catalogos',['nombre','activo']);tabs=st.tabs(['Alta','Cambio','Baja']);
 with tabs[0]:
  with st.form('cat_add'):concept=st.text_input('Concepto');ok=st.form_submit_button('Agregar')
  if ok and concept:execute('INSERT INTO catalogo_valores(catalogo_id,codigo,nombre) VALUES(%s,%s,%s)',(cat['id'],auto_code(concept),concept));st.rerun()
 labels={x['nombre']:x for x in rows}
 with tabs[1]:
  if labels:
   sel=st.selectbox('Concepto',list(labels),key='cat_e');r=labels[sel]
   with st.form('cat_edit'):concept=st.text_input('Concepto',value=r['nombre']);ok=st.form_submit_button('Guardar Cambio')
   if ok:execute('UPDATE catalogo_valores SET nombre=%s WHERE id=%s',(concept,r['id']));st.rerun()
 with tabs[2]:
  if labels:
   sel=st.selectbox('Concepto',list(labels),key='cat_d');r=labels[sel];n=references(cat['codigo'],r['codigo']);st.caption(f'Registros Asociados: {n}')
   if n==0 and st.button('Eliminar'):execute('DELETE FROM catalogo_valores WHERE id=%s',(r['id'],));st.rerun()
   elif n>0 and st.button('Desactivar'):execute('UPDATE catalogo_valores SET activo=FALSE WHERE id=%s',(r['id'],));st.rerun()
