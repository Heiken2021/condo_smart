from core.db import fetch_all

def _local_roles(user):
    if not user or not user.get('id'): return set()
    return {r['rol_codigo'] for r in fetch_all('SELECT DISTINCT rol_codigo FROM usuario_inmuebles WHERE usuario_id=%s AND activo=TRUE',(user['id'],))}

def allowed(user,key):
    if not user or not user.get('activo'): return False
    if user.get('rol_global') == 'SUPERADMIN': return True
    if key in {'configuracion','catalogos','auditoria'}: return False
    roles=_local_roles(user)
    if roles & {'ADMINISTRADOR','GERENTE','COMITE'}:
        return key in {'portafolio','dashboard','inmuebles','espacios','personas','finanzas','reportes','notificaciones','soporte'}
    if 'CONTABILIDAD' in roles:
        return key in {'dashboard','finanzas','reportes','notificaciones','soporte'}
    if roles & {'PROPIETARIO','INQUILINO','OCUPANTE'}:
        return key in {'dashboard','espacios','personas','finanzas','notificaciones','soporte'}
    return False
