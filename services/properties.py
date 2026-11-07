from core.db import fetch_all, fetch_one, execute

def list_properties():
    return fetch_all('SELECT id,clave,nombre,tipo_codigo,direccion,rfc,moneda_base,zona_horaria,activo,logo_data,logo_mime,portada_data,portada_mime FROM condominios ORDER BY nombre')

def get_property(pid):
    return fetch_one('SELECT * FROM condominios WHERE id=%s', (pid,))

def update_logo(pid, data, mime):
    execute('UPDATE condominios SET logo_data=%s,logo_mime=%s,actualizado_en=NOW() WHERE id=%s', (data, mime, pid))

def delete_logo(pid):
    execute('UPDATE condominios SET logo_data=NULL,logo_mime=NULL,actualizado_en=NOW() WHERE id=%s', (pid,))

def update_cover(pid, data, mime):
    execute('UPDATE condominios SET portada_data=%s,portada_mime=%s,actualizado_en=NOW() WHERE id=%s', (data, mime, pid))

def delete_cover(pid):
    execute('UPDATE condominios SET portada_data=NULL,portada_mime=NULL,actualizado_en=NOW() WHERE id=%s', (pid,))

def dependencies(pid):
    tables=['espacios','usuario_inmuebles','cargos','pagos','gastos'];out={}
    for t in tables:
        out[t]=fetch_one(f'SELECT COUNT(*) n FROM {t} WHERE condominio_id=%s',(pid,))['n']
    return out

def deletable(pid):
    return sum(dependencies(pid).values()) == 0
