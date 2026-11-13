import json
import uuid

from core.authorization import authorize
from core.db import execute, fetch_all


SENSITIVE_KEYS = {
    "password",
    "password_hash",
    "salt",
    "token",
    "token_hash",
    "api_key",
    "secret",
    "smtp_password",
    "database_url",
    "openai_api_key",
    "authorization",
    "session",
}


def _sensitive(key):
    value = str(key or "").lower()

    return any(
        token in value
        for token in SENSITIVE_KEYS
    )


def sanitize(value):
    if value is None:
        return None

    if isinstance(value, dict):
        result = {}

        for key, item in value.items():
            if _sensitive(key):
                result[key] = "[REDACTED]"
            else:
                result[key] = sanitize(item)

        return result

    if isinstance(value, (list, tuple)):
        return [sanitize(item) for item in value]

    return value


def new_trace_id():
    return uuid.uuid4().hex


def serialize(value):
    sanitized = sanitize(value)

    if sanitized is None:
        return None

    return json.dumps(
        sanitized,
        default=str,
        ensure_ascii=False,
    )


SYSTEM_CRITICAL_TOKENS = (
    "ELIMINAR",
    "DELETE",
    "DENEG",
    "UNAUTHORIZED",
    "FORBIDDEN",
    "ACCESS_DENIED",
    "PERMISSION_DENIED",
    "AUTHORIZATION_FAILED",

    "ROOT_DELEGADO_ASIGNAR",
    "ROOT_DELEGADO_REVOCAR",
    "ROOT_PRIVILEGE_DENIED",
    "ROOT_PRINCIPAL_PROTECTED",)

SYSTEM_WARNING_TOKENS = (
    "REVOCAR",
    "DESACTIVAR",
    "CONFIGURACION",
    "PERMISO",
    "PASSWORD",
    "RECOVERY",
    "SEGURIDAD",
)

FINANCIAL_CRITICAL_TOKENS = (
    "REVERS",
    "CANCEL",
    "ANUL",
)

FINANCIAL_WARNING_TOKENS = (
    "AJUST",
    "CORRECC",
    "MODIFIC",
)


def _contains_any(value, tokens):
    text = str(value or "").upper()
    return any(token in text for token in tokens)


def system_severity(row):
    result = str(row.get("resultado") or "OK").upper()

    action = row.get("accion")
    detail = row.get("detalle")

    if result not in {"OK", "SUCCESS"}:
        return "CRITICO"

    if (
        _contains_any(action, SYSTEM_CRITICAL_TOKENS)
        or _contains_any(detail, SYSTEM_CRITICAL_TOKENS)
    ):
        return "CRITICO"

    if (
        _contains_any(action, SYSTEM_WARNING_TOKENS)
        or _contains_any(detail, SYSTEM_WARNING_TOKENS)
    ):
        return "ATENCION"

    return "NORMAL"


def financial_severity(row):
    operation = row.get("tipo_operacion")
    previous_status = row.get("estado_anterior")
    new_status = row.get("estado_nuevo")

    values = (
        operation,
        previous_status,
        new_status,
    )

    if any(
        _contains_any(
            value,
            FINANCIAL_CRITICAL_TOKENS,
        )
        for value in values
    ):
        return "CRITICO"

    if any(
        _contains_any(
            value,
            FINANCIAL_WARNING_TOKENS,
        )
        for value in values
    ):
        return "ATENCION"

    return "NORMAL"


def _system_reason(row):
    result = str(
        row.get("resultado") or "OK"
    ).upper()

    action = str(
        row.get("accion") or ""
    )

    detail = str(
        row.get("detalle") or ""
    )

    if result not in {"OK", "SUCCESS"}:
        return (
            "El evento tiene un resultado distinto "
            "de OK/SUCCESS."
        )

    if _contains_any(
        action,
        SYSTEM_CRITICAL_TOKENS,
    ):
        return (
            "La acción pertenece a una categoría "
            "administrativa o de seguridad "
            "clasificada como crítica."
        )

    if _contains_any(
        detail,
        SYSTEM_CRITICAL_TOKENS,
    ):
        return (
            "El detalle del evento contiene un "
            "indicador crítico de seguridad."
        )

    if _contains_any(
        action,
        SYSTEM_WARNING_TOKENS,
    ):
        return (
            "La acción corresponde a una operación "
            "sensible que requiere revisión."
        )

    if _contains_any(
        detail,
        SYSTEM_WARNING_TOKENS,
    ):
        return (
            "El detalle contiene un indicador que "
            "requiere atención."
        )

    return (
        "El evento terminó correctamente y no "
        "activó reglas de atención o criticidad."
    )


