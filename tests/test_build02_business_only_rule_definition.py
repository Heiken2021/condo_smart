from pathlib import Path


VIEW = Path(
    "views/financial_governance.py"
).read_text(encoding="utf-8")

EDITOR = Path(
    "services/"
    "financial_dynamic_parameter_editor.py"
).read_text(encoding="utf-8")


def test_rule_detail_has_business_tabs():
    for label in (
        "Definición",
        "Configuración",
        "Versiones",
        "Gobierno y auditoría",
    ):
        assert f'"{label}"' in VIEW


def test_raw_technical_json_is_not_visible():
    forbidden = (
        "st.json(schema)",
        "Ver definición técnica",
        "st.data_editor(schema",
        'st.text_area("JSON',
        'st.text_area("Esquema',
    )

    for token in forbidden:
        assert token not in VIEW


def test_internal_schema_stays_internal():
    assert (
        "La estructura técnica de estos "
        in VIEW
    )

    assert (
        "administrada "
        in VIEW
    )

    assert (
        "internamente por Condo_Smart"
        in VIEW
    )

    assert (
        "internamente por Condo_Smart y no "
        in VIEW
    )

    assert (
        "se muestra ni se edita como código."
        in VIEW
    )


def test_configuration_has_generic_empty_state():
    assert (
        "Esta regla todavía no tiene "
        in VIEW
    )

    assert (
        "una configuración creada."
        in VIEW
    )

    assert (
        "Selecciona **Nueva regla** "
        in VIEW
    )

    assert (
        "crear su primera versión"
        in VIEW
    )


def test_configuration_is_versioned():
    for token in (
        "Los valores de configuración ",
        "pertenecen a una versión.",
        "Una versión aprobada no se ",
        "modifica destructivamente",
        "una nueva versión.",
    ):
        assert token in VIEW


def test_definition_uses_dynamic_parameter_presenter():
    assert (
        "render_parameter_definition_cards("
        in VIEW
    )

    assert (
        "def render_parameter_definition_cards("
        in EDITOR
    )

    assert (
        "for code, specification in "
        in EDITOR
    )


def test_dynamic_cards_have_help_popovers():
    assert "st.popover(" in EDITOR
    assert '"ⓘ"' in EDITOR

    assert (
        "¿Qué significa "
        in EDITOR
    )

    assert (
        "este parámetro?"
        in EDITOR
    )


def test_dynamic_cards_explain_business_metadata():
    for token in (
        "**¿Qué configura?** ",
        "**Tipo de valor:** ",
        "**Límites permitidos:** ",
        "**Obligatorio:** ",
    ):
        assert token in EDITOR


def test_dynamic_cards_support_all_current_policies():
    for code in (
        "amount",
        "frequency",
        "due_day",
        "minimum_payment_percentage",
        "minimum_compliance",
        "surcharge_percentage",
        "calculation_base",
        "grace_days",
        "surcharge_frequency",
        "maximum_surcharge_percentage",
        "minimum_coverage_percentage",
        "tolerance_days",
        "prior_notice_required",
        "authorization_required",
        "operational_action",
    ):
        assert f'"{code}"' in EDITOR


def test_optional_parameters_are_explained():
    assert (
        "Este parámetro es opcional."
        in EDITOR
    )

    assert (
        "puede decidir "
        in EDITOR
    )


def test_limits_are_not_current_values():
    assert (
        "Los límites permitidos determinan qué "
        in EDITOR
    )

    assert (
        "No representan los valores actuales "
        in EDITOR
    )
