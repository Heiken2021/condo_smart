import os
import smtplib
import ssl
from email.message import EmailMessage

from core.db import execute
from services.audit_service import sanitize


SUPPORT_EMAIL = "soporte.condosmart@gmail.com"


def _env(*names, default=None):
    for name in names:
        value = os.environ.get(name)

        if value:
            return value

    return default


def smtp_configuration():
    username = _env(
        "SMTP_USER",
        "SMTP_USERNAME",
        "SMTP_EMAIL",
    )

    password = _env(
        "SMTP_PASSWORD",
    )

    sender = _env(
        "SMTP_FROM",
        "SMTP_FROM_EMAIL",
        default=username,
    )

    if (
        not username
        or not password
        or not sender
    ):
        raise RuntimeError(
            "SMTP_NOT_CONFIGURED"
        )

    return {
        "host": _env(
            "SMTP_HOST",
            default="smtp.gmail.com",
        ),
        "port": int(
            _env(
                "SMTP_PORT",
                default="587",
            )
        ),
        "username": username,
        "password": password,
        "sender": sender,
    }


def _claim_alert(audit_id):
    return execute(
        """
        INSERT INTO auditoria_alertas(
            auditoria_id,
            destinatario,
            estado,
            intentos
        )
        VALUES(
            %s,
            %s,
            'PENDING',
            1
        )
        ON CONFLICT(auditoria_id)
        DO NOTHING
        RETURNING id
        """,
        (
            audit_id,
            SUPPORT_EMAIL,
        ),
        returning=True,
    )


def _mark_sent(audit_id):
    execute(
        """
        UPDATE auditoria_alertas
        SET estado='SENT',
            enviado_en=NOW(),
            ultimo_error=NULL
        WHERE auditoria_id=%s
        """,
        (audit_id,),
    )


def _mark_error(audit_id, error):
    execute(
        """
        UPDATE auditoria_alertas
        SET estado='ERROR',
            ultimo_error=%s
        WHERE auditoria_id=%s
        """,
        (
            str(error)[:500],
            audit_id,
        ),
    )


def notify_critical_audit_event(
    *,
    audit_id,
    property_id,
    user,
    action,
    entity,
    entity_id,
    result,
    detail,
    trace_id,
    reason,
):
    if not audit_id:
        return False

    claim = _claim_alert(audit_id)

    if not claim:
        return False

    safe = sanitize(
        {
            "usuario": (
                user.get("username")
                if user
                else "sistema"
            ),
            "accion": action,
            "condominio_id": property_id,
            "entidad": entity,
            "entidad_id": entity_id,
            "resultado": result,
            "detalle": detail,
            "trace_id": trace_id,
            "motivo": reason,
        }
    )

    try:
        config = smtp_configuration()

        message = EmailMessage()

        message["Subject"] = (
            "🔴 Condo_Smart | "
            "Evento crítico detectado"
        )

        message["From"] = config["sender"]
        message["To"] = SUPPORT_EMAIL

        message.set_content(
            "Condo_Smart detectó un evento crítico."
            "\n\n"
            "Severidad: CRITICO\n"
            f"Usuario: {safe.get('usuario')}\n"
            f"Acción: {safe.get('accion')}\n"
            f"Inmueble ID: "
            f"{safe.get('condominio_id')}\n"
            f"Entidad: {safe.get('entidad')}\n"
            f"Registro ID: "
            f"{safe.get('entidad_id')}\n"
            f"Resultado: "
            f"{safe.get('resultado')}\n"
            f"Motivo: {safe.get('motivo')}\n"
            f"Detalle: {safe.get('detalle')}\n"
            f"Trace ID: {safe.get('trace_id')}\n"
            "\n"
            "Recomendación: revisa el usuario, "
            "la acción y el registro afectado "
            "en el módulo Auditoría."
        )

        context = ssl.create_default_context()

        with smtplib.SMTP(
            config["host"],
            config["port"],
            timeout=15,
        ) as smtp:
            smtp.ehlo()
            smtp.starttls(
                context=context,
            )
            smtp.ehlo()

            smtp.login(
                config["username"],
                config["password"],
            )

            smtp.send_message(
                message,
            )

        _mark_sent(
            audit_id,
        )

        return True

    except Exception as error:
        _mark_error(
            audit_id,
            error,
        )

        return False
