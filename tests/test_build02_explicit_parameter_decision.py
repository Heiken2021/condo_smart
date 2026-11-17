from pathlib import Path

from services.financial_dynamic_parameter_editor import (
    missing_required_parameters,
)


EDITOR = Path(
    "services/financial_dynamic_parameter_editor.py"
).read_text(encoding="utf-8")

LIFECYCLE = Path(
    "views/financial_rule_lifecycle.py"
).read_text(encoding="utf-8")


def test_new_numeric_value_has_no_implicit_default():
    assert (
        "return None"
        in EDITOR
    )

    assert (
        '"Introduce el valor aprobado"'
        in EDITOR
    )


def test_number_input_can_start_empty():
    assert (
        "required=not optional"
        in EDITOR
    )

    assert (
        "placeholder=("
        in EDITOR
    )


def test_boolean_requires_explicit_decision():
    assert (
        "boolean_index = None"
        in EDITOR
    )

    assert (
        '"Selecciona Sí o No"'
        in EDITOR
    )


def test_allowed_string_has_no_implicit_first_option():
    assert (
        "index = None"
        in EDITOR
    )

    assert (
        '"Selecciona un valor"'
        in EDITOR
    )


def test_missing_required_parameters():
    schema = {
        "minimum_payment_percentage": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "unit": "PERCENT",
        },
        "maximum_surcharge_percentage": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "optional": True,
        },
    }

    missing = missing_required_parameters(
        schema=schema,
        values={},
    )

    assert missing == [
        "minimum_payment_percentage"
    ]


def test_zero_is_valid_explicit_percentage():
    schema = {
        "minimum_payment_percentage": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "unit": "PERCENT",
        },
    }

    missing = missing_required_parameters(
        schema=schema,
        values={
            "minimum_payment_percentage": 0.0,
        },
    )

    assert missing == []


def test_any_percentage_is_not_hardcoded():
    forbidden = (
        "minimum_payment_percentage = 80",
        '"minimum_payment_percentage": 80',
        "default_percentage = 80",
        "recommended_percentage = 80",
    )

    for token in forbidden:
        assert token not in EDITOR


def test_lifecycle_rejects_incomplete_version():
    assert (
        "missing_required_parameters("
        in LIFECYCLE
    )

    assert (
        "Completa los parámetros "
        in LIFECYCLE
    )


def test_existing_values_are_preserved_on_edit():
    assert (
        "if current_value is not None:"
        in EDITOR
    )

    assert (
        "return float(current_value)"
        in EDITOR
    )
