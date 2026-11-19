from pathlib import Path
G=Path("views/financial_governance.py").read_text(encoding="utf-8")
def test_operational_semaphore_preserved():
 assert "🟢 Correcto" in G and "🟠 Requiere atención" in G and "🔴 Incidencia" in G
def test_coloured_status_symbols_are_distinct():
 for value in ["⚠️ Borrador","➡️ Pendiente de aprobación","✅ Aprobada / Vigente","❌ Rechazada","❓ Incompleta / Incidencia","⏹️ Finalizada"]: assert value in G
def test_main_grid_has_both_semaphore_and_state():
 assert '"Semáforo": _operational_semaphore(row["status"])' in G
 assert '"Estado": _semantic_status(row["status"])' in G
def test_approved_and_final_are_not_confusable(): assert "✅ Aprobada / Vigente" in G and "⏹️ Finalizada" in G
