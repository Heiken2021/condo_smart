from pathlib import Path


VIEW = Path(
    "views/finanzas.py"
).read_text(encoding="utf-8")


def test_finance_ui_has_structure_scope_selector():
    assert '"Alcance financiero"' in VIEW
    assert "financial_scope_options(" in VIEW
    assert "financial_scope_space_ids(" in VIEW


def test_finance_ui_filters_spaces_by_scope():
    assert "allowed_space_ids" in VIEW
    assert 'row["id"] in allowed' in VIEW


def test_finance_ui_filters_charge_and_payment_rows():
    assert "def _rows_in_scope(" in VIEW
    assert VIEW.count(
        "rows = _rows_in_scope("
    ) >= 2


def test_finance_summary_is_scope_aware():
    assert 'scope["kind"] == "ALL"' in VIEW
    assert "total_charges" in VIEW
    assert "total_payments" in VIEW


def test_structure_summary_does_not_assign_expenses():
    assert (
        "Los gastos y el disponible no se "
        in VIEW
    )
    assert (
        "ámbito general del inmueble"
        in VIEW
    )


def test_expenses_are_only_visible_at_property_scope():
    assert 'scope["kind"] != "ALL"' in VIEW
    assert (
        "no se atribuyen "
        in VIEW
    )


def test_statement_uses_only_scoped_spaces():
    assert "_space_options(" in VIEW
    assert "allowed_space_ids" in VIEW
    assert "spaces = _space_options(" in VIEW


def test_finance_scope_supports_direct_spaces():
    assert (
        "Vista limitada a espacios asociados "
        in VIEW
    )


def test_finance_scope_supports_descendants():
    assert (
        "estructura seleccionada y todos sus "
        in VIEW
    )


def test_finance_ui_does_not_write_structure_sql():
    for token in [
        "WITH RECURSIVE",
        "INSERT INTO estructura_inmueble",
        "UPDATE estructura_inmueble",
        "DELETE FROM estructura_inmueble",
    ]:
        assert token not in VIEW
