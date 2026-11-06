import base64
import html
import pandas as pd
import streamlit as st
from core.formatting import labels, state


def title(t, s=''):
    st.title(t)
    if s:
        st.caption(s)


def table(rows, entity, visible):
    d = pd.DataFrame(rows or [])
    if d.empty:
        st.info('Sin Registros')
        return d
    d = d[[c for c in visible if c in d.columns]]
    if 'activo' in d.columns:
        d['activo'] = d['activo'].map(state)
    d = d.rename(columns=labels(entity))
    st.dataframe(d, hide_index=True, use_container_width=True)
    return d


def metrics(items):
    for col, (name, value) in zip(st.columns(len(items)), items):
        col.metric(name, value)


def _datauri(data, mime='image/jpeg'):
    if not data:
        return ''
    return 'data:' + (mime or 'image/jpeg') + ';base64,' + base64.b64encode(bytes(data)).decode()


def datauri(data, mime='image/jpeg'):
    """Backward-compatible public data URI helper used by portfolio."""
    return _datauri(data, mime)


def _clickable_image(data, mime, alt, width=220, max_height=None):
    """Small preview that opens the original image in a new browser tab."""
    if not data:
        return
    uri = _datauri(data, mime)
    height_style = f'max-height:{int(max_height)}px;' if max_height else ''
    safe_alt = html.escape(alt or 'Imagen del inmueble')
    st.markdown(
        f'''<a href="{uri}" target="_blank" title="Abrir imagen en tamaño completo">
        <img src="{uri}" alt="{safe_alt}" style="width:{int(width)}px;{height_style}object-fit:cover;border-radius:10px;border:1px solid #E1E6EF;box-shadow:0 2px 8px rgba(17,34,68,.08);cursor:zoom-in;" />
        </a>''',
        unsafe_allow_html=True,
    )
    st.caption('Haz clic en la imagen para verla en tamaño completo.')


def property_header(p):
    if not p:
        return
    st.markdown('---')
    left, center, right = st.columns([1, 2.7, 1.5], vertical_alignment='center')
    with left:
        if p.get('logo_data'):
            _clickable_image(
                p['logo_data'],
                p.get('logo_mime') or 'image/png',
                f"Logotipo - {p.get('nombre', 'Inmueble')}",
                width=120,
                max_height=90,
            )
    with center:
        st.subheader(p.get('nombre', ''))
        details = [p.get('tipo_codigo'), p.get('direccion'), p.get('moneda_base')]
        st.caption(' · '.join(str(v) for v in details if v))
    with right:
        if p.get('portada_data'):
            _clickable_image(
                p['portada_data'],
                p.get('portada_mime') or 'image/jpeg',
                f"Portada - {p.get('nombre', 'Inmueble')}",
                width=220,
                max_height=125,
            )
