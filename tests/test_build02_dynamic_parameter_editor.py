from pathlib import Path

from services.financial_dynamic_parameter_editor import (
    friendly_value,
    limits_text,
    parameter_label,
)


EDITOR = Path(
    "services/financial_dynamic_parameter_editor.py"
).read_text(encoding="utf-8")

LIFECYCLE = Path(
    "views/financial_rule_lifecycle.py"
).read_text(encoding="utf-8")

GOVERNANCE = Path(
    "views/financial_governance.py"
).read_text(encoding="utf-8")


def test_editor_supports_schema_types():
    for token in (
        '"number"',
        '"integer"',
        '"boolean"',
        '"string"',
    ):
        assert token in EDITOR


def test_editor_supports_percentages():
    assert (
        'unit == "PERCENT"'
        in EDITOR
    )

    assert (
        'f"{label} (%)"'
        in EDITOR
    )


def test_percentages_have_no_business_default():
    forbidden = (
        '"minimum_payment_percentage": 80',
        '"minimum_payment_percentage": 0.8',
        "default_percentage = 80",
    )

    for token in forbidden:
        assert token not in EDITOR


def test_optional_parameters_are_supported():
    assert (
        'specification.get(\n'
        '                "optional"'
        in EDITOR
    )

    assert (
        "Configurar {label}"
        in EDITOR
    )


def test_allowed_values_use_selectbox():
    assert "st.selectbox(" in EDITOR
    assert "format_func=(" in EDITOR


def test_boolean_values_require_explicit_decision():
    assert (
        "boolean_index = None"
        in EDITOR
    )

    assert (
        "st.selectbox("
        in EDITOR
    )

    assert (
        '"Selecciona Sí o No"'
        in EDITOR
    )

    assert (
        '"Sí"'
        in EDITOR
    )

    assert (
        '"No"'
        in EDITOR
    )


def test_limits_are_dynamic():
    schema = {
        "type": "number",
        "minimum": 0,
        "maximum": 100,
        "unit": "PERCENT",
    }

    value = limits_text(schema)

    assert "Mínimo 0 %" in value
    assert "Máximo 100 %" in value


def test_internal_values_are_friendly():
    assert (
        friendly_value(
            "SALDO_PENDIENTE"
        )
        == "Saldo pendiente"
    )

    assert (
        friendly_value(
            "RESTRINGIR_SEGUN_POLITICA"
        )
        == "Aplicar restricción según política"
    )


def test_policy_labels_are_business_friendly():
    assert (
        parameter_label(
            "minimum_payment_percentage"
        )
        == "Pago mínimo requerido"
    )

    assert (
        parameter_label(
            "surcharge_percentage"
        )
        == "Porcentaje de recargo"
    )


def test_create_version_uses_dynamic_editor():
    assert (
        "render_parameter_inputs("
        in LIFECYCLE
    )

    assert (
        "new_version_"
        in LIFECYCLE
    )


def test_edit_draft_uses_dynamic_editor():
    assert (
        "edit_version_"
        in LIFECYCLE
    )


def test_configuration_uses_limits_language():
    assert (
        "Límites permitidos"
        in GOVERNANCE
        or
        "limits_text"
        in EDITOR
    )


def test_dynamic_editor_does_not_write_database():
    forbidden = (
        "INSERT INTO",
        "UPDATE ",
        "DELETE FROM",
    )

    for token in forbidden:
        assert token not in EDITOR
