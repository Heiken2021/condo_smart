from pathlib import Path


DEPENDENCIES = Path(
    "services/financial_rule_dependencies.py"
).read_text(encoding="utf-8")

COMMANDS = Path(
    "services/financial_governance_commands.py"
).read_text(encoding="utf-8")

LIFECYCLE = Path(
    "views/financial_rule_lifecycle.py"
).read_text(encoding="utf-8")


def test_dependency_preview_is_business_friendly():
    assert (
        "def dependency_preview_rows("
        in DEPENDENCIES
    )

    for label in (
        "Criterio heredado",
        "Fuente gobernada",
        "Versión fuente",
        "Valor heredado",
        "Disponibilidad",
    ):
        assert label in DEPENDENCIES


def test_dependency_values_have_units():
    assert (
        '"coverage_threshold": "PERCENT"'
        in DEPENDENCIES
    )

    assert (
        '"tolerance_days": "DAYS"'
        in DEPENDENCIES
    )


def test_version_form_shows_inherited_criteria():
    assert (
        "def _render_inherited_dependency_preview("
        in LIFECYCLE
    )

    assert (
        '"#### Criterios heredados"'
        in LIFECYCLE
    )

    assert (
        "Valor heredado actual"
        in LIFECYCLE
    )


def test_draft_dependency_is_explained():
    assert (
        "Vista previa desde una versión "
        in LIFECYCLE
    )

    assert (
        "en Borrador. Este criterio no "
        in LIFECYCLE
    )

    assert (
        "será efectivo hasta que la "
        in LIFECYCLE
    )


def test_approval_ui_blocks_unresolved_dependencies():
    assert (
        "unresolved_dependencies"
        in LIFECYCLE
    )

    assert (
        "disabled=bool("
        in LIFECYCLE
    )

    assert (
        "Esta versión no puede aprobarse "
        in LIFECYCLE
    )


def test_approval_command_has_transactional_gate():
    assert (
        "def _validate_rule_dependencies_for_approval("
        in COMMANDS
    )

    assert (
        "FINANCIAL_RULE_DEPENDENCY_"
        in COMMANDS
    )

    assert (
        "NOT_EFFECTIVE:"
        in COMMANDS
    )


def test_approval_dependency_query_uses_approved_sources():
    assert (
        "source_version.estado_codigo="
        in COMMANDS
    )

    assert (
        "'APROBADO'"
        in COMMANDS
    )

    assert (
        "source_version.vigente_desde"
        in COMMANDS
    )


def test_approval_audit_records_dependency_sources():
    assert (
        '"resolved_dependencies"'
        in COMMANDS
    )

    assert (
        '"source_version_id"'
        in COMMANDS
    )

    assert (
        '"inherited_value"'
        in COMMANDS
    )


def test_continuity_does_not_copy_source_values():
    forbidden = (
        '"minimum_payment_percentage": 80',
        '"grace_days": 3',
        '"coverage_threshold": 80',
        '"tolerance_days": 3',
    )

    for token in forbidden:
        assert token not in LIFECYCLE
        assert token not in COMMANDS


def test_dependency_preview_accepts_definition_code():
    start = LIFECYCLE.index(
        "def _render_inherited_dependency_preview("
    )
    end = LIFECYCLE.index(
        "\ndef ",
        start + 5,
    )
    function = LIFECYCLE[start:end]

    assert '"definition_code"' in function
    assert (
        "consumer_rule_code=rule_code"
        in function
    )


def test_dependency_preview_reports_ready_state():
    start = LIFECYCLE.index(
        "def _render_inherited_dependency_preview("
    )
    end = LIFECYCLE.index(
        "\ndef ",
        start + 5,
    )
    function = LIFECYCLE[start:end]

    assert "unresolved_required" in function
    assert '"ready_for_approval"' in function
    assert (
        "Todas las dependencias requeridas "
        in function
    )
    assert (
        "están aprobadas y efectivas."
        in function
    )
    assert (
        "quedará bloqueada mientras "
        in function
    )
