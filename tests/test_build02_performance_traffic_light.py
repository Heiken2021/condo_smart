from pathlib import Path
S=Path('services/performance.py').read_text(encoding='utf-8')
V=Path('views/performance_dashboard.py').read_text(encoding='utf-8')

def test_health_uses_recent_and_historical_data():
 assert 'def performance_health' in S
 assert 'ROW_NUMBER() OVER(ORDER BY recorded_at DESC)' in S
 assert "FILTER(WHERE status='OK')" in S
 assert 'recent_limit=20' in S

def test_health_has_three_levels_and_score():
 for value in ['OPTIMO','ATENCION','CRITICO','score','error_rate','baseline_p95_ms']:
  assert value in S

def test_dashboard_renders_graphical_traffic_light():
 assert 'Estado actual del rendimiento' in V
 assert '#16A34A' in V and '#F59E0B' in V and '#DC2626' in V
 assert '¿Por qué aparece este estado?' in V
 assert 'P95 reciente' in V and 'Tendencia' in V
