from core.db import fetch_all,fetch_one,execute
def values(code):return fetch_all('SELECT v.* FROM catalogo_valores v JOIN catalogos c ON c.id=v.catalogo_id WHERE c.codigo=%s AND v.activo=TRUE ORDER BY v.nombre',(code,))
def options(code):return {x['nombre']:x['codigo'] for x in values(code)}
def references(code,value):
 m={'TIPO_INMUEBLE':('condominios','tipo_codigo'),'TIPO_ESPACIO':('espacios','tipo_codigo')}
 if code not in m:return 0
 t,c=m[code];return fetch_one(f'SELECT COUNT(*) n FROM {t} WHERE {c}=%s',(value,))['n']
def auto_code(name):return '_'.join(name.upper().split())
