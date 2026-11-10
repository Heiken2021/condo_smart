from pathlib import Path


V = Path(
    'views/performance_dashboard.py'
).read_text(encoding='utf-8')


def test_ai_cache_has_bounded_ttl():
    assert 'AI_REFRESH_SECONDS = 60' in V
    assert 'AI_CACHE_TTL_SECONDS = 300' in V
    assert 'cache_age < AI_CACHE_TTL_SECONDS' in V


def test_ai_cache_depends_on_sanitized_telemetry():
    assert 'sanitize_snapshot(snapshot)' in V
    assert 'sort_keys=True' in V
    assert 'hashlib.sha256' in V
    assert 'cached_fingerprint == fingerprint' in V


def test_ai_provider_is_skipped_on_cache_hit():
    cache_check = V.index('if cache_valid:')
    provider_call = V.index(
        'result=PerformanceAgent().analyze('
    )
    assert cache_check < provider_call
    assert 'return cached_result, True, cache_age' in V


def test_ai_is_not_called_when_switch_is_off():
    enabled_branch = V.index('if enabled:')
    disabled_branch = V.index(
        "'fallback_reason': 'AGENTE_IA_APAGADO'",
        enabled_branch,
    )
    provider_call = V.index(
        '_performance_ai_result(',
        enabled_branch,
    )
    assert enabled_branch < provider_call < disabled_branch


def test_local_performance_analysis_remains_available():
    assert 'performance_agent_interpretation(' in V
    assert "'source': 'LOCAL'" in V
    assert "'analysis': None" in V
    assert "AGENTE_IA_APAGADO" in V
    assert "performance_agent_interpretation(" in V


def test_cache_status_is_visible():
    assert 'if cache_hit:' in V
    assert 'Resultado IA reutilizado desde caché' in V
    assert 'Resultado IA actualizado con la telemetría' in V
