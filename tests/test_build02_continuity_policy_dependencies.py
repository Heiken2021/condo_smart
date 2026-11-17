from pathlib import Path


SQL = Path(
    "database/migrations/"
    "025_continuity_policy_dependencies_build02.sql"
).read_text(encoding="utf-8")

EDITOR = Path(
    "services/"
    "financial_dynamic_parameter_editor.py"
).read_text(encoding="utf-8")


def test_continuity_consumes_other_policy_results():
    assert (
        "Pago mínimo parcial"
        in SQL
    )

    assert (
        "Recargo por "
        in SQL
    )

    assert (
        "morosidad"
        in SQL
    )

    assert (
        "sin duplicar sus parámetros"
        in SQL
    )


def test_continuity_keeps_operational_parameters():
    for code in (
        "operational_action",
        "prior_notice_required",
        "authorization_required",
    ):
        assert f"'{code}'" in SQL


def test_continuity_removes_duplicated_thresholds():
    update = SQL[
        SQL.index(
            "UPDATE financial_rule_definitions"
        ):
    ]

    assert (
        "'minimum_coverage_percentage'"
        not in update
    )

    assert (
        "'tolerance_days'"
        not in update
    )


def test_continuity_uses_same_governed_catalog():
    assert (
        "UPDATE financial_rule_definitions"
        in SQL
    )

    assert (
        "WHERE codigo = "
        "'CONTINUIDAD_SERVICIOS'"
        in SQL
    )


def test_continuity_creates_no_operational_records():
    forbidden = (
        "INSERT INTO financial_rules",
        "INSERT INTO financial_rule_versions",
        "INSERT INTO financial_obligations",
        "INSERT INTO payment_allocations",
        "INSERT INTO space_fee_history",
    )

    for token in forbidden:
        assert token not in SQL


def test_operational_labels_remain_business_friendly():
    for label in (
        "Acción operativa",
        "Requiere aviso previo",
        "Requiere autorización",
    ):
        assert f'"{label}"' in EDITOR
