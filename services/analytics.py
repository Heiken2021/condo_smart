from core.db import fetch_all,fetch_one
def prop_rows(user):
 base="SELECT c.id,c.clave,c.nombre,c.tipo_codigo,c.direccion,c.logo_data,c.portada_data,c.activo,COUNT(DISTINCT e.id) espacios,COUNT(DISTINCT CASE WHEN e.estado_codigo='OCUPADO' THEN e.id END) ocupados,COALESCE((SELECT SUM(x.monto_mxn) FROM cargos x WHERE x.condominio_id=c.id AND x.activo),0) cargos,COALESCE((SELECT SUM(p.monto_mxn) FROM pagos p WHERE p.condominio_id=c.id AND p.activo),0) pagos,COALESCE((SELECT COUNT(*) FROM usuario_inmuebles a WHERE a.condominio_id=c.id AND a.activo AND a.rol_codigo='ADMINISTRADOR'),0) administradores FROM condominios c LEFT JOIN espacios e ON e.condominio_id=c.id AND e.activo"
 if user.get('rol_global')=='SUPERADMIN': return fetch_all(base+' GROUP BY c.id ORDER BY c.nombre')
 return fetch_all(base+' JOIN usuario_inmuebles scope ON scope.condominio_id=c.id AND scope.usuario_id=%s AND scope.activo=TRUE GROUP BY c.id ORDER BY c.nombre',(user['id'],))
def periods(pid=None):
 where='WHERE c.activo=TRUE';params=[]
 if pid:where+=' AND c.condominio_id=%s';params=[pid]
 return fetch_all(f"SELECT c.periodo,SUM(c.monto_mxn) cargos,COALESCE((SELECT SUM(p.monto_mxn) FROM pagos p WHERE p.periodo=c.periodo {'AND p.condominio_id='+str(pid) if pid else ''} AND p.activo),0) pagos FROM cargos c {where} GROUP BY c.periodo ORDER BY c.periodo",tuple(params))
def expense_categories(pid):return fetch_all('SELECT categoria_codigo,SUM(monto_mxn) total FROM gastos WHERE condominio_id=%s AND activo GROUP BY categoria_codigo ORDER BY total DESC',(pid,))
def occupation(pid):return fetch_all("SELECT COALESCE(estado_codigo,'SIN ESTADO') estado,COUNT(*) total FROM espacios WHERE condominio_id=%s AND activo GROUP BY estado_codigo",(pid,))

def kpis(pid):
 def total(table):return fetch_one(f"SELECT COALESCE(SUM(monto_mxn),0) total FROM {table} WHERE condominio_id=%s AND activo=TRUE",(pid,))["total"]
 c=total("cargos");p=total("pagos");g=total("gastos");return {"cargos":c,"pagos":p,"pendiente":max(c-p,0),"gastos":g,"saldo":p-g}
