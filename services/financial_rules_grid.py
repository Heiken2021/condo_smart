from core.authorization import authorize
from core.db import fetch_all, fetch_one


GOVERNANCE_READ_PERMISSION = (
    "FINANZAS_GOBIERNO_CONSULTAR"
)


def _require_read(
    user,
    property_id,
):
    decision = authorize(
        user,
        GOVERNANCE_READ_PERMISSION,
        property_id,
    )

    if not decision.allowed:
        raise PermissionError(
            GOVERNANCE_READ_PERMISSION
        )


def _property_context(
    property_id,
):
    row = fetch_one(
        """
        SELECT
            id,
            clave,
            nombre,
            tipo_codigo,
            activo
        FROM condominios
        WHERE id=%s
        """,
        (property_id,),
    )

    if not row:
        raise ValueError(
            "FINANCIAL_PROPERTY_NOT_FOUND"
        )

    return dict(row)


def _scope_label(row):
    level = (
        row.get("scope_level")
        or "CORE"
    )

    if level == "ESPACIO":
        return (
            row.get("space_key")
            or f"Espacio {row.get('espacio_id')}"
        )

    if level == "ESTRUCTURA":
        return (
            row.get("structure_name")
            or f"Estructura "
            f"{row.get('estructura_id')}"
        )

    if level == "INMUEBLE":
        return (
            row.get("property_name")
            or "Inmueble"
        )

    return "Core"


def _applicability_map(
    definition_ids,
):
    if not definition_ids:
        return {}

    rows = fetch_all(
        """
        SELECT
            rule_definition_id,
            dimension_codigo,
            valor_codigo,
            incluido
        FROM financial_rule_applicability
        WHERE rule_definition_id = ANY(%s)
        ORDER BY
            rule_definition_id,
            dimension_codigo,
            valor_codigo
        """,
        (list(definition_ids),),
    )

    result = {}

    for row in rows:
        result.setdefault(
            row["rule_definition_id"],
            [],
        ).append(
            {
                "dimension": (
                    row["dimension_codigo"]
                ),
                "value": row["valor_codigo"],
                "included": row["incluido"],
            }
        )

    return result


def _applicability_label(items):
    if not items:
        return "General"

    included = [
        (
            f"{item['dimension']}:"
            f"{item['value']}"
        )
        for item in items
        if item["included"]
    ]

    excluded = [
        (
            f"Excepto "
            f"{item['dimension']}:"
            f"{item['value']}"
        )
        for item in items
        if not item["included"]
    ]

    return " · ".join(
        included + excluded
    ) or "General"


def _definition_matches_property(
    items,
    property_context,
):
    if not items:
        return True

    property_type = str(
        property_context.get(
            "tipo_codigo"
        )
        or ""
    ).upper()

    relevant = [
        item
        for item in items
        if item["dimension"] in {
            "TIPO_INMUEBLE",
            "NATURALEZA_INMUEBLE",
        }
    ]

    if not relevant:
        return True

    includes = [
        item
        for item in relevant
        if item["included"]
    ]

    excludes = [
        item
        for item in relevant
        if not item["included"]
    ]

    for item in excludes:
        if (
            str(item["value"]).upper()
            == property_type
        ):
            return False

    if not includes:
        return True

    return any(
        str(item["value"]).upper()
        == property_type
        for item in includes
    )


