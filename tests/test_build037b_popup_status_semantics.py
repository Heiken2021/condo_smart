from pathlib import Path
G=Path("views/financial_governance.py").read_text(encoding="utf-8")
B=Path("views/financial_rule_visual_builder.py").read_text(encoding="utf-8")
def test_semantic_status_symbols():
 for value in ["⚠️ Borrador","➡️ Pendiente de aprobación","✅ Aprobada / Vigente","❌ Rechazada","❓ Incompleta / Incidencia","⏹️ Finalizada"]: assert value in G
def test_grid_uses_semantic_status(): assert '"Estado": _semantic_status(row["status"])' in G
def test_version_grid_uses_semantic_status(): assert '_semantic_status(version["estado_codigo"])' in G
def test_saved_dialog_exists(): assert '@st.dialog("Borrador guardado correctamente")' in B
def test_dialog_shows_business_summary():
 for value in ["Disponibilidad","Alcance","Herencia","Override","Prioridad","Vigencia","Parámetros configurados"]: assert value in B
def test_approval_remains_disabled(): assert '"Enviar a aprobación", disabled=True' in B
