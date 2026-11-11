from core.authorization import require
from core.db import fetch_all, fetch_one, execute


def _actor(actor_id):
    user = fetch_one(
        """
        SELECT id,username,nombre,email,rol_global,activo
        FROM usuarios
        WHERE id=%s
        """,
        (actor_id,),
    )

    if not user or not user.get("activo"):
        raise PermissionError("USER_INACTIVE")

    return dict(user)


def _require_actor(actor_id, permission, property_id=None):
    return require(
        _actor(actor_id),
        permission,
        property_id,
    )


def list_properties(user):
    fields = (
        "c.id,c.clave,c.nombre,c.tipo_codigo,c.direccion,c.rfc,"
        "c.moneda_base,c.zona_horaria,c.fecha_construccion,"
        "c.condicion_codigo,c.activo,c.logo_data,c.logo_mime,"
        "c.portada_data,c.portada_mime"
    )

    if user.get("rol_global") == "SUPERADMIN":
        return fetch_all(
            f"SELECT {fields} FROM condominios c ORDER BY c.nombre"
        )

    return fetch_all(
        f"""
        SELECT DISTINCT {fields}
        FROM condominios c
        JOIN usuario_inmuebles ui
          ON ui.condominio_id=c.id
        WHERE ui.usuario_id=%s
          AND ui.activo=TRUE
        ORDER BY c.nombre
        """,
        (user["id"],),
    )


def create_property(actor_id, values):
    _require_actor(
        actor_id,
        "INMUEBLE_CREAR",
    )

    return execute(
        """
        INSERT INTO condominios(
            clave,
            nombre,
            tipo_codigo,
            direccion,
            rfc,
            moneda_base,
            zona_horaria,
            fecha_construccion,
            condicion_codigo
        )
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING id
        """,
        (
            values["clave"],
            values["nombre"],
            values["tipo_codigo"],
            values["direccion"],
            values["rfc"],
            values["moneda_base"],
            values["zona_horaria"],
            values["fecha_construccion"],
            values["condicion_codigo"],
        ),
        True,
    )


def get_property(pid, actor_id):
    _require_actor(
        actor_id,
        "INMUEBLE_CONSULTAR",
        pid,
    )

    return fetch_one(
        "SELECT * FROM condominios WHERE id=%s",
        (pid,),
    )


def update_property(pid, values, actor_id):
    _require_actor(
        actor_id,
        "INMUEBLE_MODIFICAR",
        pid,
    )

    execute(
        """
        UPDATE condominios
        SET clave=%s,
            nombre=%s,
            tipo_codigo=%s,
            moneda_base=%s,
            direccion=%s,
            rfc=%s,
            zona_horaria=%s,
            fecha_construccion=%s,
            condicion_codigo=%s,
            actualizado_en=NOW()
        WHERE id=%s
        """,
        (
            values["clave"],
            values["nombre"],
            values["tipo_codigo"],
            values["moneda_base"],
            values["direccion"],
            values["rfc"],
            values["zona_horaria"],
            values["fecha_construccion"],
            values["condicion_codigo"],
            pid,
        ),
    )


def update_logo(pid, data, mime, actor_id):
    _require_actor(
        actor_id,
        "INMUEBLE_BRANDING",
        pid,
    )

    execute(
        """
        UPDATE condominios
        SET logo_data=%s,
            logo_mime=%s,
            actualizado_en=NOW()
        WHERE id=%s
        """,
        (data, mime, pid),
    )


def delete_logo(pid, actor_id):
    _require_actor(
        actor_id,
        "INMUEBLE_BRANDING",
        pid,
    )

    execute(
        """
        UPDATE condominios
        SET logo_data=NULL,
            logo_mime=NULL,
            actualizado_en=NOW()
        WHERE id=%s
        """,
        (pid,),
    )


def update_cover(pid, data, mime, actor_id):
    _require_actor(
        actor_id,
        "INMUEBLE_BRANDING",
        pid,
    )

    execute(
        """
        UPDATE condominios
        SET portada_data=%s,
            portada_mime=%s,
            actualizado_en=NOW()
        WHERE id=%s
        """,
        (data, mime, pid),
    )


def delete_cover(pid, actor_id):
    _require_actor(
        actor_id,
        "INMUEBLE_BRANDING",
        pid,
    )

    execute(
        """
        UPDATE condominios
        SET portada_data=NULL,
            portada_mime=NULL,
            actualizado_en=NOW()
        WHERE id=%s
        """,
        (pid,),
    )


def set_property_active(pid, active, actor_id):
    permission = (
        "INMUEBLE_REACTIVAR"
        if active
        else "INMUEBLE_DESACTIVAR"
    )

    _require_actor(
        actor_id,
        permission,
        pid,
    )

    execute(
        """
        UPDATE condominios
        SET activo=%s,
            actualizado_en=NOW()
        WHERE id=%s
        """,
        (active, pid),
    )


def dependencies(pid, actor_id):
    _require_actor(
        actor_id,
        "INMUEBLE_ELIMINAR",
        pid,
    )

    tables = [
        "espacios",
        "usuario_inmuebles",
        "cargos",
        "pagos",
        "gastos",
    ]

    result = {}

    for table in tables:
        result[table] = fetch_one(
            f"""
            SELECT COUNT(*) n
            FROM {table}
            WHERE condominio_id=%s
            """,
            (pid,),
        )["n"]

    return result


def deletable(pid, actor_id):
    return sum(
        dependencies(pid, actor_id).values()
    ) == 0


def delete_property(pid, actor_id):
    _require_actor(
        actor_id,
        "INMUEBLE_ELIMINAR",
        pid,
    )

    if not deletable(pid, actor_id):
        raise ValueError("PROPERTY_HAS_DEPENDENCIES")

    execute(
        "DELETE FROM condominios WHERE id=%s",
        (pid,),
    )

    return True
