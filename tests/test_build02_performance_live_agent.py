from pathlib import Path
S=Path('services/performance.py').read_text(encoding='utf-8')
V=Path('views/performance_dashboard.py').read_text(encoding='utf-8')

def test_agent_is_local_and_evidence_based():
 assert 'def performance_agent_interpretation' in S
 assert 'performance_health(days,module)' in S
 assert 'diagnostic_breakdown(days,module)' in S
 assert "'evidence'" in S and "'recommendations'" in S and "'confidence'" in S

def test_agent_interprets_layers_errors_and_modules():
 for value in ['Tasa de errores reciente','Capa dominante estimada','Módulo de mayor impacto','Operación más lenta']:
  assert value in S
 assert 'sql_pct>=50' in S and "health.get('trend')=='Degradación'" in S

def test_live_agent_uses_fragment_with_hybrid_ai():
 assert "AI_REFRESH_SECONDS = 60" in V
 assert "AI_CACHE_TTL_SECONDS = 300" in V
 assert "f'{AI_REFRESH_SECONDS}s'" in V
 assert "@fragment(run_every=run_every)" in V
 assert 'Agente De Interpretación En Vivo' in V
 assert 'Evidencia Interpretada' in V and 'Acciones Recomendadas' in V
 assert 'PerformanceAgent().analyze(' in V
 assert 'telemetría técnica sanitizada de Condo_Smart' in V
 assert 'FUENTE: {source}' in V
