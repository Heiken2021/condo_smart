from core.db import fetch_all
from core.access import cid
from components.ui import title,table
def render():title('Propietarios / Inquilinos','Módulo Preservado Para Build 03');table(fetch_all('SELECT p.nombre,p.email,p.telefono,pe.tipo_relacion,pe.fecha_inicio,pe.fecha_fin,pe.activo FROM persona_espacios pe JOIN personas p ON p.id=pe.persona_id JOIN espacios e ON e.id=pe.espacio_id WHERE e.condominio_id=%s',(cid(),)),'personas',['nombre','email','telefono','tipo_relacion','fecha_inicio','fecha_fin','activo'])