def list_financial_rule_grid(
    *,
    property_id,
    user,
    domain=None,
    status=None,
    scope_level=None,
    include_available=True,
):
    _require_read(
        user,
        property_id,
    )

    property_context = (
        _property_context(
            property_id
        )
    )

    rows = fetch_all(
        """
        SELECT
            definition.id
                AS definition_id,
            definition.codigo
                AS definition_code,
            definition.nombre
                AS definition_name,
            definition.descripcion
                AS definition_description,
            definition.dominio_codigo,
            definition.nivel_base_codigo,
            definition.tipo_resultado,
            definition.esquema_parametros,
            definition.obligatoria,
            definition.admite_especializacion,
            definition.admite_herencia,
            definition.admite_override,
            definition.admite_excepcion,
            definition.requiere_aprobacion,
            definition.permite_nivel_inmueble,
            definition.permite_nivel_estructura,
            definition.permite_nivel_espacio,
            definition.contexto_kpi,
            definition.contexto_ia,
            definition.activo
                AS definition_active,

            rule.id AS rule_id,
            rule.scope_level,
            rule.condominio_id,
            rule.estructura_id,
            rule.espacio_id,
            rule.tipo_aplicable_codigo,
            rule.codigo AS rule_code,
            rule.nombre AS rule_name,
            rule.descripcion
                AS rule_description,
            rule.hereda,
            rule.es_override,
            rule.prioridad,
            rule.activo AS rule_active,

            property.nombre
                AS property_name,
            structure.nombre
                AS structure_name,
            space.clave
                AS space_key,

            current_version.id
                AS current_version_id,
            current_version.version_num,
            current_version.vigente_desde,
            current_version.vigente_hasta,
            current_version.estado_codigo,
            current_version.parametros,
            current_version.aprobado_por,
            current_version.aprobado_en,
            current_version.motivo_cambio,

            (
                SELECT COUNT(*)
                FROM financial_rule_versions
                    version_count
                WHERE
                    version_count.rule_id=
                    rule.id
            ) AS version_count,

            (
                SELECT COUNT(*)
                FROM financial_rule_exceptions
                    exception_count
                WHERE
                    exception_count.rule_version_id=
                    current_version.id
                  AND exception_count.estado_codigo
                      IN (
                          'PENDIENTE',
                          'APROBADA'
                      )
            ) AS active_exception_count

        FROM financial_rule_definitions
            definition

        LEFT JOIN financial_rules rule
          ON rule.rule_definition_id=
             definition.id
         AND (
             rule.condominio_id=%s
             OR rule.condominio_id IS NULL
         )

        LEFT JOIN condominios property
          ON property.id=rule.condominio_id

        LEFT JOIN estructura_inmueble
            structure
          ON structure.id=rule.estructura_id

        LEFT JOIN espacios space
          ON space.id=rule.espacio_id

        LEFT JOIN LATERAL (
            SELECT version.*
            FROM financial_rule_versions
                version
            WHERE version.rule_id=rule.id
            ORDER BY
                CASE
                    WHEN
                        version.estado_codigo=
                        'APROBADO'
                    THEN 0
                    ELSE 1
                END,
                version.version_num DESC,
                version.id DESC
            LIMIT 1
        ) current_version
          ON TRUE

        WHERE definition.activo=TRUE

        ORDER BY
            definition.dominio_codigo,
            definition.nombre,
            rule.prioridad DESC NULLS LAST,
            rule.id
        """,
        (property_id,),
    )

    definition_ids = {
        row["definition_id"]
        for row in rows
    }

    applicability = (
        _applicability_map(
            definition_ids
        )
    )

    result = []

    for source in rows:
        row = dict(source)

        applicability_items = (
            applicability.get(
                row["definition_id"],
                [],
            )
        )

        if not _definition_matches_property(
            applicability_items,
            property_context,
        ):
            continue

        configured = (
            row.get("rule_id")
            is not None
        )

        if (
            not include_available
            and not configured
        ):
            continue

        row_domain = (
            row.get("dominio_codigo")
            or ""
        )

        row_status = (
            row.get("estado_codigo")
            or (
                "SIN_CONFIGURAR"
                if not configured
                else "SIN_VERSION"
            )
        )

        row_scope = (
            row.get("scope_level")
            or "CORE"
        )

        if (
            domain
            and row_domain != domain
        ):
            continue

        if (
            status
            and row_status != status
        ):
            continue

        if (
            scope_level
            and row_scope != scope_level
        ):
            continue

        result.append(
            {
                **row,
                "configured": configured,
                "display_code": (
                    row.get("rule_code")
                    or row[
                        "definition_code"
                    ]
                ),
                "display_name": (
                    row.get("rule_name")
                    or row[
                        "definition_name"
                    ]
                ),
                "display_description": (
                    row.get(
                        "rule_description"
                    )
                    or row.get(
                        "definition_description"
                    )
                ),
                "status": row_status,
                "scope": row_scope,
                "scope_label": (
                    _scope_label(row)
                ),
                "applicability": (
                    applicability_items
                ),
                "applicability_label": (
                    _applicability_label(
                        applicability_items
                    )
                ),
                "property_type": (
                    property_context.get(
                        "tipo_codigo"
                    )
                ),
                "version_label": (
                    (
                        f"v{row['version_num']}"
                    )
                    if row.get(
                        "version_num"
                    ) is not None
                    else "Sin versión"
                ),
                "inheritance_label": (
                    "Hereda"
                    if row.get("hereda")
                    else "No hereda"
                ),
                "override_label": (
                    "Override"
                    if row.get(
                        "es_override"
                    )
                    else "Base"
                ),
                "kpi_enabled": bool(
                    row.get("contexto_kpi")
                ),
                "ai_enabled": bool(
                    row.get("contexto_ia")
                ),
            }
        )

    return result


