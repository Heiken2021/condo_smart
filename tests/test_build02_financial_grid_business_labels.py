from pathlib import Path


VIEW = Path(
    "views/financial_governance.py"
).read_text(encoding="utf-8")


def test_grid_uses_business_scope_language():
    assert (
        '"Nivel de aplicación"'
        in VIEW
    )

    assert (
        '"Aplica en"'
        in VIEW
    )

    assert (
        '"Alcance": ('
        not in VIEW
    )

    assert (
        '"Ámbito": ('
        not in VIEW
    )


def test_grid_explains_inheritance_semantically():
    assert (
        '"Herencia permitida"'
        in VIEW
    )

    assert (
        '== "Hereda"'
        in VIEW
    )


def test_grid_explains_configuration_type():
    assert (
        '"Tipo de configuración"'
        in VIEW
    )

    assert (
        '_semantic_assignment('
        in VIEW
    )
    assert (
        'row.get("override_label")'
        in VIEW
    )


def test_grid_hides_none_end_date():
    assert (
        '"Sin fecha de término"'
        in VIEW
    )


def test_grid_keeps_business_priority():
    assert (
        "business_priority("
        in VIEW
    )


def test_grid_keeps_business_status():
    assert (
        "business_status("
        in VIEW
    )


def test_grid_keeps_business_applicability():
    assert (
        "business_applicability("
        in VIEW
    )
