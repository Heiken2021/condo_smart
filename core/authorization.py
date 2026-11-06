from dataclasses import dataclass
from core.db import fetch_one
@dataclass(frozen=True)
class Decision:allowed:bool;reason:str;role:str|None=None;scope:str|None=None
def authorize(user,permission,property_id=None):
 if not user or not user.get('activo'):return Decision(False,'USER_INACTIVE')
 if user.get('rol_global')=='SUPERADMIN':return Decision(True,'GLOBAL_SUPERADMIN','SUPERADMIN','GLOBAL')
 if property_id is None:return Decision(False,'PROPERTY_REQUIRED')
 row=fetch_one('SELECT ui.rol_codigo FROM usuario_inmuebles ui JOIN rol_permisos rp ON rp.rol_codigo=ui.rol_codigo WHERE ui.usuario_id=%s AND ui.condominio_id=%s AND ui.activo=TRUE AND rp.permiso_codigo=%s AND rp.permitido=TRUE',(user['id'],property_id,permission))
 if not row:return Decision(False,'PROPERTY_NOT_ASSIGNED')
 return Decision(True,'LOCAL_ROLE',row['rol_codigo'],'INMUEBLE')
def require(user,permission,property_id=None):
 d=authorize(user,permission,property_id)
 if not d.allowed:raise PermissionError(d.reason)
 return d
