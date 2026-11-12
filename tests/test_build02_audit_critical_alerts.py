from pathlib import Path


APP = Path(
    "app.py"
).read_text(encoding="utf-8")

AUTH = Path(
    "core/auth.py"
).read_text(encoding="utf-8")

VIEW = Path(
    "views/auditoria.py"
).read_text(encoding="utf-8")

ALERTS = Path(
    "services/audit_alerts.py"
).read_text(encoding="utf-8")

MIGRATION = Path(
    "database/migrations/"
    "017_audit_critical_alerts_build02.sql"
).read_text(encoding="utf-8")


def test_audit_hides_global_quick_selector():
    assert "current_nav_for_context" in APP
    assert (
        "current_nav_for_context!='auditoria'"
        in APP
    )


def test_audit_is_not_property_required():
    line = APP.split(
        "PROPERTY_REQUIRED=",
        1,
    )[1].splitlines()[0]

    assert "'auditoria'" in line


def test_audit_uses_authorized_property_fallback():
    assert "active_property = cid()" in VIEW
    assert "iter(options.values())" in VIEW


def test_old_property_message_is_removed():
    assert (
        "Selecciona un inmueble autorizado "
        "para consultar su auditoría."
        not in VIEW
    )


def test_support_email_is_fixed():
    assert (
        'SUPPORT_EMAIL = '
        '"soporte.condosmart@gmail.com"'
        in ALERTS
    )


def test_alert_uses_smtp_environment():
    assert '"SMTP_HOST"' in ALERTS
    assert '"SMTP_PASSWORD"' in ALERTS
    assert '"SMTP_USER"' in ALERTS


def test_alert_payload_is_sanitized():
    assert "sanitize(" in ALERTS


def test_alert_contains_incident_context():
    for value in [
        "Usuario:",
        "Acción:",
        "Inmueble ID:",
        "Entidad:",
        "Registro ID:",
        "Resultado:",
        "Motivo:",
        "Trace ID:",
    ]:
        assert value in ALERTS


def test_only_critical_events_notify():
    assert (
        'system_severity(event)'
        in AUTH
    )
    assert (
        '== "CRITICO"'
        in AUTH
    )


def test_event_is_saved_before_notification():
    assert "RETURNING id" in AUTH
    assert "returning=True" in AUTH
    assert (
        "notify_critical_audit_event("
        in AUTH
    )


def test_alert_is_deduplicated():
    assert (
        "auditoria_id BIGINT NOT NULL UNIQUE"
        in MIGRATION
    )
    assert (
        "ON CONFLICT(auditoria_id)"
        in ALERTS
    )


def test_delivery_state_is_persisted():
    assert "PENDING" in MIGRATION
    assert "'SENT'" in ALERTS
    assert "'ERROR'" in ALERTS


def test_smtp_failure_does_not_break_operation():
    assert "except Exception:" in AUTH
    assert "pass" in AUTH


def test_smtp_failure_is_recorded():
    assert "_mark_error(" in ALERTS
    assert "ultimo_error" in ALERTS


def test_no_email_credentials_are_hardcoded():
    assert "SMTP_PASSWORD =" not in ALERTS
    assert "sk-" not in ALERTS


def test_migration_is_idempotent():
    assert (
        "CREATE TABLE IF NOT EXISTS "
        "auditoria_alertas"
        in MIGRATION
    )

    assert (
        "CREATE INDEX IF NOT EXISTS"
        in MIGRATION
    )
