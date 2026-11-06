import streamlit as st
from core.config import PRODUCT_NAME,BUILD
from core.db import init_database
from core.auth import bootstrap_admin,require_login,logout
from core.access import select_property
from core.permissions import allowed
from core.schema_check import check
st.set_page_config(page_title=PRODUCT_NAME,page_icon='🏢',layout='wide');init_database();bootstrap_admin();issues=check()
if issues:st.error('Condo_Smart No Puede Iniciar');st.code('\n'.join(issues));st.stop()
require_login();u=st.session_state.user;st.sidebar.title('🏢 Condo_Smart');st.sidebar.caption(BUILD);select_property(u);P=[('🏠 Portafolio','portafolio','views.portafolio'),('📊 Dashboard','dashboard','views.dashboard'),('🏢 Inmuebles','inmuebles','views.inmuebles'),('🏬 Espacios','espacios','views.espacios'),('👥 Propietarios / Inquilinos','personas','views.personas'),('👤 Usuarios Y Accesos','usuarios','views.usuarios'),('⚙️ Catálogos','catalogos','views.catalogos'),('🛡️ Auditoría','auditoria','views.auditoria')];pages=[x for x in P if allowed(u,x[1])];lab=st.sidebar.radio('Navegación',[x[0] for x in pages]);st.sidebar.divider();st.sidebar.write(u['nombre']);
if st.sidebar.button('Cerrar Sesión'):logout()
module=next(x[2] for x in pages if x[0]==lab);__import__(module,fromlist=['render']).render()
