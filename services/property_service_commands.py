import json
import uuid

from core.authorization import authorize
from core.db import fetch_one, pool


MANAGE_PERMISSION = "FINANZAS_REGLA_GESTIONAR"

SCOPE_LEVELS = {
    "INMUEBLE",
    "ESTRUCTURA",
    "ESPACIO",
}


def _required_text(
    value,
    error_code,
    maximum=None,
):
    value = str(value or "").strip()

    if not value:
        raise ValueError(error_code)

    if (
        maximum is not None
        and len(value) > maximum
    ):
        raise ValueError(
            error_code + "_TOO_LONG"
        )

    return value


def _optional_text(
    value,
    maximum=None,
):
    value = str(value or "").strip()

    if not value:
        return None

    if (
        maximum is not None
        and len(value) > maximum
    ):
        raise ValueError(
            "OPTIONAL_TEXT_TOO_LONG"
        )

    return value


def _actor(
    *,
    actor_id,
    property_id,
):
    actor = fetch_one(
        """
        SELECT *
        FROM usuarios
        WHERE id=%s
          AND activo=TRUE
        """,
        (actor_id,),
    )

    if not actor:
        raise PermissionError(
            "PROPERTY_SERVICE_ACTOR_NOT_FOUND"
        )

    actor = dict(actor)

    decision = authorize(
        actor,
        MANAGE_PERMISSION,
        property_id,
    )

    if not decision.allowed:
        raise PermissionError(
            "PROPERTY_SERVICE_ACCESS_DENIED"
        )

    return actor


def _audit_json(value):
    return json.dumps(
        value or {},
        default=str,
        ensure_ascii=False,
    )


def _insert_audit(
    cursor,
    *,
    actor,
    property_id,
    operation_type,
    entity,
    entity_id,
    previous_status=None,
    new_status=None,
    detail=None,
    metadata=None,
    trace_id=None,
):
    trace_id = (
        trace_id
        or str(uuid.uuid4())
    )

    cursor.execute(
        """
        INSERT INTO auditoria_financiera(
            condominio_id,
            usuario_id,
            username,
            tipo_operacion,
            entidad,
            entidad_id,
            estado_anterior,
            estado_nuevo,
            detalle,
            metadata,
            trace_id
        )
        VALUES(
            %s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s::jsonb,%s
        )
        RETURNING id
        """,
        (
            property_id,
            actor["id"],
            actor.get("username"),
            operation_type,
            entity,
            entity_id,
            previous_status,
            new_status,
            detail,
            _audit_json(metadata),
            trace_id,
        ),
    )

    return dict(cursor.fetchone())



def _require_active_service_category(
    cursor,
    *,
    property_id,
    category_id,
):
    if category_id is None:
        raise ValueError(
            "PROPERTY_SERVICE_CATEGORY_REQUIRED"
        )

    cursor.execute(
        """
        SELECT
            id,
            codigo,
            nombre
        FROM property_service_categories
        WHERE id=%s
          AND condominio_id=%s
          AND activo=TRUE
        """,
        (
            category_id,
            property_id,
        ),
    )

    row = cursor.fetchone()

    if not row:
        raise ValueError(
            "PROPERTY_SERVICE_CATEGORY_NOT_FOUND"
        )

    return dict(row)


