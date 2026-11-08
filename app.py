import streamlit as st
from core.config import PRODUCT_NAME,BUILD
from core.db import init_database
from core.auth import bootstrap_admin,require_login,logout
from core.access import select_property
from core.permissions import allowed
from core.schema_check import check
from components.brand import inject_theme,logo,sidebar_nav
from services.system_settings import get_system_identity
st.set_page_config(page_title=PRODUCT_NAME,page_icon='🏢',layout='wide');inject_theme();init_database();bootstrap_admin();issues=check()
if issues:st.error('Condo_Smart No Puede Iniciar');st.code('\n'.join(issues));st.stop()
require_login();u=st.session_state.user;identity=get_system_identity()
with st.sidebar:
 if identity.get('logo_data'):logo(identity['logo_data'],identity.get('logo_mime') or 'image/png',max_width=245,max_height=180,alt='Condo-Smart')
 st.caption(BUILD)
select_property(u)
P=[('Portafolio','portafolio','views.portafolio'),('Dashboard','dashboard','views.dashboard'),('Inmuebles','inmuebles','views.inmuebles'),('Espacios','espacios','views.espacios'),('Propietarios / Inquilinos','personas','views.personas'),('Usuarios Y Accesos','usuarios','views.usuarios'),('Finanzas','finanzas','views.finanzas'),('Catálogos','catalogos','views.catalogos'),('Configuración General','configuracion','views.configuracion'),('Auditoría','auditoria','views.auditoria')]
pages=[x for x in P if allowed(u,x[1])];valid={x[1] for x in pages};nav=st.session_state.get('cs_nav',pages[0][1]);nav=nav if nav in valid else pages[0][1];selected=sidebar_nav(pages,nav,u);
if selected != nav: st.session_state.cs_nav=selected;st.rerun()
nav=st.session_state.get('cs_nav',nav)
if st.sidebar.button('Cerrar Sesión',use_container_width=True):logout()
module=next(x[2] for x in pages if x[1]==nav);__import__(module,fromlist=['render']).render()
