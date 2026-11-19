import streamlit as st
from core.config import PRODUCT_NAME,BUILD
from core.db import init_database
from core.auth import bootstrap_admin,require_login,logout
from core.access import select_property,authorized_properties,refresh_current_property,ensure_property_context
from core.permissions import allowed
from core.schema_check import check
from components.brand import inject_theme,logo,sidebar_nav
from services.system_settings import get_system_identity,get_setting
from services.performance import measure
st.set_page_config(page_title=PRODUCT_NAME,page_icon='🏢',layout='wide');inject_theme()

@st.cache_resource
def _bootstrap_runtime_once():
    init_database()
    bootstrap_admin()
    return tuple(check())

issues=_bootstrap_runtime_once()
if issues:st.error('Condo_Smart No Puede Iniciar');st.code('\n'.join(issues));st.stop()


@st.dialog("Inmueble requerido", dismissible=False)
def require_active_property_dialog():
    st.warning("No hay un inmueble activo.")
    st.write("Selecciona un inmueble para continuar.")
    if st.button("OK", type="primary", use_container_width=True):
        st.session_state.cs_nav = "inmuebles"
        st.session_state.pop("condominio_id", None)
        st.session_state.pop("condominio", None)
        st.rerun()

require_login();u=st.session_state.user;identity=get_system_identity()

current_nav_for_context=st.session_state.get('cs_nav','portafolio')
if current_nav_for_context!='auditoria':
  # Selector rapido global del inmueble activo.
  quick_properties=ensure_property_context(u)
  if quick_properties:
   quick_labels={f"{p.get('clave','')} · {p.get('nombre','Inmueble')}":p for p in quick_properties}
   no_property_label='Sin inmueble activo'
   quick_names=[no_property_label,*list(quick_labels)]
   active_id=st.session_state.get('condominio_id')
   active_label=next((label for label,p in quick_labels.items() if p['id']==active_id),None)
   quick_index=quick_names.index(active_label) if active_label in quick_names else 0
   expected_quick_label=active_label or no_property_label
   if st.session_state.get('quick_property_selector') != expected_quick_label:
    st.session_state.quick_property_selector=expected_quick_label

   def _clear_property_context():
    st.session_state.pop('condominio_id',None)
    st.session_state.pop('condominio',None)
    st.session_state.pop('inmueble_gestion_id',None)

   def _close_active_property():
    _clear_property_context()
    st.session_state.quick_property_selector=no_property_label

   def _change_quick_property():
    selected_label=st.session_state.get('quick_property_selector')
    if selected_label == no_property_label:
     _clear_property_context()
     return
    selected_property=quick_labels.get(selected_label)
    if not selected_property:
     return
    selected_id=selected_property['id']
    if selected_id==st.session_state.get('condominio_id'):
     return
    st.session_state.condominio_id=selected_id
    st.session_state.inmueble_gestion_id=selected_id
    refresh_current_property(selected_id)
    for state_key in (
     'spaces_search','spaces_type_filter','spaces_occupancy_filter',
     'spaces_status_filter','admin_gestion_id',
    ):
     st.session_state.pop(state_key,None)

   with st.container(key='quick_property_bar'):
    quick_cols=st.columns([1.1,3.2,1.55,4.15],vertical_alignment='center')
    quick_cols[0].markdown('**Inmueble activo**')
    quick_cols[1].selectbox(
     'Selección rápida de inmueble',
     quick_names,
     index=quick_index,
     label_visibility='collapsed',
     key='quick_property_selector',
     on_change=_change_quick_property,
    )
    quick_cols[2].button(
     'Cerrar inmueble',
     key='close_active_property',
     disabled=not bool(active_id),
     help='Cierra el contexto del inmueble activo. No elimina ni modifica el inmueble.',
     use_container_width=True,
     on_click=_close_active_property,
    )


st.markdown("""<style>
.st-key-quick_property_bar {position:relative;top:-2.65rem;margin-bottom:-2.25rem;}
</style>""", unsafe_allow_html=True)

with st.sidebar:
 if identity.get('logo_data'):
  sidebar_logo_width=int(get_setting('SYSTEM_LOGO_WIDTH','245'))
  sidebar_logo_height=int(get_setting('SYSTEM_LOGO_MAX_HEIGHT','180'))
  logo(identity['logo_data'],identity.get('logo_mime') or 'image/png',max_width=sidebar_logo_width,max_height=sidebar_logo_height,alt='Condo-Smart')
 st.caption(BUILD)
