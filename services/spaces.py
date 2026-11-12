from core.authorization import require
from core.db import fetch_all, fetch_one, execute
from services.property_structure import validate_space_structure


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


def _require_actor(actor_id, permission, property_id):
    return require(
        _actor(actor_id),
        permission,
        property_id,
    )


def list_spaces(property_id):
    return fetch_all(
        """
        SELECT e.id,e.condominio_id,e.clave,e.nombre,e.tipo_codigo,e.estado_codigo,
               e.superficie_m2,e.edificio_zona,e.nivel,e.uso_codigo,e.descripcion,
               e.fecha_construccion,e.anio_construccion,e.condicion_codigo,
               e.responsable_persona_id,e.responsable_relacion,
               p.nombre responsable_nombre,p.email responsable_email,
               p.telefono responsable_telefono,
               e.estructura_id,
               n.nombre estructura_nombre,n.tipo_codigo estructura_tipo,
               e.cuota_base,e.indiviso_pct,e.activo
        FROM espacios e
        LEFT JOIN personas p ON p.id=e.responsable_persona_id
        LEFT JOIN estructura_inmueble n ON n.id=e.estructura_id AND n.condominio_id=e.condominio_id
        WHERE e.condominio_id=%s
        ORDER BY COALESCE(e.clave,''),e.nombre
        """,
        (property_id,),
    )


def get_space(property_id, space_id):
    return fetch_one(
        """
        SELECT e.*,p.nombre responsable_nombre,p.email responsable_email,
               p.telefono responsable_telefono
        FROM espacios e
        LEFT JOIN personas p ON p.id=e.responsable_persona_id
        LEFT JOIN estructura_inmueble n ON n.id=e.estructura_id AND n.condominio_id=e.condominio_id
        WHERE e.id=%s AND e.condominio_id=%s
        """,
        (space_id, property_id),
    )


def list_people(property_id):
    return fetch_all(
        'SELECT DISTINCT p.id,p.nombre,p.email,p.telefono FROM personas p JOIN persona_espacios pe ON pe.persona_id=p.id JOIN espacios e ON e.id=pe.espacio_id WHERE e.condominio_id=%s ORDER BY p.nombre',
        (property_id,),
    )


def create_space(property_id, nombre, tipo_codigo, estado_codigo,
                 cuota_base=0, indiviso_pct=0, clave=None, superficie_m2=0,
                 edificio_zona=None, nivel=None, uso_codigo=None, descripcion=None,
                 fecha_construccion=None, anio_construccion=None, condicion_codigo=None,
                 responsable_persona_id=None, responsable_relacion=None,
                estructura_id=None, actor_id=None):
    _require_actor(
        actor_id,
        "ESPACIO_CREAR",
        property_id,
    )
    estructura_id = validate_space_structure(property_id, estructura_id)
    return execute(
        """
        INSERT INTO espacios(
            condominio_id,clave,nombre,tipo_codigo,estado_codigo,superficie_m2,
            edificio_zona,nivel,uso_codigo,descripcion,fecha_construccion,condicion_codigo,responsable_persona_id,
            responsable_relacion,estructura_id,cuota_base,indiviso_pct,activo
        ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,TRUE)
        RETURNING id
        """,
        (property_id,clave,nombre,tipo_codigo,estado_codigo,superficie_m2,
         edificio_zona,nivel,uso_codigo,descripcion,fecha_construccion,condicion_codigo,responsable_persona_id,
         responsable_relacion,estructura_id,cuota_base,indiviso_pct),
        returning=True,
    )


def update_space(property_id, space_id, nombre, tipo_codigo, estado_codigo,
                 cuota_base, indiviso_pct, clave=None, superficie_m2=0,
                 edificio_zona=None, nivel=None, uso_codigo=None, descripcion=None,
                 fecha_construccion=None, anio_construccion=None, condicion_codigo=None,
                 responsable_persona_id=None, responsable_relacion=None,
                estructura_id=None, actor_id=None):
    _require_actor(
        actor_id,
        "ESPACIO_MODIFICAR",
        property_id,
    )
    if not get_space(property_id, space_id):
        raise ValueError("INVALID_SPACE")
    estructura_id = validate_space_structure(property_id, estructura_id)
    execute(
        """
        UPDATE espacios SET clave=%s,nombre=%s,tipo_codigo=%s,estado_codigo=%s,
            superficie_m2=%s,edificio_zona=%s,nivel=%s,uso_codigo=%s,descripcion=%s,
            fecha_construccion=%s,condicion_codigo=%s,responsable_persona_id=%s,
            responsable_relacion=%s,estructura_id=%s,cuota_base=%s,
            indiviso_pct=%s
        WHERE id=%s AND condominio_id=%s
        """,
        (clave,nombre,tipo_codigo,estado_codigo,superficie_m2,edificio_zona,nivel,
         uso_codigo,descripcion,fecha_construccion,condicion_codigo,responsable_persona_id,responsable_relacion,estructura_id,
         cuota_base,indiviso_pct,space_id,property_id),
    )


