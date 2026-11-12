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
)

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