def create_property_service(
    *,
    property_id,
    code,
    name,
    actor_id,
    description=None,
    category_id=None,
):
    actor = _actor(
        actor_id=actor_id,
        property_id=property_id,
    )

    code = _required_text(
        code,
        "PROPERTY_SERVICE_CODE_REQUIRED",
        100,
    ).upper()

    name = _required_text(
        name,
        "PROPERTY_SERVICE_NAME_REQUIRED",
        200,
    )

    description = _optional_text(
        description,
    )

    trace_id = str(uuid.uuid4())

    with pool().connection() as connection:
        try:
            with connection.cursor() as cursor:
                category = (
                    _require_active_service_category(
                        cursor,
                        property_id=property_id,
                        category_id=category_id,
                    )
                )

                cursor.execute(
                    """
                    INSERT INTO property_service_catalog(
                        condominio_id,
                        codigo,
                        nombre,
                        descripcion,
                        categoria_id,
                        activo,
                        creado_por,
                        actualizado_por
                    )
                    VALUES(
                        %s,%s,%s,%s,%s,
                        TRUE,%s,%s
                    )
                    RETURNING *
                    """,
                    (
                        property_id,
                        code,
                        name,
                        description,
                        category_id,
                        actor["id"],
                        actor["id"],
                    ),
                )

                service = dict(
                    cursor.fetchone()
                )

                audit = _insert_audit(
                    cursor,
                    actor=actor,
                    property_id=property_id,
                    operation_type=(
                        "PROPERTY_SERVICE_CREATED"
                    ),
                    entity="PROPERTY_SERVICE",
                    entity_id=service["id"],
                    new_status="ACTIVO",
                    detail=name,
                    metadata={
                        "codigo": code,
                        "categoria_id":
                            category_id,
                        "categoria_codigo":
                            category["codigo"],
                        "categoria_nombre":
                            category["nombre"],
                    },
                    trace_id=trace_id,
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    service["audit_event_id"] = audit["id"]
    service["trace_id"] = trace_id
    return service


def update_property_service(
    *,
    property_id,
    service_id,
    name,
    actor_id,
    description=None,
    category_id=None,
):
    actor = _actor(
        actor_id=actor_id,
        property_id=property_id,
    )

    name = _required_text(
        name,
        "PROPERTY_SERVICE_NAME_REQUIRED",
        200,
    )

    description = _optional_text(
        description,
    )

    trace_id = str(uuid.uuid4())

    with pool().connection() as connection:
        try:
            with connection.cursor() as cursor:
                category = (
                    _require_active_service_category(
                        cursor,
                        property_id=property_id,
                        category_id=category_id,
                    )
                )

                cursor.execute(
                    """
                    SELECT *
                    FROM property_service_catalog
                    WHERE id=%s
                      AND condominio_id=%s
                    FOR UPDATE
                    """,
                    (
                        service_id,
                        property_id,
                    ),
                )

                before_row = cursor.fetchone()

                if not before_row:
                    raise ValueError(
                        "PROPERTY_SERVICE_NOT_FOUND"
                    )

                before = dict(before_row)

                cursor.execute(
                    """
                    UPDATE property_service_catalog
                    SET
                        nombre=%s,
                        descripcion=%s,
                        categoria_id=%s,
                        actualizado_por=%s,
                        actualizado_en=NOW()
                    WHERE id=%s
                      AND condominio_id=%s
                    RETURNING *
                    """,
                    (
                        name,
                        description,
                        category_id,
                        actor["id"],
                        service_id,
                        property_id,
                    ),
                )

                service = dict(
                    cursor.fetchone()
                )

                audit = _insert_audit(
                    cursor,
                    actor=actor,
                    property_id=property_id,
                    operation_type=(
                        "PROPERTY_SERVICE_UPDATED"
                    ),
                    entity="PROPERTY_SERVICE",
                    entity_id=service_id,
                    previous_status=(
                        "ACTIVO"
                        if before["activo"]
                        else "INACTIVO"
                    ),
                    new_status=(
                        "ACTIVO"
                        if service["activo"]
                        else "INACTIVO"
                    ),
                    detail=name,
                    metadata={
                        "before": {
                            "nombre":
                                before["nombre"],
                            "descripcion":
                                before["descripcion"],
                            "categoria_id":
                                before[
                                    "categoria_id"
                                ],
                        },
                        "after": {
                            "nombre":
                                service["nombre"],
                            "descripcion":
                                service["descripcion"],
                            "categoria_id":
                                service[
                                    "categoria_id"
                                ],
                            "categoria_codigo":
                                category["codigo"],
                            "categoria_nombre":
                                category["nombre"],
                        },
                    },
                    trace_id=trace_id,
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    service["audit_event_id"] = audit["id"]
    service["trace_id"] = trace_id
    return service


def set_property_service_active(
    *,
    property_id,
    service_id,
    active,
    actor_id,
    reason=None,
):
    actor = _actor(
        actor_id=actor_id,
        property_id=property_id,
    )

    reason = _optional_text(reason)
    active = bool(active)
    trace_id = str(uuid.uuid4())

    with pool().connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM property_service_catalog
                    WHERE id=%s
                      AND condominio_id=%s
                    FOR UPDATE
                    """,
                    (
                        service_id,
                        property_id,
                    ),
                )

                row = cursor.fetchone()

                if not row:
                    raise ValueError(
                        "PROPERTY_SERVICE_NOT_FOUND"
                    )

                service = dict(row)
                previous_active = bool(
                    service["activo"]
                )

                cursor.execute(
                    """
                    UPDATE property_service_catalog
                    SET
                        activo=%s,
                        actualizado_por=%s,
                        actualizado_en=NOW()
                    WHERE id=%s
                      AND condominio_id=%s
                    RETURNING *
                    """,
                    (
                        active,
                        actor["id"],
                        service_id,
                        property_id,
                    ),
                )

                service = dict(
                    cursor.fetchone()
                )

                audit = _insert_audit(
                    cursor,
                    actor=actor,
                    property_id=property_id,
                    operation_type=(
                        "PROPERTY_SERVICE_ACTIVATED"
                        if active
                        else
                        "PROPERTY_SERVICE_DEACTIVATED"
                    ),
                    entity="PROPERTY_SERVICE",
                    entity_id=service_id,
                    previous_status=(
                        "ACTIVO"
                        if previous_active
                        else "INACTIVO"
                    ),
                    new_status=(
                        "ACTIVO"
                        if active
                        else "INACTIVO"
                    ),
                    detail=reason,
                    metadata={
                        "codigo": service["codigo"],
                    },
                    trace_id=trace_id,
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    service["audit_event_id"] = audit["id"]
    service["trace_id"] = trace_id
    return service


def create_service_availability(
    *,
    property_id,
    service_id,
    scope_level,
    effective_from,
    actor_id,
    available=True,
    structure_id=None,
    space_id=None,
    inherits=True,
    is_override=False,
    priority=100,
    effective_to=None,
    change_reason=None,
):
    actor = _actor(
        actor_id=actor_id,
        property_id=property_id,
    )

    scope_level = _required_text(
        scope_level,
        "PROPERTY_SERVICE_SCOPE_REQUIRED",
        20,
    ).upper()

    if scope_level not in SCOPE_LEVELS:
        raise ValueError(
            "PROPERTY_SERVICE_SCOPE_INVALID"
        )

    if scope_level == "INMUEBLE":
        structure_id = None
        space_id = None

    elif scope_level == "ESTRUCTURA":
        if structure_id is None:
            raise ValueError(
                "PROPERTY_SERVICE_STRUCTURE_REQUIRED"
            )
        space_id = None

    elif scope_level == "ESPACIO":
        if space_id is None:
            raise ValueError(
                "PROPERTY_SERVICE_SPACE_REQUIRED"
            )

    priority = int(priority)

    if priority < 0:
        raise ValueError(
            "PROPERTY_SERVICE_PRIORITY_INVALID"
        )

    if (
        effective_to is not None
        and effective_to < effective_from
    ):
        raise ValueError(
            "PROPERTY_SERVICE_DATES_INVALID"
        )

    change_reason = _optional_text(
        change_reason,
    )

    trace_id = str(uuid.uuid4())

    with pool().connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id
                    FROM property_service_catalog
                    WHERE id=%s
                      AND condominio_id=%s
                    """,
                    (
                        service_id,
                        property_id,
                    ),
                )

                if not cursor.fetchone():
                    raise ValueError(
                        "PROPERTY_SERVICE_NOT_FOUND"
                    )

                cursor.execute(
                    """
                    INSERT INTO
                        property_service_availability(
                            service_id,
                            scope_level,
                            estructura_id,
                            espacio_id,
                            disponible,
                            hereda,
                            es_override,
                            prioridad,
                            vigente_desde,
                            vigente_hasta,
                            motivo_cambio,
                            creado_por,
                            actualizado_por
                        )
                    VALUES(
                        %s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s
                    )
                    RETURNING *
                    """,
                    (
                        service_id,
                        scope_level,
                        structure_id,
                        space_id,
                        bool(available),
                        bool(inherits),
                        bool(is_override),
                        priority,
                        effective_from,
                        effective_to,
                        change_reason,
                        actor["id"],
                        actor["id"],
                    ),
                )

                availability = dict(
                    cursor.fetchone()
                )

                audit = _insert_audit(
                    cursor,
                    actor=actor,
                    property_id=property_id,
                    operation_type=(
                        "PROPERTY_SERVICE_"
                        "AVAILABILITY_CREATED"
                    ),
                    entity=(
                        "PROPERTY_SERVICE_"
                        "AVAILABILITY"
                    ),
                    entity_id=availability["id"],
                    new_status=(
                        "DISPONIBLE"
                        if available
                        else "NO_DISPONIBLE"
                    ),
                    detail=change_reason,
                    metadata={
                        "service_id": service_id,
                        "scope_level": scope_level,
                        "estructura_id":
                            structure_id,
                        "espacio_id": space_id,
                        "hereda": bool(inherits),
                        "es_override":
                            bool(is_override),
                        "prioridad": priority,
                        "vigente_desde":
                            effective_from,
                        "vigente_hasta":
                            effective_to,
                    },
                    trace_id=trace_id,
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    availability["audit_event_id"] = (
        audit["id"]
    )
    availability["trace_id"] = trace_id
    return availability
