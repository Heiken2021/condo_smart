from core.db import fetch_all,fetch_one
REQUIRED={
 'usuarios':['rol_global','activo'],
 'usuario_inmuebles':['rol_codigo','asignado_por','revocado_en'],
 'condominios':['logo_data','portada_data'],
 'roles':['codigo'],
 'permisos':['codigo'],
 'configuracion_sistema':['clave','valor','tipo','actualizado_en'],
 'identidad_sistema':['logo_data','logo_mime','actualizado_en'],
}
def check():
 issues=[]
 for table,cols in REQUIRED.items():
  found={x['column_name'] for x in fetch_all("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name=%s",(table,))}
  if not found:issues.append(f'Tabla faltante: {table}')
  for c in cols:
   if c not in found:issues.append(f'Columna faltante: {table}.{c}')
 if not fetch_one("SELECT 1 ok FROM usuarios WHERE rol_global='SUPERADMIN' AND activo=TRUE LIMIT 1"):issues.append('No existe SuperAdmin activo')
 return issues
