from core.db import pool
from services.property_service_commands import (
    _actor,
    _insert_audit,
    _optional_text,
    _required_text,
)


def create_service_category(
    *,
    property_id,
    code,
    name,
    actor_id,
    description=None,
    order=100,
):
    actor = _actor(
        actor_id=actor_id,
        property_id=property_id,
    )

    code = _required_text(
        code,
        "PROPERTY_SERVICE_CATEGORY_CODE_REQUIRED",
        100,
    ).upper()

    name = _required_text(
        name,
        "PROPERTY_SERVICE_CATEGORY_NAME_REQUIRED",
        160,
    )

    description = _optional_text(description)
    order = int(order)

    if order < 0:
        raise ValueError(
            "PROPERTY_SERVICE_CATEGORY_ORDER_INVALID"
        )

    with pool().connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO property_service_categories(
                        condominio_id,
                        codigo,
                        nombre,
                        descripcion,
                        orden,
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
                        order,
                        actor["id"],
                        actor["id"],
                    ),
                )

                category = dict(
                    cursor.fetchone()
                )

                audit = _insert_audit(
                    cursor,
                    actor=actor,
                    property_id=property_id,
                    operation_type=(
                        "PROPERTY_SERVICE_CATEGORY_CREATED"
                    ),
                    entity=(
                        "PROPERTY_SERVICE_CATEGORY"
                    ),
                    entity_id=category["id"],
                    new_status="ACTIVO",
                    detail=name,
                    metadata={
                        "codigo": code,
                        "orden": order,
                    },
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    category["audit_event_id"] = audit["id"]
    return category


def update_service_category(
    *,
    property_id,
    category_id,
    name,
    actor_id,
    description=None,
    order=100,
):
    actor = _actor(
        actor_id=actor_id,
        property_id=property_id,
    )

    name = _required_text(
        name,
        "PROPERTY_SERVICE_CATEGORY_NAME_REQUIRED",
        160,
    )

    description = _optional_text(description)
    order = int(order)

    if order < 0:
        raise ValueError(
            "PROPERTY_SERVICE_CATEGORY_ORDER_INVALID"
        )

    with pool().connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM property_service_categories
                    WHERE id=%s
                      AND condominio_id=%s
                    FOR UPDATE
                    """,
                    (
                        category_id,
                        property_id,
                    ),
                )

                before_row = cursor.fetchone()

                if not before_row:
                    raise ValueError(
                        "PROPERTY_SERVICE_CATEGORY_NOT_FOUND"
                    )

                before = dict(before_row)

                cursor.execute(
                    """
                    UPDATE property_service_categories
                    SET
                        nombre=%s,
                        descripcion=%s,
                        orden=%s,
                        actualizado_por=%s,
                        actualizado_en=NOW()
                    WHERE id=%s
                      AND condominio_id=%s
                    RETURNING *
                    """,
                    (
                        name,
                        description,
                        order,
                        actor["id"],
                        category_id,
                        property_id,
                    ),
                )

                category = dict(
                    cursor.fetchone()
                )

                audit = _insert_audit(
                    cursor,
                    actor=actor,
                    property_id=property_id,
                    operation_type=(
                        "PROPERTY_SERVICE_CATEGORY_UPDATED"
                    ),
                    entity=(
                        "PROPERTY_SERVICE_CATEGORY"
                    ),
                    entity_id=category_id,
                    previous_status=(
                        "ACTIVO"
                        if before["activo"]
                        else "INACTIVO"
                    ),
                    new_status=(
                        "ACTIVO"
                        if category["activo"]
                        else "INACTIVO"
                    ),
                    detail=name,
                    metadata={
                        "before": {
                            "nombre": before["nombre"],
                            "descripcion": (
                                before["descripcion"]
                            ),
                            "orden": before["orden"],
                        },
                        "after": {
                            "nombre": category["nombre"],
                            "descripcion": (
                                category["descripcion"]
                            ),
                            "orden": category["orden"],
                        },
                    },
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    category["audit_event_id"] = audit["id"]
    return category


def set_service_category_active(
    *,
    property_id,
    category_id,
    active,
    actor_id,
    reason=None,
):
    actor = _actor(
        actor_id=actor_id,
        property_id=property_id,
    )

    active = bool(active)
    reason = _optional_text(reason)

    with pool().connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM property_service_categories
                    WHERE id=%s
                      AND condominio_id=%s
                    FOR UPDATE
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

                category = dict(row)
                previous_active = bool(
                    category["activo"]
                )

                cursor.execute(
                    """
                    UPDATE property_service_categories
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
                        category_id,
                        property_id,
                    ),
                )

                category = dict(
                    cursor.fetchone()
                )

                audit = _insert_audit(
                    cursor,
                    actor=actor,
                    property_id=property_id,
                    operation_type=(
                        "PROPERTY_SERVICE_CATEGORY_ACTIVATED"
                        if active
                        else
                        "PROPERTY_SERVICE_CATEGORY_DEACTIVATED"
                    ),
                    entity=(
                        "PROPERTY_SERVICE_CATEGORY"
                    ),
                    entity_id=category_id,
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
                        "codigo": category["codigo"],
                    },
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    category["audit_event_id"] = audit["id"]
    return category