def list_occupancy_history(property_id, space_id):
    return fetch_all(
        """
        SELECT pe.id,p.nombre,p.email,p.telefono,pe.tipo_relacion,
               pe.fecha_inicio,pe.fecha_fin,pe.activo,
               CASE WHEN pe.fecha_inicio IS NULL THEN NULL
                    ELSE CURRENT_DATE-pe.fecha_inicio END antiguedad_dias
        FROM persona_espacios pe
        JOIN personas p ON p.id=pe.persona_id
        JOIN espacios e ON e.id=pe.espacio_id
        WHERE pe.espacio_id=%s AND e.condominio_id=%s
        ORDER BY pe.fecha_inicio DESC NULLS LAST,pe.id DESC
        """,(space_id,property_id))


def sync_responsible_history(
    property_id,
    space_id,
    persona_id,
    relation,
    fecha_inicio=None,
    actor_id=None,
):
    _require_actor(
        actor_id,
        "ESPACIO_MODIFICAR",
        property_id,
    )
    if not get_space(property_id, space_id):
        return False
    current=fetch_one("SELECT persona_id,tipo_relacion FROM persona_espacios WHERE espacio_id=%s AND activo=TRUE ORDER BY id DESC LIMIT 1",(space_id,))
    if current and current["persona_id"]==persona_id and current["tipo_relacion"]==relation:
        return True
    if not current and not persona_id:
        return True
    execute("UPDATE persona_espacios SET activo=FALSE,fecha_fin=COALESCE(fecha_fin,CURRENT_DATE) WHERE espacio_id=%s AND activo=TRUE",(space_id,))
    if persona_id:
        execute("INSERT INTO persona_espacios(persona_id,espacio_id,tipo_relacion,fecha_inicio,activo) VALUES(%s,%s,%s,COALESCE(%s,CURRENT_DATE),TRUE)",(persona_id,space_id,relation,fecha_inicio))
    return True


def set_active(property_id, space_id, active, actor_id):
    permission = (
        "ESPACIO_REACTIVAR"
        if active
        else "ESPACIO_DESACTIVAR"
    )
    _require_actor(
        actor_id,
        permission,
        property_id,
    )
    if not get_space(property_id, space_id):
        raise ValueError("INVALID_SPACE")
    execute(
        "UPDATE espacios SET activo=%s WHERE id=%s AND condominio_id=%s",
        (active, space_id, property_id),
    )


def dependencies(property_id, space_id, actor_id=None):
    if actor_id is not None:
        _require_actor(
            actor_id,
            "ESPACIO_ELIMINAR",
            property_id,
        )
    if not get_space(property_id, space_id):
        return None
    checks = {
        "personas": ("SELECT COUNT(*) n FROM persona_espacios WHERE espacio_id=%s", (space_id,)),
        "usuarios": ("SELECT COUNT(*) n FROM usuario_espacios WHERE espacio_id=%s", (space_id,)),
        "cargos": ("SELECT COUNT(*) n FROM cargos WHERE espacio_id=%s AND condominio_id=%s", (space_id,property_id)),
        "pagos": ("SELECT COUNT(*) n FROM pagos WHERE espacio_id=%s AND condominio_id=%s", (space_id,property_id)),
    }
    return {name:int(fetch_one(sql,params)["n"]) for name,(sql,params) in checks.items()}


def deletable(property_id, space_id, actor_id=None):
    deps = dependencies(
        property_id,
        space_id,
        actor_id,
    )
    return deps is not None and sum(deps.values()) == 0


def delete_space(property_id, space_id, actor_id):
    _require_actor(
        actor_id,
        "ESPACIO_ELIMINAR",
        property_id,
    )
    if not deletable(property_id, space_id):
        return False
    execute(
        "DELETE FROM espacios WHERE id=%s AND condominio_id=%s",
        (space_id, property_id),
    )
    return True
