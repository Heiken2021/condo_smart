from pathlib import Path

GOV = Path('views/financial_governance.py').read_text(encoding='utf-8')
BUILDER = Path('views/financial_rule_visual_builder.py').read_text(encoding='utf-8')


def test_builder_is_inside_governance():
    assert '"Rule Visual Builder"' in GOV
    assert 'render_rule_visual_builder(' in GOV


def test_builder_has_six_visual_stages():
    for label in ('Definición','Disponibilidad','Alcance','Parámetros','Versión','Revisión'):
        assert label in BUILDER


def test_builder_has_advanced_pieces():
    assert 'Dependencias' in BUILDER
    assert 'Excepciones' in BUILDER


def test_builder_reuses_governed_catalog_and_code_suggestion():
    assert 'list_global_financial_rule_catalog(' in BUILDER
    assert 'suggest_financial_rule_code(' in BUILDER


def test_builder_is_draft_only_pilot():
    assert 'Draft-only' in BUILDER
    assert 'disabled=True' in BUILDER
    assert 'sin escrituras directas' in BUILDER


def test_builder_does_not_write_database_directly():
    for token in ('INSERT INTO ', 'UPDATE financial_', 'DELETE FROM ', 'core.db import execute', 'pool().connection'):
        assert token not in BUILDER
