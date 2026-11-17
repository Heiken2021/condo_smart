from pathlib import Path


VIEW = Path(
    "views/financial_governance.py"
).read_text(encoding="utf-8")


def test_governance_renderer_exists():
    assert (
        "def render_governance_section("
        in VIEW
    )


def test_governance_requires_permission():
    assert (
        "FINANZAS_CUOTA_GESTIONAR"
        in VIEW
    )


def test_governance_fee_draft_is_temporarily_blocked():
    assert (
        "Crear cuota en borrador"
        in VIEW
    )
    assert (
        "disabled=True"
        in VIEW
    )
    assert (
        "La creación de nuevas cuotas está "
        in VIEW
    )
    assert (
        "create_space_fee_version("
        not in VIEW
    )


def test_governance_does_not_approve_fee_without_rule():
    assert (
        "approve_space_fee_version("
        not in VIEW
    )
    assert (
        "Aprobar cuota"
        not in VIEW
    )
    assert (
        "rule_version_id"
        in VIEW
    )


def test_governance_supports_maintenance_fee():
    assert (
        "MANTENIMIENTO_ORDINARIO"
        in VIEW
    )


def test_governance_has_effective_date():
    assert "effective_from" in VIEW
    assert "Vigente desde" in VIEW


def test_governance_does_not_create_obligation():
    assert (
        "generate_governed_obligation("
        not in VIEW
    )
    assert (
        "create_financial_obligation("
        not in VIEW
    )


def test_governance_does_not_register_payment():
    assert "register_payment(" not in VIEW


def test_governance_has_no_direct_sql():
    for token in (
        "INSERT INTO",
        "UPDATE ",
        "DELETE FROM",
    ):
        assert token not in VIEW
