from core.db import fetch_all, fetch_one, execute


def _require_superadmin(actor_id):
    actor = fetch_one(
        """
        SELECT id,rol_global,activo
        FROM usuarios
        WHERE id=%s
        """,
        (actor_id,),
    )

    if (
        not actor
        or not actor.get("activo")
        or actor.get("rol_global") != "SUPERADMIN"
    ):
        raise PermissionError("GLOBAL_SUPERADMIN_REQUIRED")

    return dict(actor)

def list_settings():
    return fetch_all('SELECT clave,valor,tipo,descripcion,activo,actualizado_en FROM configuracion_sistema ORDER BY clave')

def get_setting(key, default=None):
    row = fetch_one('SELECT valor FROM configuracion_sistema WHERE clave=%s AND activo=TRUE', (key,))
    return row['valor'] if row else default

def set_setting(key, value, actor, setting_type='TEXTO', description=None):
    _require_superadmin(actor)

    execute('''INSERT INTO configuracion_sistema(clave,valor,tipo,descripcion,actualizado_por)
               VALUES(%s,%s,%s,%s,%s)
               ON CONFLICT(clave) DO UPDATE SET valor=EXCLUDED.valor,tipo=EXCLUDED.tipo,
               descripcion=COALESCE(EXCLUDED.descripcion,configuracion_sistema.descripcion),
               activo=TRUE,actualizado_por=EXCLUDED.actualizado_por,actualizado_en=NOW()''',
            (key, value, setting_type, description, actor))

def get_system_identity():
    return fetch_one('SELECT * FROM identidad_sistema WHERE id=1') or {}

def update_system_logo(data, mime, actor):
    _require_superadmin(actor)

    execute('UPDATE identidad_sistema SET logo_data=%s,logo_mime=%s,actualizado_por=%s,actualizado_en=NOW() WHERE id=1', (data, mime, actor))

def delete_system_logo(actor):
    _require_superadmin(actor)

    execute('UPDATE identidad_sistema SET logo_data=NULL,logo_mime=NULL,actualizado_por=%s,actualizado_en=NOW() WHERE id=1', (actor,))
