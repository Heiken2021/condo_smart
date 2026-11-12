from pathlib import Path


SETTINGS = Path(
    "services/system_settings.py"
).read_text(encoding="utf-8")

CATALOGOS = Path(
    "views/catalogos.py"
).read_text(encoding="utf-8")

PASSWORD = Path(
    "services/password_recovery.py"
).read_text(encoding="utf-8")

PERFORMANCE = Path(
    "services/performance.py"
).read_text(encoding="utf-8")


def test_system_settings_has_service_superadmin_guard():
    assert "def _require_superadmin(actor_id):" in SETTINGS
    assert "GLOBAL_SUPERADMIN_REQUIRED" in SETTINGS


def test_setting_mutation_checks_actor():
    block = SETTINGS.split("def set_setting", 1)[1]
    assert "_require_superadmin(actor)" in block


def test_system_logo_mutations_check_actor():
    update = SETTINGS.split(
        "def update_system_logo",
        1,
    )[1].split(
        "def delete_system_logo",
        1,
    )[0]

    delete = SETTINGS.split(
        "def delete_system_logo",
        1,
    )[1]

    assert "_require_superadmin(actor)" in update
    assert "_require_superadmin(actor)" in delete


def test_catalogos_has_explicit_superadmin_guard():
    assert "def _require_superadmin():" in CATALOGOS
    assert 'user.get("rol_global") != "SUPERADMIN"' in CATALOGOS


def test_catalogos_render_invokes_guard():
    render = CATALOGOS.split("def render():", 1)[1]
    assert "_require_superadmin()" in render


def test_password_recovery_uses_persistent_tokens():
    assert "password_reset_tokens" in PASSWORD


def test_password_recovery_does_not_require_active_session():
    assert "GLOBAL_SUPERADMIN_REQUIRED" not in PASSWORD
    assert "_require_superadmin" not in PASSWORD


def test_performance_is_internal_telemetry():
    assert "performance_events" in PERFORMANCE
    assert "duration_ms" in PERFORMANCE
    assert "query_count" in PERFORMANCE


def test_performance_is_not_a_business_crud_service():
    assert "usuarios SET" not in PERFORMANCE
    assert "condominios SET" not in PERFORMANCE
    assert "espacios SET" not in PERFORMANCE
