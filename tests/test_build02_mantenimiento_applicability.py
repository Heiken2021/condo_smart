from pathlib import Path

SQL=Path("database/migrations/032_expand_mantenimiento_ordinary_applicability_build02.sql").read_text(encoding="utf-8")

def test_adds_vertical_to_mantenimiento():
    assert "MANTENIMIENTO_ORDINARIO" in SQL
    assert "'VERTICAL',TRUE" in SQL
    assert "NOT EXISTS" in SQL

def test_does_not_modify_financial_lifecycle():
    for token in ("INSERT INTO financial_rules","INSERT INTO financial_rule_versions","INSERT INTO financial_obligations","space_fee_history"):
        assert token not in SQL
