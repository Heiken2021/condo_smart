from core.db import fetch_all,fetch_one,execute
from core.security import hash_password,validate_password
def list_admins(pid):return fetch_all("SELECT u.id,u.username,u.nombre,u.email,u.activo,ui.rol_codigo,ui.activo asignacion_activa FROM usuarios u JOIN usuario_inmuebles ui ON ui.usuario_id=u.id WHERE ui.condominio_id=%s AND ui.rol_codigo IN ('ADMINISTRADOR','GERENTE','CONTABILIDAD','COMITE') ORDER BY u.nombre",(pid,))
def create_admin(pid,name,email,username,password,actor):
 if not validate_password(password):raise ValueError('Contraseña insegura')
 s,h=hash_password(password);u=execute("INSERT INTO usuarios(username,nombre,email,rol_global,salt,password_hash,debe_cambiar_password) VALUES(%s,%s,%s,'USUARIO',%s,%s,TRUE) RETURNING id",(username,name,email.lower(),s,h),True);execute("INSERT INTO usuario_inmuebles(usuario_id,condominio_id,rol_codigo,asignado_por) VALUES(%s,%s,'ADMINISTRADOR',%s)",(u['id'],pid,actor));return u
def revoke(pid,uid,actor):execute('UPDATE usuario_inmuebles SET activo=FALSE,revocado_por=%s,revocado_en=NOW() WHERE usuario_id=%s AND condominio_id=%s',(actor,uid,pid))
def reactivate(pid,uid,actor):execute('UPDATE usuario_inmuebles SET activo=TRUE,asignado_por=%s,asignado_en=NOW(),revocado_por=NULL,revocado_en=NULL WHERE usuario_id=%s AND condominio_id=%s',(actor,uid,pid))
def reset_password(uid,password):
 if not validate_password(password):raise ValueError('Contraseña insegura')
 s,h=hash_password(password);execute('UPDATE usuarios SET salt=%s,password_hash=%s,debe_cambiar_password=TRUE WHERE id=%s',(s,h,uid))


def get_admin(user_id):
    return fetch_one("SELECT * FROM usuarios WHERE id=%s", (user_id,))

def update_admin_profile(user_id,username,nombre,email,telefono_of_casa,telefono_celular,direccion,origen_codigo):
    execute(
        "UPDATE usuarios SET username=%s,nombre=%s,email=%s,telefono_of_casa=%s,telefono_celular=%s,direccion=%s,origen_codigo=%s,actualizado_en=NOW() WHERE id=%s",
        (username,nombre,email,telefono_of_casa,telefono_celular,direccion,origen_codigo,user_id),
    )


def list_assignable_admins(property_id):
    """Identidades administradoras existentes disponibles para el inmueble."""
    return fetch_all(
        """
        SELECT DISTINCT
            u.id,u.username,u.nombre,u.email,u.activo,
            current_ui.activo AS asignacion_actual_activa
        FROM usuarios u
        JOIN usuario_inmuebles any_ui
          ON any_ui.usuario_id=u.id
         AND any_ui.rol_codigo='ADMINISTRADOR'
        LEFT JOIN usuario_inmuebles current_ui
          ON current_ui.usuario_id=u.id
         AND current_ui.condominio_id=%s
         AND current_ui.rol_codigo='ADMINISTRADOR'
        WHERE u.rol_global<>'SUPERADMIN'
          AND u.activo=TRUE
          AND (current_ui.usuario_id IS NULL OR current_ui.activo=FALSE)
        ORDER BY u.nombre,u.username
        """,
        (property_id,),
    )


