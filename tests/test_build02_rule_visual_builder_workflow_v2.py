from pathlib import Path

BUILDER = Path('views/financial_rule_visual_builder.py').read_text(encoding='utf-8')


def test_v2_is_guided_workflow():
    assert 'Workflow guiado' in BUILDER
    assert 'Una decisión por pantalla' in BUILDER
    assert 'Paso {step["number"]} de 6' in BUILDER


def test_v2_has_six_controlled_steps():
    for token in (
        '¿Qué quieres gobernar?',
        '¿Dónde podrá utilizarse?',
        '¿A quién debe aplicarse?',
        '¿Cómo debe funcionar?',
        '¿Desde cuándo tendrá vigencia?',
        '¿La regla está lista para enviarse?',
    ):
        assert token in BUILDER


def test_v2_has_gates_and_locking():
    assert 'Punto de control superado' in BUILDER
    assert 'Completa este paso para continuar' in BUILDER
    assert 'Bloqueado' in BUILDER
    assert '_first_incomplete(' in BUILDER


def test_v2_keeps_visual_map_and_contextual_branches():
    assert 'Mapa de la regla' in BUILDER
    assert 'Dependencias' in BUILDER
    assert 'Excepciones' in BUILDER
    assert 'Se muestran sólo cuando' in BUILDER


def test_v2_uses_business_language():
    assert 'Todo el inmueble' in BUILDER
    assert 'Una estructura o privada' in BUILDER
    assert 'Determinados espacios' in BUILDER
    assert 'Todo el inmueble' in BUILDER
    assert 'rule_definition_id' not in BUILDER


def test_v2_preserves_separate_approval_after_governed_draft_save():
    assert 'Draft-only' in BUILDER
    assert 'create_financial_rule_with_initial_draft' in BUILDER
    assert '"Enviar a aprobación", disabled=True' in BUILDER
    assert 'Enviar a aprobación", disabled=True' in BUILDER
    for token in ('INSERT INTO ', 'UPDATE financial_', 'DELETE FROM ', 'pool().connection'):
        assert token not in BUILDER
