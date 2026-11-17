from pathlib import Path

from services.financial_dynamic_parameter_editor import (
    limits_text,
    parameter_help,
    parameter_label,
    parameter_type_label,
)


VIEW = Path(
    "views/financial_governance.py"
).read_text(encoding="utf-8")

EDITOR = Path(
    "services/"
    "financial_dynamic_parameter_editor.py"
).read_text(encoding="utf-8")


def test_parameter_experience_is_dynamic():
    assert (
        "render_parameter_definition_cards("
        in VIEW
    )

    assert (
        "def render_parameter_definition_cards("
        in EDITOR
    )


def test_parameters_have_help_popovers():
    assert "st.popover(" in EDITOR
    assert '"ⓘ"' in EDITOR

    assert (
        "parameter_help(code)"
        in EDITOR
    )


def test_amount_has_business_guidance():
    assert (
        parameter_label("amount")
        == "Importe"
    )

    assert (
        "Importe concreto"
        in parameter_help("amount")
    )

    assert (
        parameter_type_label(
            {
                "type": "number",
                "currency": "MXN",
            }
        )
        == "Importe monetario"
    )


def test_frequency_has_business_guidance():
    assert (
        parameter_label("frequency")
        == "Frecuencia"
    )

    assert (
        "Periodicidad"
        in parameter_help("frequency")
    )

    result = limits_text(
        {
            "type": "string",
            "allowed": ["MENSUAL"],
        }
    )

    assert result == (
        "Opciones permitidas: Mensual"
    )


def test_due_day_has_business_guidance():
    assert (
        parameter_label("due_day")
        == "Día de vencimiento"
    )

    assert (
        "Día del periodo"
        in parameter_help("due_day")
    )

    result = limits_text(
        {
            "type": "integer",
            "minimum": 1,
            "maximum": 31,
            "optional": True,
        }
    )

    assert "Mínimo 1" in result
    assert "Máximo 31" in result


def test_late_fee_has_business_guidance():
    expected = {
        "surcharge_percentage":
            "Porcentaje de recargo",
        "calculation_base":
            "Base de cálculo",
        "grace_days":
            "Días de gracia",
        "surcharge_frequency":
            "Frecuencia del recargo",
        "maximum_surcharge_percentage":
            "Recargo máximo",
    }

    for code, label in expected.items():
        assert parameter_label(code) == label
        assert parameter_help(code)


def test_boolean_is_business_friendly():
    assert (
        parameter_type_label(
            {"type": "boolean"}
        )
        == "Decisión Sí / No"
    )

    assert (
        limits_text(
            {"type": "boolean"}
        )
        == "Sí o No"
    )


def test_percentage_is_business_friendly():
    assert (
        parameter_type_label(
            {
                "type": "number",
                "unit": "PERCENT",
            }
        )
        == "Porcentaje"
    )

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


def test_optional_parameter_is_explained():
    assert (
        "Este parámetro es opcional."
        in EDITOR
    )


def test_schema_is_internal_engine_only():
    assert (
        'detail.get(\n'
        '                "esquema_parametros"'
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


def test_admin_does_not_edit_json():
    forbidden = (
        "st.json(schema)",
        "st.data_editor(schema",
        'st.text_area("JSON',
        'st.text_area("Esquema',
    )

    for token in forbidden:
        assert token not in VIEW
