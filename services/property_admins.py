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
