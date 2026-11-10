from agents.performance_agent import (
    PROMPT_VERSION,
    SYSTEM_PROMPT,
    PerformanceAgent,
    sanitize_snapshot,
)
from core.ai.schemas import AgentAnalysis


SNAPSHOT = {
    "health": {
        "level": "ATENCION",
        "label": "Atención",
        "score": 74,
        "trend": "Degradación",
        "recent_p95_ms": 1800,
        "error_rate": 2.5,
        "recent_total": 30,
        "baseline_total": 20,
    },
    "diagnostic": {
        "dominant_cause": "Aplicación / render",
        "sql_pct": 30,
        "app_render_pct": 70,
        "modules": [
            {
                "module": "Inmuebles",
                "p95_ms": 1800,
                "errors": 0,
            }
        ],
    },
    "operations": [
        {
            "module": "Inmuebles",
            "operation": "render",
            "p95_ms": 1800,
            "errors": 0,
            "metadata_json": "NO_DEBE_SALIR",
        }
    ],
    "history": [
        {
            "metadata_json": "NO_DEBE_SALIR",
        }
    ],
}


LOCAL = {
    "level": "ATENCION",
    "confidence": "Alta",
    "headline": "Atención local",
    "summary": "Diagnóstico determinista",
    "evidence": ["P95 elevado"],
    "recommendations": ["Revisar render"],
}


def test_snapshot_is_sanitized():
    result = sanitize_snapshot(SNAPSHOT)

    assert "history" not in result
    assert "metadata_json" not in str(result)
    assert result["health"]["recent_p95_ms"] == 1800


def test_agent_uses_ai_when_available():
    class FakeAI:
        configured = True

        def structured_response(self, **kwargs):
            return AgentAnalysis(
                level="ATENCION",
                confidence="Alta",
                headline="Análisis IA",
                summary="La degradación se concentra en render.",
                evidence=["P95 de 1800 ms"],
                probable_causes=["Render de aplicación"],
                recommendations=["Revisar reruns"],
                priority="MEDIA",
                requires_human_review=False,
            )

    result = PerformanceAgent(FakeAI()).analyze(SNAPSHOT, LOCAL)

    assert result["source"] == "IA"
    assert result["analysis"].headline == "Análisis IA"
    assert result["prompt_version"] == PROMPT_VERSION


def test_agent_falls_back_when_ai_not_configured():
    class FakeAI:
        configured = False

    result = PerformanceAgent(FakeAI()).analyze(SNAPSHOT, LOCAL)

    assert result["source"] == "LOCAL"
    assert result["fallback_reason"] == "IA_NO_CONFIGURADA"
    assert result["analysis"].headline == "Atención local"


def test_agent_falls_back_if_provider_fails():
    class FakeAI:
        configured = True

        def structured_response(self, **kwargs):
            raise TimeoutError("simulado")

    result = PerformanceAgent(FakeAI()).analyze(SNAPSHOT, LOCAL)

    assert result["source"] == "LOCAL"
    assert "TimeoutError" in result["fallback_reason"]


def test_prompt_has_grounding_guardrails():
    from agents.performance_agent import SYSTEM_PROMPT

    assert "No inventes métricas" in SYSTEM_PROMPT
    assert "fuente de verdad" in SYSTEM_PROMPT
    assert "exclusivamente diagnóstica" in SYSTEM_PROMPT



def test_health_level_is_authoritative_when_ai_disagrees():
    class FakeAI:
        configured = True

        def structured_response(self, **kwargs):
            return AgentAnalysis(
                level="CRITICO",
                confidence="Alta",
                headline="IA detecta riesgo elevado",
                summary="La IA considera elevada la prioridad.",
                evidence=["P95 elevado"],
                probable_causes=["Render"],
                recommendations=["Revisar render"],
                priority="CRITICA",
                requires_human_review=True,
            )

    result = PerformanceAgent(FakeAI()).analyze(
        SNAPSHOT,
        LOCAL,
    )

    assert result["source"] == "IA"

    # ATENCION procede de SNAPSHOT["health"]["level"].
    assert result["analysis"].level == "ATENCION"

    # Conservamos la clasificación original de la IA
    # para auditoría y diagnóstico.
    assert result["ai_original_level"] == "CRITICO"
    assert result["official_level"] == "ATENCION"
    assert result["severity_aligned"] is False

    # La alineación del nivel no elimina la capacidad
    # de elevar prioridad o solicitar revisión humana.
    assert result["analysis"].priority == "CRITICA"
    assert result["analysis"].requires_human_review is True


def test_matching_ai_severity_is_preserved():
    class FakeAI:
        configured = True

        def structured_response(self, **kwargs):
            return AgentAnalysis(
                level="ATENCION",
                confidence="Alta",
                headline="Análisis alineado",
                summary="La IA coincide con la telemetría.",
                evidence=["P95 elevado"],
                probable_causes=["Render"],
                recommendations=["Revisar render"],
                priority="ALTA",
                requires_human_review=False,
            )

    result = PerformanceAgent(FakeAI()).analyze(
        SNAPSHOT,
        LOCAL,
    )

    assert result["analysis"].level == "ATENCION"
    assert result["ai_original_level"] == "ATENCION"
    assert result["official_level"] == "ATENCION"
    assert result["severity_aligned"] is True


def test_prompt_declares_health_level_authoritative():
    assert (
        "health.level proporcionado por Condo_Smart es la"
        in SYSTEM_PROMPT
    )
    assert (
        "clasificación oficial de severidad"
        in SYSTEM_PROMPT
    )
