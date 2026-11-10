from pathlib import Path

V = Path(
    "views/performance_dashboard.py"
).read_text(encoding="utf-8")


def test_dashboard_imports_performance_agent():
    assert "from agents.performance_agent import (" in V
    assert "PerformanceAgent," in V
    assert "sanitize_snapshot," in V


def test_dashboard_uses_hybrid_agent():
    assert "PerformanceAgent().analyze(" in V
    assert "local_interpretation" in V


def test_dashboard_displays_analysis_source():
    assert "FUENTE: {source}" in V
    assert "source == 'IA'" in V
    assert "'source': 'LOCAL'" in V


def test_dashboard_displays_prompt_version():
    assert "PROMPT: {prompt_version}" in V
    assert "'performance-v1'" in V


def test_dashboard_keeps_agent_off_without_ai_call():
    assert "if enabled:" in V
    assert "'AGENTE_IA_APAGADO'" in V


def test_old_switch_label_block_was_removed():
    assert (
        "agent_label='🟢 ON · Agente en tiempo real'"
        not in V
    )
    assert "'[ON] Agente en tiempo real'" in V
    assert "'[OFF] Agente en tiempo real'" in V
