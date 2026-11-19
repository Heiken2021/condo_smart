from pathlib import Path
G=Path("views/financial_governance.py").read_text(encoding="utf-8")
def test_unconfigured_is_blue(): assert 'return "🔵 Sin configurar"' in G
def test_attention_remains_orange(): assert '🟠 Requiere atención' in G
def test_incident_remains_red(): assert '🔴 Incidencia' in G
def test_draft_remains_warning(): assert '⚠️ Borrador' in G
