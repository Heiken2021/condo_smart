from pathlib import Path

from services.financial_dynamic_parameter_editor import (
    missing_required_parameters,
)


EDITOR = Path(
    "services/financial_dynamic_parameter_editor.py"
).read_text(encoding="utf-8")


def test_empty_integer_is_not_cast_directly():
    assert (
        "integer_value = st.number_input("
        in EDITOR
    )

    assert (
        "if integer_value is not None"
        in EDITOR
    )

    assert (
        "else None"
        in EDITOR
    )


def test_required_empty_integer_is_reported_missing():
    schema = {
        "grace_days": {
            "type": "integer",
            "minimum": 0,
        },
    }

    assert (
        missing_required_parameters(
            schema=schema,
            values={
                "grace_days": None,
            },
        )
        == ["grace_days"]
    )


def test_zero_integer_is_valid_explicit_decision():
    schema = {
        "grace_days": {
            "type": "integer",
            "minimum": 0,
        },
    }

    assert (
        missing_required_parameters(
            schema=schema,
            values={
                "grace_days": 0,
            },
        )
        == []
    )


def test_no_implicit_zero_default_is_reintroduced():
    block_start = EDITOR.index(
        "def _integer_default("
    )

    block_end = EDITOR.index(
        "def missing_required_parameters(",
        block_start,
    )

    block = EDITOR[
        block_start:block_end
    ]

    assert "return 0" not in block
    assert "return None" in block