def _financial_reason(row):
    operation = str(
        row.get("tipo_operacion") or ""
    )

    previous_status = str(
        row.get("estado_anterior") or ""
    )

    new_status = str(
        row.get("estado_nuevo") or ""
    )

    values = (
        operation,
        previous_status,
        new_status,
    )

    if any(
        _contains_any(
            value,
            FINANCIAL_CRITICAL_TOKENS,
        )
        for value in values
    ):
        return (
            "La operación contiene una cancelación, "
            "anulación o reversión, clasificada como "
            "evento financiero crítico."
        )

    if any(
        _contains_any(
            value,
            FINANCIAL_WARNING_TOKENS,
        )
        for value in values
    ):
        return (
            "La operación corresponde a un ajuste, "
            "corrección o modificación que requiere "
            "revisión."
        )

    return (
        "El movimiento no activó reglas financieras "
        "de revisión o criticidad."
    )


def system_status_explanation(rows):
    severity = overall_severity(
        rows,
        system_severity,
    )

    classified = [
        (
            row,
            system_severity(row),
            _system_reason(row),
        )
        for row in rows
    ]

    critical = [
        item
        for item in classified
        if item[1] == "CRITICO"
    ]

    warning = [
        item
        for item in classified
        if item[1] == "ATENCION"
    ]

    if severity == "CRITICO":
        trigger = critical[0]

        action = (
            trigger[0].get("accion")
            or "Evento sin acción identificada"
        )

        return {
            "severity": severity,
            "summary": (
                f"Se detectaron {len(critical)} "
                f"evento(s) críticos y "
                f"{len(warning)} evento(s) que "
                "requieren atención."
            ),
            "reason": trigger[2],
            "trigger": str(action),
            "criteria": (
                "El estado cambia a Crítico cuando "
                "existe al menos un evento con "
                "resultado fallido, acceso denegado, "
                "fallo de autorización o una acción "
                "administrativa clasificada como "
                "crítica por las reglas actuales."
            ),
            "recommendation": (
                "Revisa primero los eventos en rojo, "
                "confirma el usuario, la acción y el "
                "registro afectado, y determina si "
                "la operación era esperada."
            ),
        }

    if severity == "ATENCION":
        trigger = warning[0]

        action = (
            trigger[0].get("accion")
            or "Evento sin acción identificada"
        )

        return {
            "severity": severity,
            "summary": (
                f"No existen eventos críticos. "
                f"Se detectaron {len(warning)} "
                "evento(s) que requieren atención."
            ),
            "reason": trigger[2],
            "trigger": str(action),
            "criteria": (
                "El estado cambia a Atención cuando "
                "no existen incidentes críticos, pero "
                "sí revocaciones, desactivaciones, "
                "cambios de configuración, permisos "
                "u otras operaciones sensibles."
            ),
            "recommendation": (
                "Revisa los eventos amarillos y "
                "confirma que los cambios sensibles "
                "correspondan a operaciones "
                "autorizadas."
            ),
        }

    return {
        "severity": "NORMAL",
        "summary": (
            "No se detectaron eventos críticos ni "
            "eventos que requieran atención según "
            "las reglas activas."
        ),
        "reason": (
            "Los eventos evaluados finalizaron "
            "correctamente y no activaron reglas "
            "de riesgo."
        ),
        "trigger": "Ninguno",
        "criteria": (
            "El estado permanece Normal mientras "
            "no exista ningún evento clasificado "
            "como Atención o Crítico."
        ),
        "recommendation": (
            "No se requiere una acción inmediata. "
            "Mantén la supervisión periódica de la "
            "actividad."
        ),
    }


def financial_status_explanation(rows):
    severity = overall_severity(
        rows,
        financial_severity,
    )

    classified = [
        (
            row,
            financial_severity(row),
            _financial_reason(row),
        )
        for row in rows
    ]

    critical = [
        item
        for item in classified
        if item[1] == "CRITICO"
    ]

    warning = [
        item
        for item in classified
        if item[1] == "ATENCION"
    ]

    if severity == "CRITICO":
        trigger = critical[0]

        operation = (
            trigger[0].get("tipo_operacion")
            or "Movimiento sin tipo identificado"
        )

        return {
            "severity": severity,
            "summary": (
                f"Se detectaron {len(critical)} "
                "movimiento(s) financieros críticos "
                f"y {len(warning)} movimiento(s) "
                "para revisión."
            ),
            "reason": trigger[2],
            "trigger": str(operation),
            "criteria": (
                "El estado cambia a Crítico cuando "
                "el ledger contiene una cancelación, "
                "anulación o reversión conforme a "
                "las reglas financieras actuales."
            ),
            "recommendation": (
                "Revisa la operación original y su "
                "secuencia de eventos relacionados "
                "antes de cerrar la incidencia."
            ),
        }

    if severity == "ATENCION":
        trigger = warning[0]

        operation = (
            trigger[0].get("tipo_operacion")
            or "Movimiento sin tipo identificado"
        )

        return {
            "severity": severity,
            "summary": (
                "No existen movimientos financieros "
                "críticos. "
                f"Se detectaron {len(warning)} "
                "movimiento(s) para revisión."
            ),
            "reason": trigger[2],
            "trigger": str(operation),
            "criteria": (
                "El estado cambia a Revisión cuando "
                "existen ajustes, correcciones o "
                "modificaciones y no existe alguna "
                "regla crítica activa."
            ),
            "recommendation": (
                "Comprueba que los ajustes estén "
                "respaldados por la operación de "
                "negocio correspondiente."
            ),
        }

    if not rows:
        summary = (
            "El ledger financiero está activo y "
            "todavía no contiene movimientos."
        )
    else:
        summary = (
            "Los movimientos registrados no "
            "activaron reglas financieras de "
            "revisión o criticidad."
        )

    return {
        "severity": "NORMAL",
        "summary": summary,
        "reason": (
            "No existen cancelaciones, anulaciones, "
            "reversiones, ajustes o correcciones "
            "clasificadas por las reglas actuales."
        ),
        "trigger": "Ninguno",
        "criteria": (
            "El estado permanece Normal mientras "
            "ningún movimiento active una regla "
            "financiera de Revisión o Crítico."
        ),
        "recommendation": (
            "No se requiere una acción inmediata. "
            "Mantén la supervisión del ledger."
        ),
    }

