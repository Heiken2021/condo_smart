from core.db import fetch_all,fetch_one,execute
def list_properties():return fetch_all('SELECT id,clave,nombre,tipo_codigo,direccion,rfc,moneda_base,zona_horaria,activo,logo_data,logo_mime,portada_data,portada_mime FROM condominios ORDER BY nombre')
def dependencies(pid):
 tables=['espacios','usuario_inmuebles','cargos','pagos','gastos'];out={}
 for t in tables:
  col='condominio_id';out[t]=fetch_one(f'SELECT COUNT(*) n FROM {t} WHERE {col}=%s',(pid,))['n']
 return out
def deletable(pid):return sum(dependencies(pid).values())==0
