import re

from core.db import fetch_all, fetch_one


def list_service_categories(
    *,
    property_id,
    active_only=True,
):
    active_filter = (
        " AND category.activo=TRUE"
        if active_only
        else ""
    )

    rows = fetch_all(
        f"""
        SELECT
            category.id,
            category.condominio_id,
            category.codigo,
            category.nombre,
            category.descripcion,
            category.orden,
            category.activo
        FROM property_service_categories category
        WHERE category.condominio_id=%s
        {active_filter}
        ORDER BY
            category.orden,
            category.nombre,
            category.id
        """,
        (property_id,),
    )

    return [dict(row) for row in rows]


def get_service_category(
    *,
    property_id,
    category_id,
):
    row = fetch_one(
        """
        SELECT
            id,
            condominio_id,
            codigo,
            nombre,
            descripcion,
            orden,
            activo
        FROM property_service_categories
        WHERE id=%s
          AND condominio_id=%s
        """,
        (
            category_id,
            property_id,
        ),
    )

    return dict(row) if row else None


def suggest_service_code(
    *,
    property_id,
):
    property_row = fetch_one(
        """
        SELECT clave
        FROM condominios
        WHERE id=%s
        """,
        (property_id,),
    )

    if not property_row:
        raise ValueError(
            "PROPERTY_NOT_FOUND"
        )

    prefix = str(
        property_row["clave"]
    ).strip()

    if not prefix:
        raise ValueError(
            "PROPERTY_KEY_REQUIRED"
        )

    rows = fetch_all(
        """
        SELECT codigo
        FROM property_service_catalog
        WHERE condominio_id=%s
        ORDER BY id
        """,
        (property_id,),
    )

    pattern = re.compile(
        "^"
        + re.escape(prefix)
        + r"-S(\d+)$"
    )

    maximum = 0

    for row in rows:
        match = pattern.match(
            str(row["codigo"] or "")
        )

        if match:
            maximum = max(
                maximum,
                int(match.group(1)),
            )

    sequence = maximum + 1

    return (
        f"{prefix}-S{sequence:03d}"
    )
