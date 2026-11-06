from core.db import fetch_all
from core.access import cid
from components.ui import title,table
def render():title('Espacios','Módulo Preservado Para Build 02');table(fetch_all('SELECT nombre,tipo_codigo,estado_codigo,cuota_base,indiviso_pct,activo FROM espacios WHERE condominio_id=%s ORDER BY nombre',(cid(),)),'espacios',['nombre','tipo_codigo','estado_codigo','cuota_base','indiviso_pct','activo'])
