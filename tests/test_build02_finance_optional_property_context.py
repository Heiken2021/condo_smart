from pathlib import Path
APP=Path("app.py").read_text(encoding="utf-8")
FINANCE=Path("views/finanzas.py").read_text(encoding="utf-8")

def test_finance_does_not_trigger_global_property_modal():
    line=next(line for line in APP.splitlines() if line.startswith("PROPERTY_REQUIRED="))
    assert "'finanzas'" in line

def test_finance_opens_in_global_context_without_property():
    assert '"Todos los inmuebles"' in FINANCE
    assert '"Gobierno global", "Operación por inmueble"' in FINANCE
    assert 'El inmueble es un contexto operativo, no un requisito para entrar' in FINANCE

def test_property_operations_remain_explicitly_contextual():
    for label in ["Cargos", "Pagos", "Gastos", "Obligaciones", "estados de cuenta", "Workflow"]:
        assert label in FINANCE
    assert 'requieren un inmueble activo' in FINANCE

def test_global_context_does_not_write_or_fake_aggregates():
    global_block=FINANCE[FINANCE.index('if not property_id:'):FINANCE.index('property_data = st.session_state.get(')]
    for forbidden in ['create_charge(', 'register_payment(', 'register_expense(', 'financial_summary(']:
        assert forbidden not in global_block
