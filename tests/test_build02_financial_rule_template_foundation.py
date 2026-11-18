from pathlib import Path

MIGRATION = Path('database/migrations/030_financial_rule_template_foundation_build02.sql').read_text(encoding='utf-8')
SERVICE = Path('services/financial_rule_template_profiles.py').read_text(encoding='utf-8')


def test_030a_creates_versionable_jurisdiction_foundation():
    assert 'financial_rule_jurisdiction_profiles' in MIGRATION
    assert 'financial_rule_definition_profiles' in MIGRATION
    assert 'profile_version INTEGER' in MIGRATION
    assert "status_code IN ('DRAFT','APPROVED','RETIRED')" in MIGRATION


def test_030a_supports_incremental_geography():
    assert 'country_code VARCHAR' in MIGRATION
    assert 'state_code VARCHAR' in MIGRATION
    assert 'municipality_code VARCHAR' in MIGRATION
    assert 'parent_profile_id' in MIGRATION


def test_030a_separates_suggestions_constraints_and_legal_basis():
    assert 'suggested_values JSONB' in MIGRATION
    assert 'parameter_constraints JSONB' in MIGRATION
    assert 'locked_parameters JSONB' in MIGRATION
    assert 'legal_basis JSONB' in MIGRATION


def test_030a_does_not_seed_or_mutate_financial_rule_lifecycle():
    forbidden = (
        'INSERT INTO financial_rule_definitions',
        'INSERT INTO financial_rules',
        'INSERT INTO financial_rule_versions',
        'UPDATE financial_rule_versions',
        'UPDATE space_fee_history',
        'INSERT INTO financial_obligations',
    )
    for token in forbidden:
        assert token not in MIGRATION


def test_030a_service_is_read_only():
    assert 'list_jurisdiction_profiles' in SERVICE
    assert 'list_definition_profiles' in SERVICE
    assert 'get_approved_definition_profile' in SERVICE
    for token in ('execute(', 'INSERT INTO ', 'UPDATE ', 'DELETE FROM '):
        assert token not in SERVICE
