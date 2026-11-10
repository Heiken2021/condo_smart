from pathlib import Path

V = Path('views/performance_dashboard.py').read_text(encoding='utf-8')


def test_agent_switch_defaults_off():
    assert "st.toggle(" in V
    assert "'[ON] Agente en tiempo real'" in V
    assert "'[OFF] Agente en tiempo real'" in V
    assert 'value=False' in V
    assert "key='performance_live_agent_enabled'" in V


def test_agent_refresh_is_dynamic():
    assert "AI_REFRESH_SECONDS = 60" in V
    assert "AI_CACHE_TTL_SECONDS = 300" in V
    assert "f'{AI_REFRESH_SECONDS}s'" in V
    assert '@fragment(run_every=run_every)' in V
    assert 'render_live_performance_agent(days,module,limit,agent_enabled)' in V


def test_telemetry_continues_when_agent_paused():
    assert 'La telemetría y el semáforo ' in V
    assert 'continúan funcionando sin actualización automática.' in V
    assert "'AGENTE_IA_APAGADO'" in V
