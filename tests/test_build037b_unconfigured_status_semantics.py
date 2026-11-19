from pathlib import Path
G=Path("views/financial_governance.py").read_text(encoding="utf-8")
def test_unconfigured_is_not_incident():
 assert 'return "🔵 Sin configurar"' in G
def test_unknown_state_keeps_incident_fallback():
 assert 'return "❓ Incompleta / Incidencia"' in G
def test_draft_keeps_warning_symbol(): assert 'return "⚠️ Borrador"' in G
def test_operational_semaphore_still_exists():
 assert '🟢 Correcto' in G and '🟠 Requiere atención' in G and '🔴 Incidencia' in G
