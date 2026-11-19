from pathlib import Path
B=Path("views/financial_rule_visual_builder.py").read_text(encoding="utf-8")
def test_atomic_command_connected(): assert "create_financial_rule_with_initial_draft" in B
def test_save_requires_manage_and_complete_and_property_scope(): assert "save_ready = all_ready and can_manage and property_scope" in B
def test_save_is_property_scope_only(): assert 'scope_level="INMUEBLE"' in B and '== "Todo el inmueble"' in B
def test_priority_is_mapped_to_governed_value(): assert 'priority=PRIORITY_VALUES[' in B
def test_success_tracks_created_ids(): assert 'saved_rule_id' in B and 'saved_version_id' in B
def test_approval_remains_disabled(): assert '"Enviar a aprobación", disabled=True' in B
def test_no_direct_approval_call(): assert 'approve_rule_version(' not in B
