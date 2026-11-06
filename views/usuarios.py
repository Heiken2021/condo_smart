from core.db import fetch_all
from core.access import cid
from components.ui import title,table
def render():title('Usuarios Y Accesos','Módulo Preservado Para Build 04');table(fetch_all('SELECT u.username,u.nombre,u.email,ui.rol_local,u.activo FROM usuarios u JOIN usuario_inmuebles ui ON ui.usuario_id=u.id WHERE ui.condominio_id=%s',(cid(),)),'usuarios',['username','nombre','email','rol_local','activo'])
