import pandas as pd,plotly.express as px,streamlit as st
from components.ui import title,metrics,property_header
from core.access import cid
from core.formatting import money
from services.analytics import kpis,periods,expense_categories,occupation
def render():
 p=st.session_state.get('condominio',{});title('Dashboard',p.get('nombre','Inmueble Activo'));property_header(p);x=kpis(cid());rate=round(100*float(x['pagos'])/float(x['cargos']),1) if float(x['cargos']) else 0;metrics([('Cargos',money(x['cargos'])),('Cobrado',money(x['pagos'])),('Pendiente',money(x['pendiente'])),('Gastos',money(x['gastos'])),('Saldo',money(x['saldo'])),('Cobranza',f'{rate}%')]);c1,c2=st.columns(2);d=pd.DataFrame(periods(cid()));e=pd.DataFrame(expense_categories(cid()))
 with c1:
  st.subheader('Cargos Vs Pagos');st.plotly_chart(px.bar(d,x='periodo',y=['cargos','pagos'],barmode='group'),use_container_width=True) if len(d) else st.info('Aún No Hay Información Suficiente')
 with c2:
  st.subheader('Gastos Por Categoría');st.plotly_chart(px.pie(e,names='categoria_codigo',values='total',hole=.5),use_container_width=True) if len(e) else st.info('Aún No Hay Información Suficiente')
 o=pd.DataFrame(occupation(cid()));st.subheader('Estado De Ocupación');st.plotly_chart(px.bar(o,x='estado',y='total'),use_container_width=True) if len(o) else st.info('Aún No Hay Información Suficiente')
