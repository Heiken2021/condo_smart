from core.db import fetch_all, fetch_one, execute

def list_properties(user):
    fields='c.id,c.clave,c.nombre,c.tipo_codigo,c.direccion,c.rfc,c.moneda_base,c.zona_horaria,c.fecha_construccion,c.condicion_codigo,c.activo,c.logo_data,c.logo_mime,c.portada_data,c.portada_mime'
    if user.get('rol_global') == 'SUPERADMIN':
        return fetch_all(f'SELECT {fields} FROM condominios c ORDER BY c.nombre')
    return fetch_all(f'SELECT DISTINCT {fields} FROM condominios c JOIN usuario_inmuebles ui ON ui.condominio_id=c.id WHERE ui.usuario_id=%s AND ui.activo=TRUE ORDER BY c.nombre',(user['id'],))

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
