from pathlib import Path


LIFECYCLE = Path(
    "views/financial_rule_lifecycle.py"
).read_text(encoding="utf-8")

GOVERNANCE = Path(
    "views/financial_governance.py"
).read_text(encoding="utf-8")


def test_lifecycle_uses_governed_commands():
    for token in (
        "create_financial_rule(",
        "create_rule_version(",
        "approve_rule_version(",
        "close_rule_version(",
    ):
        assert token in LIFECYCLE


def test_lifecycle_requires_permissions():
    assert (
        "FINANZAS_REGLA_GESTIONAR"
        in LIFECYCLE
    )
    assert (
        "FINANZAS_REGLA_APROBAR"
        in LIFECYCLE
    )


def test_lifecycle_has_required_actions():
    for label in (
        "Nueva regla",
        "Editar borrador",
        "Nueva versión",
        "Aprobar",
        "Finalizar vigencia",
        "Auditoría",
    ):
        assert label in LIFECYCLE


def test_lifecycle_has_scope_options():
    for scope in (
        "INMUEBLE",
        "ESTRUCTURA",
        "ESPACIO",
    ):
        assert scope in LIFECYCLE


def test_lifecycle_uses_dynamic_parameter_inputs():
    assert (
        "render_parameter_inputs("
        in LIFECYCLE
    )

    editor = Path(
        "services/"
        "financial_dynamic_parameter_editor.py"
    ).read_text(encoding="utf-8")

    assert (
        "PARAMETER_LABELS"
        in editor
    )

    assert (
        "PARAMETER_HELP"
        in editor
    )

    for parameter_type in (
        '"number"',
        '"integer"',
        '"string"',
        '"boolean"',
    ):
        assert parameter_type in editor

def test_lifecycle_has_version_fields():
    assert "Vigente desde" in LIFECYCLE
    assert "Motivo del cambio" in LIFECYCLE


def test_help_popovers_exist():
    assert "st.popover(" in LIFECYCLE

    for key in (
        "approval",
        "exceptions",
        "inheritance",
        "override",
        "scope",
        "priority",
    ):
        assert f'"{key}"' in LIFECYCLE


def test_governance_uses_help_attributes():
    assert (
        "render_governance_attributes("
        in GOVERNANCE
    )


def test_governance_uses_lifecycle_actions():
    assert (
        "render_rule_lifecycle_actions("
        in GOVERNANCE
    )


def test_existing_fee_creation_stays_blocked():
    assert (
        "La creación de nuevas cuotas está "
        in GOVERNANCE
    )


def test_lifecycle_has_no_direct_sql():
    for token in (
        "INSERT INTO",
        "UPDATE ",
        "DELETE FROM",
    ):
        assert token not in LIFECYCLE