def assign_existing_admin(property_id, user_id, actor_id):
    """Crea o reactiva solo la asignacion, sin duplicar la identidad."""
    user=fetch_one(
        "SELECT id,username,nombre,email FROM usuarios "
        "WHERE id=%s AND activo=TRUE AND rol_global<>'SUPERADMIN'",
        (user_id,),
    )
    if not user:
        raise ValueError('ADMINISTRADOR_NO_DISPONIBLE')
    assignment=fetch_one(
        "SELECT activo FROM usuario_inmuebles "
        "WHERE usuario_id=%s AND condominio_id=%s AND rol_codigo='ADMINISTRADOR'",
        (user_id,property_id),
    )
    if assignment and assignment['activo']:
        return {'status':'ALREADY_ACTIVE','user_id':user_id}
    if assignment:
        execute(
            "UPDATE usuario_inmuebles SET activo=TRUE,asignado_por=%s,"
            "asignado_en=NOW(),revocado_por=NULL,revocado_en=NULL "
            "WHERE usuario_id=%s AND condominio_id=%s "
            "AND rol_codigo='ADMINISTRADOR'",
            (actor_id,user_id,property_id),
        )
        return {'status':'REACTIVATED','user_id':user_id}
    execute(
        "INSERT INTO usuario_inmuebles"
        "(usuario_id,condominio_id,rol_codigo,activo,asignado_por) "
        "VALUES(%s,%s,'ADMINISTRADOR',TRUE,%s)",
        (user_id,property_id,actor_id),
    )
    return {'status':'ASSIGNED','user_id':user_id}


def admin_delete_dependencies(user_id):
    user=fetch_one("SELECT id,username,nombre,email,rol_global FROM usuarios WHERE id=%s",(user_id,))
    if not user: return None
    checks={
        'asignaciones_activas':("SELECT COUNT(*) n FROM usuario_inmuebles WHERE usuario_id=%s AND activo=TRUE",(user_id,)),
        'asignaciones_totales':("SELECT COUNT(*) n FROM usuario_inmuebles WHERE usuario_id=%s",(user_id,)),
        'espacios':("SELECT COUNT(*) n FROM usuario_espacios WHERE usuario_id=%s",(user_id,)),
        'actualizaciones_configuracion':("SELECT COUNT(*) n FROM configuracion_sistema WHERE actualizado_por=%s",(user_id,)),
        'actualizaciones_identidad':("SELECT COUNT(*) n FROM identidad_sistema WHERE actualizado_por=%s",(user_id,)),
        'asignaciones_realizadas':("SELECT COUNT(*) n FROM usuario_inmuebles WHERE asignado_por=%s",(user_id,)),
        'revocaciones_realizadas':("SELECT COUNT(*) n FROM usuario_inmuebles WHERE revocado_por=%s",(user_id,)),
        'tokens_recuperacion':("SELECT COUNT(*) n FROM password_reset_tokens WHERE usuario_id=%s",(user_id,)),
    }
    result={name:int(fetch_one(sql,params)['n']) for name,(sql,params) in checks.items()}
    result['usuario']=dict(user)
    return result


def delete_inactive_admin(user_id,current_user_id):
    if user_id==current_user_id: raise ValueError('CANNOT_DELETE_CURRENT_USER')
    deps=admin_delete_dependencies(user_id)
    if not deps: raise ValueError('ADMIN_NOT_FOUND')
    if deps['usuario'].get('rol_global')=='SUPERADMIN': raise ValueError('CANNOT_DELETE_SUPERADMIN')
    if deps['asignaciones_activas']>0: raise ValueError('ACTIVE_PROPERTY_ASSIGNMENTS')
    if deps['espacios']>0: raise ValueError('ACTIVE_SPACE_ASSIGNMENTS')
    # Referencias historicas anulables se conservan sin bloquear la eliminacion.
    execute('UPDATE usuario_inmuebles SET asignado_por=NULL WHERE asignado_por=%s',(user_id,))
    execute('UPDATE usuario_inmuebles SET revocado_por=NULL WHERE revocado_por=%s',(user_id,))
    execute('UPDATE configuracion_sistema SET actualizado_por=NULL WHERE actualizado_por=%s',(user_id,))
    execute('UPDATE identidad_sistema SET actualizado_por=NULL WHERE actualizado_por=%s',(user_id,))
    # usuario_inmuebles y password_reset_tokens se eliminan por ON DELETE CASCADE.
    execute('DELETE FROM usuarios WHERE id=%s',(user_id,))
    return True
