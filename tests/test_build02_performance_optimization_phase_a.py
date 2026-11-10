from pathlib import Path
A=Path('app.py').read_text(encoding='utf-8')
C=Path('views/configuracion.py').read_text(encoding='utf-8')
S=Path('services/performance.py').read_text(encoding='utf-8')
V=Path('views/performance_dashboard.py').read_text(encoding='utf-8')


def test_runtime_initialization_is_cached_once():
    assert '@st.cache_resource' in A
    assert 'def _bootstrap_runtime_once' in A
    assert 'return tuple(check())' in A


def test_configuration_tabs_are_conditionally_rendered():
    assert "key='configuration_tabs'" in C
    assert "on_change='rerun'" in C
    for tab in ['identity_tab','settings_tab','security_tab','users_tab','performance_tab']:
        assert f'if {tab}.open:' in C
        assert f'with {tab}:' in C
    assert '.open: st.stop()' not in C


def test_agent_and_dashboard_share_one_cached_snapshot():
    assert '@st.cache_data(ttl=30' in S
    assert 'def performance_snapshot' in S
    assert 'snapshot=snapshot or performance_snapshot' in S
    assert 'local_interpretation=performance_agent_interpretation(' in V
    assert 'snapshot,' in V
    assert 'PerformanceAgent().analyze(' in V
    assert "health=snapshot['health']" in V
    assert "diagnostic=snapshot['diagnostic']" in V
    assert "data=snapshot['summary']" in V
    assert "rows=snapshot['history']" in V
