from pathlib import Path


SQL = Path(
    "database/migrations/"
    "024_financial_policy_catalog_build02.sql"
).read_text(encoding="utf-8")


def test_policy_definitions_exist():
    for code in (
        "PAGO_MINIMO_PARCIAL",
        "RECARGO_MOROSIDAD",
        "CONTINUIDAD_SERVICIOS",
    ):
        assert f"'{code}'" in SQL


def test_policy_catalog_uses_same_rule_engine():
    assert (
        "INSERT INTO financial_rule_definitions"
        in SQL
    )

    assert (
        "INSERT INTO financial_rule_applicability"
        in SQL
    )


def test_partial_payment_is_dynamic():
    assert (
        "minimum_payment_percentage"
        in SQL
    )

    assert (
        "'minimum', 0"
        in SQL
    )

    assert (
        "'maximum', 100"
        in SQL
    )

    assert (
        "'unit', 'PERCENT'"
        in SQL
    )

    forbidden_defaults = (
        "'default', 80",
        "'default', 20",
        "'value', 80",
        "'value', 20",
    )

    for token in forbidden_defaults:
        assert token not in SQL


def test_late_fee_is_dynamic():
    assert "surcharge_percentage" in SQL
    assert "grace_days" in SQL
    assert "calculation_base" in SQL


def test_operational_policy_is_dynamic():
    assert (
        "minimum_coverage_percentage"
        in SQL
    )

    assert (
        "authorization_required"
        in SQL
    )


def test_policy_catalog_is_idempotent():
    assert SQL.count(
        "NOT EXISTS"
    ) >= 6


def test_policy_catalog_is_additive_only():
    upper = SQL.upper()

    for token in (
        "DROP TABLE",
        "DROP COLUMN",
        "TRUNCATE",
        "DELETE FROM",
    ):
        assert token not in upper


def test_policy_catalog_creates_no_operational_records():
    forbidden = (
        "INSERT INTO financial_rules ",
        "INSERT INTO financial_rule_versions ",
        "INSERT INTO financial_obligations ",
        "INSERT INTO payment_allocations ",
        "INSERT INTO space_fee_history ",
    )

    for token in forbidden:
        assert token not in SQL
