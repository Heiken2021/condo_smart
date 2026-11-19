from pathlib import Path

BUILDER = Path("views/financial_rule_visual_builder.py").read_text(encoding="utf-8")
GRID = Path("services/financial_rules_grid.py").read_text(encoding="utf-8")


def test_catalog_exposes_governed_parameter_schema():
    block = GRID[GRID.index("def list_global_financial_rule_catalog("):]
    assert "definition.esquema_parametros" in block


def test_workflow_selects_catalog_definition():
    assert "Plantilla de regla" in BUILDER
    assert '"definition_id"' in BUILDER
    assert '"definition_code"' in BUILDER
    assert '"parameter_schema"' in BUILDER


def test_workflow_uses_existing_dynamic_parameter_engine():
    assert "render_parameter_inputs(" in BUILDER
    assert "missing_required_parameters(" in BUILDER
    assert "parameters_confirmed" not in BUILDER


def test_parameter_gate_is_automatic_and_blocking():
    assert "Todos los parámetros obligatorios son válidos." in BUILDER
    assert "Falta completar:" in BUILDER
    assert 'disabled=(index == 5 or not ready)' in BUILDER


def test_review_has_business_parameter_summary():
    assert "Parámetros configurados" in BUILDER
    assert "parameter_label(code)" in BUILDER
    assert "friendly_value(value)" in BUILDER


def test_030c_parameter_foundation_has_evolved_to_governed_save():
    assert 'create_financial_rule_with_initial_draft' in BUILDER
    assert '"Enviar a aprobación", disabled=True' in BUILDER
    assert 'Enviar a aprobación", disabled=True' in BUILDER
    for token in ("INSERT INTO ", "UPDATE financial_", "DELETE FROM ", "pool().connection"):
        assert token not in BUILDER
