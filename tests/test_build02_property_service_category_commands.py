from pathlib import Path


COMMANDS = Path(
    "services/property_service_category_commands.py"
).read_text(encoding="utf-8")


def test_category_commands_exist():
    for token in (
        "def create_service_category(",
        "def update_service_category(",
        "def set_service_category_active(",
    ):
        assert token in COMMANDS


def test_category_commands_are_property_scoped():
    for token in (
        "condominio_id=%s",
        "property_id",
        "PROPERTY_SERVICE_CATEGORY_NOT_FOUND",
    ):
        assert token in COMMANDS


def test_category_code_is_stable_after_creation():
    start = COMMANDS.index(
        "def update_service_category("
    )
    end = COMMANDS.index(
        "def set_service_category_active("
    )

    update_function = COMMANDS[start:end]

    assert (
        "SET\n                        codigo=%s"
        not in update_function
    )


def test_category_commands_validate_order():
    assert (
        "PROPERTY_SERVICE_CATEGORY_ORDER_INVALID"
        in COMMANDS
    )


def test_category_commands_are_audited():
    for token in (
        "PROPERTY_SERVICE_CATEGORY_CREATED",
        "PROPERTY_SERVICE_CATEGORY_UPDATED",
        "PROPERTY_SERVICE_CATEGORY_ACTIVATED",
        "PROPERTY_SERVICE_CATEGORY_DEACTIVATED",
        "PROPERTY_SERVICE_CATEGORY",
    ):
        assert token in COMMANDS


def test_category_commands_are_transactional():
    assert "connection.commit()" in COMMANDS
    assert "connection.rollback()" in COMMANDS
    assert "FOR UPDATE" in COMMANDS


def test_category_commands_do_not_seed_or_touch_services():
    forbidden = (
        "INSERT INTO property_service_catalog",
        "UPDATE property_service_catalog",
        "INSERT INTO continuity_service_policy",
        "UPDATE espacios",
        "minimum_payment_percentage",
        "grace_days",
    )

    for token in forbidden:
        assert token not in COMMANDS
