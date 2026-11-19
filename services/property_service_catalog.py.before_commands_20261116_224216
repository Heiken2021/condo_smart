from datetime import date

from core.db import fetch_all, fetch_one


TREATMENT_LABELS = {
    "MANTENER": "Mantener disponible",
    "LIMITAR": "Aplicar restricción parcial",
    "BLOQUEAR": "Bloquear temporalmente",
}


def service_treatment_label(code):
    return TREATMENT_LABELS.get(
        code,
        code,
    )


def list_property_services(
    *,
    property_id,
    active_only=True,
):
    active_filter = (
        " AND service.activo=TRUE"
        if active_only
        else ""
    )

    rows = fetch_all(
        f"""
        SELECT
            service.id,
            service.condominio_id,
            service.codigo,
            service.nombre,
            service.descripcion,
            service.categoria_codigo,
            service.activo,
            service.creado_en,
            service.actualizado_en
        FROM property_service_catalog service
        WHERE service.condominio_id=%s
        {active_filter}
        ORDER BY
            service.nombre,
            service.id
        """,
        (property_id,),
    )

    return [dict(row) for row in rows]


def get_property_service(
    *,
    property_id,
    service_id,
):
    row = fetch_one(
        """
        SELECT
            service.id,
            service.condominio_id,
            service.codigo,
            service.nombre,
            service.descripcion,
            service.categoria_codigo,
            service.activo,
            service.creado_en,
            service.actualizado_en
        FROM property_service_catalog service
        WHERE service.id=%s
          AND service.condominio_id=%s
        """,
        (
            service_id,
            property_id,
        ),
    )

    return dict(row) if row else None


def list_service_availability(
    *,
    property_id,
    service_id=None,
    effective_date=None,
):
    effective_date = effective_date or date.today()

    service_filter = ""
    params = [
        property_id,
        effective_date,
        effective_date,
    ]

    if service_id is not None:
        service_filter = (
            " AND availability.service_id=%s"
        )
        params.append(service_id)

    rows = fetch_all(
        f"""
        SELECT
            availability.id,
            availability.service_id,
            service.codigo AS service_code,
            service.nombre AS service_name,
            availability.scope_level,
            availability.estructura_id,
            availability.espacio_id,
            availability.disponible,
            availability.hereda,
            availability.es_override,
            availability.prioridad,
            availability.vigente_desde,
            availability.vigente_hasta,
            availability.motivo_cambio
        FROM property_service_availability
            availability
        JOIN property_service_catalog service
          ON service.id=availability.service_id
        WHERE service.condominio_id=%s
          AND service.activo=TRUE
          AND availability.vigente_desde<=%s
          AND (
              availability.vigente_hasta IS NULL
              OR availability.vigente_hasta>=%s
          )
          {service_filter}
        ORDER BY
            availability.service_id,
            CASE availability.scope_level
                WHEN 'ESPACIO' THEN 3
                WHEN 'ESTRUCTURA' THEN 2
                WHEN 'INMUEBLE' THEN 1
                ELSE 0
            END DESC,
            availability.prioridad DESC,
            availability.id DESC
        """,
        tuple(params),
    )

    return [dict(row) for row in rows]


def list_continuity_service_policy(
    *,
    property_id,
    rule_version_id,
    active_only=True,
):
    active_filter = (
        " AND policy.activo=TRUE"
        if active_only
        else ""
    )

    rows = fetch_all(
        f"""
        SELECT
            policy.id,
            policy.rule_version_id,
            policy.service_id,
            service.codigo AS service_code,
            service.nombre AS service_name,
            service.descripcion AS service_description,
            policy.treatment_code,
            policy.restriction_detail,
            policy.restoration_detail,
            policy.prioridad,
            policy.activo
        FROM continuity_service_policy policy
        JOIN property_service_catalog service
          ON service.id=policy.service_id
        JOIN financial_rule_versions version
          ON version.id=policy.rule_version_id
        JOIN financial_rules rule
          ON rule.id=version.rule_id
        JOIN financial_rule_definitions definition
          ON definition.id=rule.rule_definition_id
        WHERE policy.rule_version_id=%s
          AND service.condominio_id=%s
          AND rule.condominio_id=%s
          AND definition.codigo=
              'CONTINUIDAD_SERVICIOS'
          {active_filter}
        ORDER BY
            policy.prioridad DESC,
            service.nombre,
            policy.id
        """,
        (
            rule_version_id,
            property_id,
            property_id,
        ),
    )

    result = []

    for row in rows:
        item = dict(row)
        item["treatment_label"] = (
            service_treatment_label(
                item["treatment_code"]
            )
        )
        result.append(item)

    return result


def continuity_service_policy_rows(
    *,
    property_id,
    rule_version_id,
):
    policy = list_continuity_service_policy(
        property_id=property_id,
        rule_version_id=rule_version_id,
    )

    return [
        {
            "Servicio": item["service_name"],
            "Tratamiento": (
                item["treatment_label"]
            ),
            "Detalle de restricción": (
                item["restriction_detail"]
                or "Sin detalle adicional"
            ),
            "Criterio de restitución": (
                item["restoration_detail"]
                or (
                    "Se determina por la regla "
                    "gobernada vigente"
                )
            ),
            "Prioridad": item["prioridad"],
        }
        for item in policy
    ]
