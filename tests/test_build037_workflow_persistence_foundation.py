from pathlib import Path
B=Path("views/financial_rule_visual_builder.py").read_text(encoding="utf-8")
def test_priority_levels_match_lifecycle():
 assert 'PRIORITY_LEVELS = ("Baja", "Normal", "Alta", "Crítica")' in B
 assert '"Normal": 200' in B
def test_normal_is_default_priority(): assert '"priority_level": "Normal"' in B
def test_review_shows_priority(): assert '("Prioridad", _get(property_id, "priority_level")' in B
def test_manage_permission_is_explicit(): assert 'FINANZAS_REGLA_GESTIONAR' in B
def test_approve_permission_is_explicit(): assert 'FINANZAS_REGLA_APROBAR' in B
def test_draft_save_is_enabled_but_approval_remains_disabled():
 assert 'create_financial_rule_with_initial_draft' in B
 assert '"Enviar a aprobación", disabled=True' in B
def test_builder_uses_only_atomic_draft_write_and_no_direct_approval():
 assert 'create_financial_rule(' not in B
 assert 'create_rule_version(' not in B
 assert 'approve_rule_version(' not in B
