from core.db import fetch_all
from core.access import cid
from components.ui import title,table
def render():title('Auditoría','Trazabilidad De Cambios');table(fetch_all('SELECT fecha,username,accion,entidad,detalle FROM auditoria WHERE condominio_id=%s OR condominio_id IS NULL ORDER BY fecha DESC LIMIT 500',(cid(),)),'auditoria',['fecha','username','accion','entidad','detalle'])
