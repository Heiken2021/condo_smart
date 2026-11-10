from pathlib import Path
M=Path('database/migrations/012_performance_observability_build02.sql').read_text()
S=Path('services/performance.py').read_text()
V=Path('views/performance_dashboard.py').read_text()
C=Path('views/configuracion.py').read_text()
A=Path('app.py').read_text()
P=Path('components/processing_status.py').read_text()
def test_schema():
 for x in ['performance_events','duration_ms','build_version','metadata_json']: assert x in M
def test_service():
 for x in ['class measure','def record_event','def summary','def history','PERCENTILE_CONT']: assert x in S
def test_configuration_dashboard():
 assert "'Rendimiento'" in C and 'render_performance()' in C
 assert 'performance_history_grid' in V and "selection_mode='single-row'" in V
def test_processing_feedback():
 assert 'st.status' in P and 'module_status=st.status' in A
 assert "with measure(nav,'module_render'" in A
def test_privacy():
 for x in ['password','email','telefono','persona_nombre']: assert x not in M.lower()



def test_safe_exception_telemetry_contract():
 assert '"exception_type"' in S
 assert "exc_type.__name__" in S
 assert "status='OK'" in S
 assert "status='RERUN'" in S
 assert "status='ERROR'" in S
 assert "exc_type.__name__ == 'RerunException'" in S
 assert 'return False' in S


def test_exception_telemetry_does_not_store_sensitive_details():
 assert '"exception_message"' not in S
 assert '"traceback"' not in S
 assert 'str(exc)' not in S