P=[('Portafolio','portafolio','views.portafolio'),('Dashboard','dashboard','views.dashboard'),('Inmuebles','inmuebles','views.inmuebles'),('Espacios','espacios','views.espacios'),('Propietarios / Inquilinos','personas','views.personas'),('Finanzas','finanzas','views.finanzas'),('Reportes','reportes','views.reportes'),('Catálogos','catalogos','views.catalogos'),('Notificaciones','notificaciones','views.notificaciones'),('Auditoría','auditoria','views.auditoria'),('Configuración General','configuracion','views.configuracion'),('Soporte','soporte','views.soporte')]
pages=[x for x in P if allowed(u,x[1])];valid={x[1] for x in pages};nav=st.session_state.get('cs_nav',pages[0][1]);nav=nav if nav in valid else pages[0][1]

# Build 035: buscador global gobernado. El índice nace exclusivamente de las
# páginas ya filtradas por allowed(), por lo que nunca descubre módulos ocultos.
SEARCH_TERMS={
 'portafolio':'portafolio cartera inmuebles gestión global resumen',
 'dashboard':'dashboard indicadores kpi resumen métricas',
 'inmuebles':'inmuebles propiedades estructuras áreas comunes planos servicios administradores',
 'espacios':'espacios casas locales departamentos unidades',
 'personas':'propietarios inquilinos ocupantes personas residentes',
 'finanzas':'finanzas gobierno financiero reglas cuotas obligaciones pagos cargos gastos estado prioridad vigencia versiones excepciones',
 'reportes':'reportes informes exportación',
 'catalogos':'catálogos conceptos códigos valores',
 'notificaciones':'notificaciones avisos alertas mensajes',
 'auditoria':'auditoría actividad sistema financiera incidentes trazabilidad',
 'configuracion':'configuración general usuarios accesos seguridad rendimiento',
 'soporte':'soporte ayuda asistencia',
}
def _open_global_search_result(target_key):
 st.session_state.cs_nav=target_key
 st.session_state.cs_global_search=''

search_query=st.sidebar.text_input(
 'Buscar en Condo_Smart',
 key='cs_global_search',
 placeholder='Módulo, sección o función...',
 help='Busca únicamente dentro de las secciones autorizadas para tu perfil.',
)
if search_query.strip():
 query=' '.join(search_query.casefold().split())
 results=[]
 for label,key,module in pages:
  haystack=f"{label} {key} {SEARCH_TERMS.get(key,'')}".casefold()
  if all(token in haystack for token in query.split()):
   results.append((label,key,module))
 if results:
  st.sidebar.caption(f'Resultados: {len(results)}')
  for label,key,module in results[:8]:
   st.sidebar.button(
    f'Ir a {label}',
    key=f'cs_search_{key}',
    use_container_width=True,
    on_click=_open_global_search_result,
    args=(key,),
   )
 else:
  st.sidebar.caption('Sin resultados dentro de tus secciones autorizadas.')

select_property(u)
PROPERTY_REQUIRED={x[1] for x in pages if x[1] not in {'portafolio','inmuebles','finanzas','configuracion','reportes','notificaciones','auditoria','soporte'}}
if nav in PROPERTY_REQUIRED and not st.session_state.get('condominio_id'):
 require_active_property_dialog()
 st.stop()
selected=sidebar_nav(pages,nav,u);
if selected != nav: st.session_state.cs_nav=selected;st.rerun()
nav=st.session_state.get('cs_nav',nav)
if st.sidebar.button('Cerrar Sesión',use_container_width=True):logout()
module=next(x[2] for x in pages if x[1]==nav)
module_status=st.status(f'Cargando módulo: {next(x[0] for x in pages if x[1]==nav)}...',expanded=False,state='running')
try:
 with measure(nav,'module_render',st.session_state.get('condominio_id'),{'module_path':module}):
  __import__(module,fromlist=['render']).render()
except Exception:
 module_status.update(label='No fue posible completar el procesamiento del módulo.',state='error',expanded=True)
 raise
else:
 module_status.update(label='Módulo procesado correctamente.',state='complete',expanded=False)
