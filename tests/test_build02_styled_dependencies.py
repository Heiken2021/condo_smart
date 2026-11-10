from pathlib import Path
V=Path("views/espacios.py").read_text(encoding="utf-8")
def test_dependencies_are_presented_as_metrics():
 assert 'st.markdown("**Dependencias asociadas**")' in V
 assert 'col.metric(label,int(total))' in V
 for x in ["Personas","Usuarios","Cargos","Pagos"]: assert x in V
def test_raw_dependency_dict_is_not_rendered():
 assert 'st.write("Dependencias",deps or {})' not in V
def test_dependency_feedback_is_user_friendly():
 assert "no puede eliminarse permanentemente" in V
 assert "no tiene dependencias asociadas y puede eliminarse" in V
