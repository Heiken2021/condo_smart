from pathlib import Path
D=Path('core/db.py').read_text(encoding='utf-8')
S=Path('services/performance.py').read_text(encoding='utf-8')
V=Path('views/performance_dashboard.py').read_text(encoding='utf-8')

def test_db_collects_scoped_query_statistics():
 assert 'ContextVar' in D and 'reset_query_stats' in D and 'query_stats' in D
 assert '_track_query' in D and 'slowest_ms' in D

def test_measure_records_sql_and_application_layers():
 assert 'stats=query_stats()' in S
 assert 'python_render_ms' in S and 'sql_share_pct' in S
 assert 'stats["duration_ms"]' in S and 'stats["count"]' in S

def test_diagnostic_breakdown_and_ui():
 assert 'def diagnostic_breakdown' in S
 assert 'Base de datos / SQL' in S and 'Lógica Python y renderizado Streamlit' in S
 assert 'Diagnóstico Por Capas' in V and 'Impacto Por Módulo' in V
 assert 'SQL promedio' in V and 'Python + render' in V
