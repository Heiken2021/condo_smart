from pathlib import Path

MIGRATION = Path(
    'database/migrations/032_maintenance_plaza_applicability_build02.sql'
).read_text(encoding='utf-8')
PRESENTER = Path(
    'services/financial_rule_presenter.py'
).read_text(encoding='utf-8')


def test_maintenance_is_enabled_for_commercial_plazas():
    assert "definition.codigo='MANTENIMIENTO_ORDINARIO'" in MIGRATION
    assert "'PLAZA_COMERCIAL'" in MIGRATION
    assert "DO UPDATE SET incluido=EXCLUDED.incluido" in MIGRATION


def test_migration_does_not_duplicate_template_or_create_lifecycle():
    assert 'INSERT INTO financial_rule_definitions' not in MIGRATION
    assert 'INSERT INTO financial_rules' not in MIGRATION
    assert 'INSERT INTO financial_rule_versions' not in MIGRATION
    assert 'Plaza Satélite' not in MIGRATION
    assert 'Las Misiones I' not in MIGRATION


def test_business_presenter_supports_governed_property_types():
    assert 'TIPO_INMUEBLE:FRACCIONAMIENTO' in PRESENTER
    assert 'TIPO_INMUEBLE:PLAZA_COMERCIAL' in PRESENTER
    assert 'TIPO_INMUEBLE:VERTICAL' in PRESENTER
    assert 'Plaza comercial' in PRESENTER
