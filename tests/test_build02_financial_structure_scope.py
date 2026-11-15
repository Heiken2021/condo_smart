from pathlib import Path


STRUCTURE = Path(
    "services/property_structure.py"
).read_text(encoding="utf-8")

FINANCE = Path(
    "services/finance.py"
).read_text(encoding="utf-8")


def test_structure_service_has_recursive_descendant_scope():
    assert "def descendant_node_ids(" in STRUCTURE
    assert "WITH RECURSIVE descendants AS" in STRUCTURE
    assert "child.parent_id=parent.id" in STRUCTURE


def test_descendant_scope_is_property_isolated():
    assert (
        "child.condominio_id="
        in STRUCTURE
    )
    assert "root.condominio_id=%s" in STRUCTURE


def test_structure_scope_supports_all_direct_and_node():
    assert "def structure_scope_spaces(" in STRUCTURE

    for token in [
        'scope_kind == "ALL"',
        'scope_kind == "DIRECT"',
        'scope_kind == "NODE"',
        "e.estructura_id IS NULL",
    ]:
        assert token in STRUCTURE


def test_node_scope_includes_descendants():
    assert "descendant_node_ids(" in STRUCTURE
    assert "e.estructura_id = ANY(%s)" in STRUCTURE


def test_finance_service_exposes_scope_options():
    assert "def financial_scope_options(" in FINANCE
    assert '"Todo el inmueble"' in FINANCE
    assert '"Espacios Directos"' in FINANCE
    assert "node_path(" in FINANCE


def test_finance_service_exposes_scope_space_ids():
    assert "def financial_scope_space_ids(" in FINANCE
    assert "structure_scope_spaces(" in FINANCE


def test_scope_does_not_change_financial_schema():
    for token in [
        "ALTER TABLE cargos",
        "ALTER TABLE pagos",
        "ALTER TABLE gastos",
        "ADD COLUMN estructura_id",
    ]:
        assert token not in FINANCE


def test_scope_does_not_assign_property_expenses_to_nodes():
    assert "structure_id" not in (
        "gastos"
    )
    assert (
        "distribute_expenses"
        not in FINANCE
    )


def test_scope_does_not_delete_financial_movements():
    for token in [
        "DELETE FROM cargos",
        "DELETE FROM pagos",
        "DELETE FROM gastos",
    ]:
        assert token not in FINANCE
