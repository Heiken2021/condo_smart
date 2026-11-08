from core.db import fetch_all, fetch_one, execute


def list_spaces(property_id):
    return fetch_all(
        """
        SELECT id, condominio_id, nombre, tipo_codigo, estado_codigo,
               cuota_base, indiviso_pct, activo
        FROM espacios
        WHERE condominio_id=%s
        ORDER BY nombre
        """,
        (property_id,),
    )


def get_space(property_id, space_id):
    return fetch_one(
        """
        SELECT id, condominio_id, nombre, tipo_codigo, estado_codigo,
               cuota_base, indiviso_pct, activo
        FROM espacios
        WHERE id=%s AND condominio_id=%s
        """,
        (space_id, property_id),
    )


def create_space(
    property_id,
    nombre,
    tipo_codigo,
    estado_codigo,
    cuota_base=0,
    indiviso_pct=0,
):
    return execute(
        """
        INSERT INTO espacios(
            condominio_id,
            nombre,
            tipo_codigo,
            estado_codigo,
            cuota_base,
            indiviso_pct,
            activo
        )
        VALUES(%s,%s,%s,%s,%s,%s,TRUE)
        RETURNING id
        """,
        (
            property_id,
            nombre,
            tipo_codigo,
            estado_codigo,
            cuota_base,
            indiviso_pct,
        ),
        returning=True,
    )


def update_space(
    property_id,
    space_id,
    nombre,
    tipo_codigo,
    estado_codigo,
    cuota_base,
    indiviso_pct,
):
    execute(
        """
        UPDATE espacios
        SET nombre=%s,
            tipo_codigo=%s,
            estado_codigo=%s,
            cuota_base=%s,
            indiviso_pct=%s
        WHERE id=%s AND condominio_id=%s
        """,
        (
            nombre,
            tipo_codigo,
            estado_codigo,
            cuota_base,
            indiviso_pct,
            space_id,
            property_id,
        ),
    )


def set_active(property_id, space_id, active):
    execute(
        """
        UPDATE espacios
        SET activo=%s
        WHERE id=%s AND condominio_id=%s
        """,
        (active, space_id, property_id),
    )


def dependencies(property_id, space_id):
    space = get_space(property_id, space_id)

    if not space:
        return None

    checks = {
        "personas": (
            "SELECT COUNT(*) n FROM persona_espacios WHERE espacio_id=%s",
            (space_id,),
        ),
        "usuarios": (
            "SELECT COUNT(*) n FROM usuario_espacios WHERE espacio_id=%s",
            (space_id,),
        ),
        "cargos": (
            "SELECT COUNT(*) n FROM cargos WHERE espacio_id=%s AND condominio_id=%s",
            (space_id, property_id),
        ),
        "pagos": (
            "SELECT COUNT(*) n FROM pagos WHERE espacio_id=%s AND condominio_id=%s",
            (space_id, property_id),
        ),
    }

    result = {}
    for name, (sql, params) in checks.items():
        row = fetch_one(sql, params)
        result[name] = int(row["n"])

    return result


def deletable(property_id, space_id):
    deps = dependencies(property_id, space_id)

    if deps is None:
        return False

    return sum(deps.values()) == 0


def delete_space(property_id, space_id):
    if not deletable(property_id, space_id):
        return False

    execute(
        "DELETE FROM espacios WHERE id=%s AND condominio_id=%s",
        (space_id, property_id),
    )
    return True
