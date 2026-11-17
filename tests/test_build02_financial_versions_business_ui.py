from pathlib import Path


VIEW = Path(
    "views/financial_governance.py"
).read_text(encoding="utf-8")


def test_version_table_hides_none_values():
    assert (
        '"Sin fecha de término"'
        in VIEW
    )

    assert (
        'else "—"'
        in VIEW
    )


def test_version_start_date_is_business_formatted():
    version_start = VIEW.index(
        "with version_tab:"
    )

    block = VIEW[version_start:]

    assert (
        '_date('
        in block
    )


def test_version_approval_datetime_is_business_formatted():
    version_start = VIEW.index(
        "with version_tab:"
    )

    block = VIEW[version_start:]

    assert (
        '"%d/%m/%Y %H:%M"'
        in block
    )


def test_empty_configuration_message_is_generic():
    assert (
        "de sus parámetros configurables."
        in VIEW
    )

    assert (
        "de Importe, Frecuencia y Día "
        not in VIEW
    )
