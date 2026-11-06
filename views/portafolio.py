import pandas as pd,plotly.express as px,streamlit as st
from components.ui import title,metrics,datauri
from core.formatting import money
from services.analytics import prop_rows,periods
def render():
 title('Portafolio De Inmuebles','Vista Ejecutiva Consolidada');rows=prop_rows();spaces=sum(int(x['espacios']) for x in rows);charges=sum(float(x['cargos']) for x in rows);paid=sum(float(x['pagos']) for x in rows);metrics([('Inmuebles Activos',sum(bool(x['activo']) for x in rows)),('Espacios',spaces),('Cargos',money(charges)),('Cobrado',money(paid)),('Pendiente',money(max(charges-paid,0)))])
 if not rows:st.info('Sin Inmuebles');return
 cols=st.columns(min(4,len(rows)))
 for i,x in enumerate(rows):
  with cols[i%len(cols)]:
   if x.get('portada_data'):st.image(x['portada_data'],use_container_width=True)
   st.subheader(x['nombre']);st.caption((x.get('tipo_codigo') or '')+' · '+(x.get('direccion') or ''))
   rate=round(100*float(x['pagos'])/float(x['cargos']),1) if float(x['cargos']) else 0;st.write(f"{x['espacios']} Espacios · {x['administradores']} Administradores");st.progress(min(rate/100,1),text=f'Cobranza {rate}%')
 d=pd.DataFrame(rows);c1,c2=st.columns(2)
 with c1:
  st.subheader('Distribución Por Tipo De Inmueble');fig=px.pie(d,names='tipo_codigo',values='espacios',hole=.5);st.plotly_chart(fig,use_container_width=True)
 with c2:
  st.subheader('Cobranza Por Inmueble');d['cobranza_pct']=[round(100*float(r.pagos)/float(r.cargos),1) if float(r.cargos) else 0 for _,r in d.iterrows()];fig=px.bar(d,x='cobranza_pct',y='nombre',orientation='h',range_x=[0,100]);st.plotly_chart(fig,use_container_width=True)
 p=pd.DataFrame(periods());st.subheader('Evolución De Cobranza')
 if len(p):st.plotly_chart(px.bar(p,x='periodo',y=['cargos','pagos'],barmode='group'),use_container_width=True)
 else:st.info('Aún No Hay Información Suficiente Para Esta Visualización')
