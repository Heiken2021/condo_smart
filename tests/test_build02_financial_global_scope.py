from pathlib import Path

MIGRATION=Path("database/migrations/029_financial_global_scope_build02.sql").read_text(encoding="utf-8")
VIEW=Path("views/financial_rule_lifecycle.py").read_text(encoding="utf-8")

def test_global_scope_migration_is_non_seeded():
    assert "'GLOBAL'" in MIGRATION
    assert "INSERT INTO financial_rules" not in MIGRATION
    assert "INSERT INTO financial_rule_versions" not in MIGRATION
    assert "space_fee_history" not in MIGRATION

def test_rule_lifecycle_offers_global_scope():
    assert '"GLOBAL"' in VIEW
