from pathlib import Path


VIEW = Path(
    "views/financial_governance.py"
).read_text(encoding="utf-8")


def test_console_has_three_areas():
    for token in (
        '"Reglas"',
        '"Cuotas"',
        '"Excepciones"',
    ):
        assert token in VIEW


def test_console_has_selectable_grid():
    assert 'selection_mode="single-row"' in VIEW
    assert 'on_select="rerun"' in VIEW


def test_console_has_rule_filters():
    for label in (
        '"Dominio"',
        '"Estado"',
        '"Alcance"',
    ):
        assert label in VIEW


def test_console_has_rule_detail():
    assert "Ficha de la regla" in VIEW
    assert '"Definición"' in VIEW
    assert '"Versiones"' in VIEW
    assert (
        '"Gobierno y auditoría"'
        in VIEW
    )


def test_console_delegates_rule_actions_to_lifecycle():
    assert (
        "render_rule_lifecycle_actions("
        in VIEW
    )

    lifecycle = Path(
        "views/financial_rule_lifecycle.py"
    ).read_text(encoding="utf-8")

    for label in (
        "Nueva regla",
        "Editar borrador",
        "Nueva versión",
        "Aprobar",
        "Finalizar vigencia",
        "Auditoría",
    ):
        assert label in lifecycle

def test_console_actions_are_disabled():
    assert "disabled=True" in VIEW


def test_console_displays_fee_grid():
    assert "list_space_fee_grid(" in VIEW
    assert "Sin regla asociada" in VIEW


def test_new_fee_is_temporarily_blocked():
    assert (
        "La creación de nuevas cuotas está "
        in VIEW
    )


def test_console_displays_exceptions():
    assert (
        "list_financial_exception_grid("
        in VIEW
    )


def test_console_has_no_direct_sql():
    for token in (
        "INSERT INTO",
        "UPDATE ",
        "DELETE FROM",
    ):
        assert token not in VIEW