def get_financial_rule_detail(
    *,
    property_id,
    user,
    definition_id,
    rule_id=None,
):
    rows = list_financial_rule_grid(
        property_id=property_id,
        user=user,
        include_available=True,
    )

    for row in rows:
        if (
            row["definition_id"]
            != definition_id
        ):
            continue

        if (
            rule_id is not None
            and row.get("rule_id")
            != rule_id
        ):
            continue

        versions = []

        if row.get("rule_id"):
            versions = [
                dict(version)
                for version in fetch_all(
                    """
                    SELECT *
                    FROM financial_rule_versions
                    WHERE rule_id=%s
                    ORDER BY
                        version_num DESC,
                        id DESC
                    """,
                    (row["rule_id"],),
                )
            ]

        exceptions = []

        if versions:
            version_ids = [
                version["id"]
                for version in versions
            ]

            exceptions = [
                dict(exception)
                for exception in fetch_all(
                    """
                    SELECT *
                    FROM financial_rule_exceptions
                    WHERE rule_version_id
                          = ANY(%s)
                    ORDER BY
                        solicitado_en DESC,
                        id DESC
                    """,
                    (version_ids,),
                )
            ]

        return {
            **row,
            "versions": versions,
            "exceptions": exceptions,
        }

    return None


def list_space_fee_grid(
    *,
    property_id,
    user,
):
    _require_read(
        user,
        property_id,
    )

    return [
        dict(row)
        for row in fetch_all(
            """
            SELECT
                fee.id,
                fee.condominio_id,
                fee.espacio_id,
                space.clave
                    AS space_key,
                space.nombre
                    AS space_name,
                structure.id
                    AS structure_id,
                structure.nombre
                    AS structure_name,
                fee.tipo_cuota_codigo,
                fee.monto_mxn,
                fee.vigente_desde,
                fee.vigente_hasta,
                fee.origen_codigo,
                fee.rule_version_id,
                version.rule_id,
                rule.codigo
                    AS rule_code,
                rule.nombre
                    AS rule_name,
                fee.estado_codigo,
                fee.creado_por,
                fee.aprobado_por,
                fee.aprobado_en,
                fee.motivo_cambio,
                fee.creado_en
            FROM space_fee_history fee
            JOIN espacios space
              ON space.id=fee.espacio_id
             AND space.condominio_id=
                 fee.condominio_id
            LEFT JOIN estructura_inmueble
                structure
              ON structure.id=
                 space.estructura_id
            LEFT JOIN financial_rule_versions
                version
              ON version.id=
                 fee.rule_version_id
            LEFT JOIN financial_rules rule
              ON rule.id=version.rule_id
            WHERE fee.condominio_id=%s
            ORDER BY
                space.clave,
                fee.tipo_cuota_codigo,
                fee.vigente_desde DESC,
                fee.id DESC
            """,
            (property_id,),
        )
    ]


def list_financial_exception_grid(
    *,
    property_id,
    user,
):
    _require_read(
        user,
        property_id,
    )

    return [
        dict(row)
        for row in fetch_all(
            """
            SELECT
                exception.*,
                definition.codigo
                    AS definition_code,
                definition.nombre
                    AS definition_name,
                rule.codigo AS rule_code,
                rule.nombre AS rule_name,
                version.version_num,
                structure.nombre
                    AS structure_name,
                space.clave AS space_key
            FROM financial_rule_exceptions
                exception
            JOIN financial_rule_versions
                version
              ON version.id=
                 exception.rule_version_id
            JOIN financial_rules rule
              ON rule.id=version.rule_id
            JOIN financial_rule_definitions
                definition
              ON definition.id=
                 rule.rule_definition_id
            LEFT JOIN estructura_inmueble
                structure
              ON structure.id=
                 exception.estructura_id
            LEFT JOIN espacios space
              ON space.id=
                 exception.espacio_id
            WHERE exception.condominio_id=%s
            ORDER BY
                exception.solicitado_en DESC,
                exception.id DESC
            """,
            (property_id,),
        )
    ]
