from pathlib import Path


MIGRATION = Path(
    "database/migrations/"
    "026_financial_rule_dependencies_build02.sql"
).read_text(encoding="utf-8")

SERVICE = Path(
    "services/"
    "financial_rule_dependencies.py"
).read_text(encoding="utf-8")


def test_dependency_catalog_is_governed():
    assert (
        "CREATE TABLE IF NOT EXISTS "
        "financial_rule_dependencies"
        in MIGRATION
    )

    assert (
        "consumer_definition_id"
        in MIGRATION
    )

    assert (
        "source_definition_id"
        in MIGRATION
    )


def test_continuity_dependencies_are_registered():
    for token in (
        "coverage_threshold",
        "minimum_payment_percentage",
        "tolerance_days",
        "grace_days",
        "PAGO_MINIMO_PARCIAL",
        "RECARGO_MOROSIDAD",
        "CONTINUIDAD_SERVICIOS",
    ):
        assert token in MIGRATION


def test_values_are_not_copied_into_continuity():
    forbidden = (
        "'minimum_payment_percentage', 80",
        "'grace_days', 3",
        "'coverage_threshold', 80",
        "'tolerance_days', 3",
    )

    for token in forbidden:
        assert token not in MIGRATION


def test_preview_supports_draft_sources():
    assert (
        "def preview_rule_dependencies("
        in SERVICE
    )

    assert (
        '"preview_only"'
        in SERVICE
    )

    assert (
        "'BORRADOR'"
        in SERVICE
    )


def test_effective_resolution_reuses_governance():
    assert (
        "def resolve_rule_dependencies("
        in SERVICE
    )

    assert (
        "resolve_effective_rule("
        in SERVICE
    )

    assert (
        '"effective_parameters"'
        in SERVICE
    )


def test_required_dependencies_have_gate():
    assert (
        '"all_required_resolved"'
        in SERVICE
    )

    assert (
        '"resolved"'
        in SERVICE
    )


def test_dependency_service_has_no_ui():
    assert "import streamlit" not in SERVICE
    assert "st." not in SERVICE
