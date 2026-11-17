from core.db import fetch_all


_OPERATION_LABELS = {
    "FINANCIAL_RULE_CREATED": (
        "Configuración de regla creada"
    ),
    "FINANCIAL_RULE_VERSION_CREATED": (
        "Versión creada"
    ),
    "FINANCIAL_RULE_VERSION_DRAFT_UPDATED": (
        "Borrador actualizado"
    ),
    "FINANCIAL_RULE_VERSION_APPROVED": (
        "Versión aprobada"
    ),
    "FINANCIAL_RULE_VERSION_CLOSED": (
        "Vigencia finalizada"
    ),
    "FINANCIAL_RULE_EXCEPTION_CREATED": (
        "Excepción creada"
    ),
    "FINANCIAL_RULE_EXCEPTION_APPROVED": (
        "Excepción aprobada"
    ),
}


def financial_audit_operation_label(
    operation_type,
):
    return _OPERATION_LABELS.get(
        operation_type,
        operation_type,
    )


def _metadata(event):
    value = event.get("metadata")
    return value if isinstance(value, dict) else {}


def _version_label(metadata):
    version_num = metadata.get("version_num")

    if version_num is None:
        return "Regla"

    return f"Versión v{version_num}"


def _state_transition(event):
    previous = event.get("estado_anterior")
    current = event.get("estado_nuevo")

    if previous and current:
        if previous == current:
            return current.title()

        return (
            f"{previous.title()} → "
            f"{current.title()}"
        )

    if current:
        return current.title()

    if previous:
        return previous.title()

    return "Sin cambio de estado"


def _dependency_summary(metadata):
    dependencies = (
        metadata.get("resolved_dependencies")
        or []
    )

    result = []

    for dependency in dependencies:
        if not isinstance(dependency, dict):
            continue

        source = (
            dependency.get("source_rule_name")
            or dependency.get("source_rule_code")
            or "Política fuente"
        )

        criterion = (
            dependency.get("criterion_label")
            or dependency.get("criterion_code")
            or "Criterio gobernado"
        )

        version_num = dependency.get(
            "source_version_num"
        )

        version = (
            f"v{version_num}"
            if version_num is not None
            else "versión no identificada"
        )

        result.append(
            f"{criterion}: {source} ({version})"
        )

    return result


def list_financial_rule_audit_events(
    *,
    property_id,
    rule_id,
):
    rows = fetch_all(
        """
        SELECT
            audit.id,
            audit.fecha,
            audit.usuario_id,
            audit.username,
            audit.tipo_operacion,
            audit.entidad,
            audit.entidad_id,
            audit.estado_anterior,
            audit.estado_nuevo,
            audit.detalle,
            audit.metadata,
            audit.trace_id
        FROM auditoria_financiera audit
        WHERE audit.condominio_id=%s
          AND (
              (
                  audit.entidad='FINANCIAL_RULE'
                  AND audit.entidad_id=%s
              )
              OR (
                  audit.entidad IN (
                      'FINANCIAL_RULE_VERSION',
                      'FINANCIAL_RULE_EXCEPTION'
                  )
                  AND audit.metadata->>'rule_id'=%s
              )
          )
        ORDER BY audit.fecha DESC, audit.id DESC
        """,
        (
            property_id,
            rule_id,
            str(rule_id),
        ),
    )

    return [dict(row) for row in rows]


def financial_rule_audit_rows(
    *,
    property_id,
    rule_id,
):
    events = list_financial_rule_audit_events(
        property_id=property_id,
        rule_id=rule_id,
    )

    result = []

    for event in events:
        metadata = _metadata(event)

        result.append(
            {
                "id": event["id"],
                "fecha": event["fecha"],
                "evento": (
                    financial_audit_operation_label(
                        event["tipo_operacion"]
                    )
                ),
                "version": _version_label(metadata),
                "actor": (
                    event.get("username")
                    or (
                        f"Usuario "
                        f"{event['usuario_id']}"
                        if event.get("usuario_id")
                        is not None
                        else "Sistema"
                    )
                ),
                "transicion": (
                    _state_transition(event)
                ),
                "motivo": (
                    event.get("detalle")
                    or "Sin motivo registrado"
                ),
                "dependencias": (
                    _dependency_summary(metadata)
                ),
                "trace_id": (
                    event.get("trace_id")
                    or "Sin identificador"
                ),
            }
        )

    return result
