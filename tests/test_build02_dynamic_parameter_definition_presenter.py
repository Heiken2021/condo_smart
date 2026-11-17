from pathlib import Path

from services.financial_dynamic_parameter_editor import (
    limits_text,
    parameter_label,
    parameter_type_label,
)

from views.financial_rule_lifecycle import (
    business_definition_value,
)


EDITOR = Path(
    "services/"
    "financial_dynamic_parameter_editor.py"
).read_text(encoding="utf-8")

GOVERNANCE = Path(
    "views/financial_governance.py"
).read_text(encoding="utf-8")


def test_definition_presenter_is_dynamic():
    assert (
        "def render_parameter_definition_cards("
        in EDITOR
    )

    assert (
        "for code, specification in "
        in EDITOR
    )


def test_governance_uses_dynamic_definition_presenter():
    assert (
        "render_parameter_definition_cards("
        in GOVERNANCE
    )


def test_governance_no_longer_has_rule_specific_cards():
    definition_start = GOVERNANCE.index(
        '"#### Parámetros configurables"'
    )

    configuration_start = GOVERNANCE.index(
        "with configuration_tab:",
        definition_start,
    )

    block = GOVERNANCE[
        definition_start:
        configuration_start
    ]

    assert (
        'schema.get(\n'
        '            "amount"'
        not in block
    )

    assert (
        "amount_spec"
        not in block
    )

    assert (
        "frequency_spec"
        not in block
    )

    assert (
        "due_day_spec"
        not in block
    )


def test_late_fee_parameters_are_business_friendly():
    assert (
        parameter_label(
            "surcharge_percentage"
        )
        == "Porcentaje de recargo"
    )

    assert (
        parameter_label(
            "calculation_base"
        )
        == "Base de cálculo"
    )

    assert (
        parameter_label(
            "grace_days"
        )
        == "Días de gracia"
    )

    assert (
        parameter_label(
            "surcharge_frequency"
        )
        == "Frecuencia del recargo"
    )

    assert (
        parameter_label(
            "maximum_surcharge_percentage"
        )
        == "Recargo máximo"
    )


def test_late_fee_limits_are_dynamic():
    result = limits_text(
        {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "unit": "PERCENT",
        }
    )

    assert "Mínimo 0 %" in result
    assert "Máximo 100 %" in result


def test_optional_parameter_is_supported():
    assert (
        "Este parámetro es opcional."
        in EDITOR
    )


def test_parameter_type_is_friendly():
    assert (
        parameter_type_label(
            {
                "type": "number",
                "unit": "PERCENT",
            }
        )
        == "Porcentaje"
    )

    assert (
        parameter_type_label(
            {
                "type": "boolean",
            }
        )
        == "Decisión Sí / No"
    )


def test_definition_codes_are_presented_as_business_labels():
    assert (
        business_definition_value(
            "Aplicabilidad",
            "TIPO_INMUEBLE:FRACCIONAMIENTO",
        )
        == "Fraccionamiento"
    )

    assert (
        business_definition_value(
            "Nivel base",
            "CORE",
        )
        == "Base del sistema"
    )

    assert (
        business_definition_value(
            "Tipo de resultado",
            "POLICY",
        )
        == "Política de negocio"
    )

    assert (
        business_definition_value(
            "Dominio",
            "COBRANZA",
        )
        == "Cobranza"
    )
