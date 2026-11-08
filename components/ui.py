import base64,html
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from core.formatting import labels,state

def title(t,s=''):
    st.title(t)
    if s:st.caption(s)
def table(rows,entity,visible):
    d=pd.DataFrame(rows or [])
    if d.empty:st.info('Sin Registros');return d
    d=d[[c for c in visible if c in d.columns]]
    if 'activo' in d.columns:d['activo']=d['activo'].map(state)
    d=d.rename(columns=labels(entity));st.dataframe(d,hide_index=True,use_container_width=True);return d
def metrics(items):
    for col,(name,value) in zip(st.columns(len(items)),items):col.metric(name,value)
def _datauri(data,mime='image/jpeg'):
    if not data:return ''
    return 'data:'+(mime or 'image/jpeg')+';base64,'+base64.b64encode(bytes(data)).decode()
def datauri(data,mime='image/jpeg'):return _datauri(data,mime)
def clickable_image(data,mime,alt,width=220,max_height=None):
    if not data:return
    uri=_datauri(data,mime); safe=html.escape(alt or 'Imagen'); mh=f'max-height:{int(max_height)}px;' if max_height else ''
    doc=f'''<!doctype html><html><head><style>body{{margin:0;background:transparent;font-family:Arial,sans-serif}}.thumb{{max-width:{int(width)}px;width:auto;height:auto;{mh}object-fit:contain;border-radius:10px;border:1px solid #E1E6EF;box-shadow:0 2px 8px rgba(17,34,68,.08);cursor:zoom-in;display:block}}dialog{{border:0;border-radius:14px;padding:12px;max-width:95vw;background:white;box-shadow:0 18px 60px rgba(0,0,0,.3)}}dialog::backdrop{{background:rgba(4,22,40,.72)}}dialog img{{max-width:90vw;max-height:78vh;width:auto;height:auto;object-fit:contain;display:block}}button{{position:absolute;right:16px;top:16px;border:0;border-radius:50%;width:34px;height:34px;background:#082F5B;color:#fff;font-size:20px;cursor:pointer}}</style></head><body><img class="thumb" src="{uri}" alt="{safe}" onclick="document.getElementById('dlg').showModal()"><dialog id="dlg"><button onclick="document.getElementById('dlg').close()">×</button><img src="{uri}" alt="{safe}"></dialog></body></html>'''
    components.html(doc,height=(int(max_height) if max_height else int(width))+8,scrolling=False)
def property_header(p):
    if not p:return
    st.markdown('---');left,center,right=st.columns([1,2.7,1.5],vertical_alignment='center')
    with left:
        if p.get('logo_data'):clickable_image(p['logo_data'],p.get('logo_mime') or 'image/png',f"Logotipo - {p.get('nombre','Inmueble')}",width=120,max_height=90)
    with center:
        st.subheader(p.get('nombre',''));details=[p.get('tipo_codigo'),p.get('direccion'),p.get('moneda_base')];st.caption(' · '.join(str(v) for v in details if v))
    with right:
        if p.get('portada_data'):clickable_image(p['portada_data'],p.get('portada_mime') or 'image/jpeg',f"Portada - {p.get('nombre','Inmueble')}",width=220,max_height=125)
