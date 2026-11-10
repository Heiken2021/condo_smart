from contextlib import contextmanager
import streamlit as st

@contextmanager
def processing(label='Procesando solicitud...'):
    status=st.status(label,expanded=False,state='running')
    try:
        yield status
    except Exception:
        status.update(label='No fue posible completar el proceso.',state='error',expanded=True)
        raise
    else:
        status.update(label='Proceso completado.',state='complete',expanded=False)