def overall_severity(rows, classifier):
    severities = [
        classifier(row)
        for row in rows
    ]

    if "CRITICO" in severities:
        return "CRITICO"

    if "ATENCION" in severities:
        return "ATENCION"

    return "NORMAL"

def list_system_audit(
    user,
    property_id=None,
    limit=500,
):
    if user.get("rol_global") == "SUPERADMIN":
        if property_id:
            return fetch_all(
                """
                SELECT
                    id,fecha,condominio_id,usuario_id,
                    username,accion,entidad,entidad_id,
                    detalle,valor_anterior,valor_nuevo,
                    resultado,modulo,trace_id
                FROM auditoria
                WHERE condominio_id=%s
                ORDER BY fecha DESC
                LIMIT %s
                """,
                (property_id, limit),
            )

        return fetch_all(
            """
            SELECT
                id,fecha,condominio_id,usuario_id,
                username,accion,entidad,entidad_id,
                detalle,valor_anterior,valor_nuevo,
                resultado,modulo,trace_id
            FROM auditoria
            ORDER BY fecha DESC
            LIMIT %s
            """,
            (limit,),
        )

    decision = authorize(
        user,
        "AUDITORIA_INMUEBLE",
        property_id,
    )

    if not decision.allowed:
        raise PermissionError(decision.reason)

    return fetch_all(
        """
        SELECT
            id,fecha,condominio_id,usuario_id,
            username,accion,entidad,entidad_id,
            detalle,valor_anterior,valor_nuevo,
            resultado,modulo,trace_id
        FROM auditoria
        WHERE condominio_id=%s
        ORDER BY fecha DESC
        LIMIT %s
        """,
        (property_id, limit),
    )


def list_financial_audit(
    user,
    property_id=None,
    limit=500,
):
    if user.get("rol_global") == "SUPERADMIN":
        if property_id:
            return fetch_all(
                """
                SELECT *
                FROM auditoria_financiera
                WHERE condominio_id=%s
                ORDER BY fecha DESC,id DESC
                LIMIT %s
                """,
                (property_id, limit),
            )

        return fetch_all(
            """
            SELECT *
            FROM auditoria_financiera
            ORDER BY fecha DESC,id DESC
            LIMIT %s
            """,
            (limit,),
        )

    decision = authorize(
        user,
        "AUDITORIA_FINANCIERA",
        property_id,
    )

    if not decision.allowed:
        raise PermissionError(decision.reason)

    return fetch_all(
        """
        SELECT *
        FROM auditoria_financiera
        WHERE condominio_id=%s
        ORDER BY fecha DESC,id DESC
        LIMIT %s
        """,
        (property_id, limit),
    )


def record_financial_event(
    *,
    user,
    property_id,
    operation_type,
    entity,
    entity_id=None,
    space_id=None,
    person_id=None,
    amount=None,
    currency="MXN",
    previous_status=None,
    new_status=None,
    reference=None,
    related_event_id=None,
    detail=None,
    metadata=None,
    trace_id=None,
):
    if not user or not user.get("id"):
        raise PermissionError("USER_REQUIRED")

    trace_id = trace_id or new_trace_id()

    return execute(
        """
        INSERT INTO auditoria_financiera(
            condominio_id,
            usuario_id,
            username,
            tipo_operacion,
            entidad,
            entidad_id,
            espacio_id,
            persona_id,
            monto_mxn,
            moneda,
            estado_anterior,
            estado_nuevo,
            referencia,
            evento_relacionado_id,
            detalle,
            metadata,
            trace_id
        )
        VALUES(
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s::jsonb,%s
        )
        RETURNING id
        """,
        (
            property_id,
            user.get("id"),
            user.get("username"),
            operation_type,
            entity,
            entity_id,
            space_id,
            person_id,
            amount,
            currency,
            previous_status,
            new_status,
            reference,
            related_event_id,
            detail,
            serialize(metadata),
            trace_id,
        ),
        returning=True,
    )
