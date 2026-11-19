from pathlib import Path
S=Path("services/financial_governance_commands.py").read_text(encoding="utf-8")
def test_atomic_creator_exists(): assert "def create_financial_rule_with_initial_draft(" in S
def test_atomic_creator_uses_single_connection_block():
 block=S.split("def create_financial_rule_with_initial_draft(",1)[1].split("def create_rule_version(",1)[0]
 assert block.count("with pool().connection() as connection:")==1
 assert block.count("connection.commit()")==1
 assert block.count("connection.rollback()")==1
def test_atomic_creator_builds_rule_and_v1_draft():
 block=S.split("def create_financial_rule_with_initial_draft(",1)[1].split("def create_rule_version(",1)[0]
 assert "INSERT INTO financial_rules" in block
 assert "INSERT INTO financial_rule_versions" in block
 assert "'BORRADOR'" in block and "version_num" in block
def test_atomic_creator_requires_manage_permission():
 block=S.split("def create_financial_rule_with_initial_draft(",1)[1].split("def create_rule_version(",1)[0]
 assert "FINANZAS_REGLA_GESTIONAR" in block
def test_atomic_creator_validates_parameters():
 block=S.split("def create_financial_rule_with_initial_draft(",1)[1].split("def create_rule_version(",1)[0]
 assert "_validate_rule_parameters(" in block
def test_atomic_creator_audits_both_records():
 block=S.split("def create_financial_rule_with_initial_draft(",1)[1].split("def create_rule_version(",1)[0]
 assert "FINANCIAL_RULE_CREATED" in block and "FINANCIAL_RULE_VERSION_CREATED" in block
