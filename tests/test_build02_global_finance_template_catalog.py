from pathlib import Path
GRID=Path("services/financial_rules_grid.py").read_text(encoding="utf-8")
CMD=Path("services/financial_governance_commands.py").read_text(encoding="utf-8")
FIN=Path("views/finanzas.py").read_text(encoding="utf-8")

def test_global_read_model_has_no_property_dependency():
    block=GRID[GRID.index("def list_global_financial_template_catalog("):]
    assert "property_id" not in block
    assert "financial_rule_definitions" in block
    assert "_applicability_map" in block

def test_global_applicability_has_no_synthetic_property():
    block=CMD[CMD.index("def set_global_financial_rule_applicability("):]
    assert "property_id=None" in block
    assert '"contexto":"GLOBAL"' in block
    assert '{"ROOT", "SUPERADMIN"}' in block

def test_global_finance_ui_connects_real_catalog():
    assert "list_global_financial_template_catalog(user=user)" in FIN
    assert "global_finance_template_catalog_grid" in FIN
    assert "set_global_financial_rule_applicability(" in FIN
    assert "Tipos de inmueble permitidos" in FIN
