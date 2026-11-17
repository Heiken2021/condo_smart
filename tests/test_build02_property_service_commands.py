from pathlib import Path


COMMANDS = Path(
    "services/property_service_commands.py"
).read_text(encoding="utf-8")


def test_commands_require_governed_permission():
    assert (
        'MANAGE_PERMISSION = '
        '"FINANZAS_REGLA_GESTIONAR"'
        in COMMANDS
    )
    assert "authorize(" in COMMANDS


def test_catalog_commands_exist():
    for token in (
        "def create_property_service(",
        "def update_property_service(",
        "def set_property_service_active(",
        "def create_service_availability(",
    ):
        assert token in COMMANDS


def test_commands_are_property_scoped():
    for token in (
        "condominio_id=%s",
        "property_id",
        "PROPERTY_SERVICE_NOT_FOUND",
    ):
        assert token in COMMANDS


def test_service_code_is_not_user_renamed():
    update_start = COMMANDS.index(
        "def update_property_service("
    )
    active_start = COMMANDS.index(
        "def set_property_service_active("
    )
    update_function = COMMANDS[
        update_start:active_start
    ]

    assert "SET\n                        nombre=%s" in (
        update_function
    )
    assert "SET\n                        codigo=%s" not in (
        update_function
    )


def test_availability_supports_hierarchy():
    for token in (
        '"INMUEBLE"',
        '"ESTRUCTURA"',
        '"ESPACIO"',
        "structure_id",
        "space_id",
        "inherits",
        "is_override",
        "priority",
        "effective_from",
        "effective_to",
    ):
        assert token in COMMANDS


def test_commands_generate_financial_audit():
    for token in (
        "INSERT INTO auditoria_financiera",
        "PROPERTY_SERVICE_CREATED",
        "PROPERTY_SERVICE_UPDATED",
        "PROPERTY_SERVICE_ACTIVATED",
        "PROPERTY_SERVICE_DEACTIVATED",
        '"PROPERTY_SERVICE_"',
        '"AVAILABILITY_CREATED"',
        "trace_id",
    ):
        assert token in COMMANDS


def test_commands_are_transactional():
    assert "connection.commit()" in COMMANDS
    assert "connection.rollback()" in COMMANDS
    assert "FOR UPDATE" in COMMANDS


def test_commands_do_not_apply_restrictions():
    forbidden = (
        "operational_service_restriction",
        "UPDATE espacios",
        "UPDATE financial_obligations",
        "INSERT INTO payment_allocations",
        "UPDATE space_fee_history",
        "minimum_payment_percentage",
        "grace_days",
    )

    for token in forbidden:
        assert token not in COMMANDS
