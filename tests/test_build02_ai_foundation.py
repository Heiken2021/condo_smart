from pathlib import Path

from core.ai.client import AIClient, AIConfigurationError
from core.ai.schemas import AgentAnalysis


def test_ai_schema_accepts_valid_analysis():
    result = AgentAnalysis(
        level="OPTIMO",
        confidence="Alta",
        headline="Rendimiento estable",
        summary="Las metricas permanecen dentro de la referencia.",
        evidence=["P95 estable"],
        probable_causes=[],
        recommendations=["Continuar monitorizando"],
        priority="BAJA",
        requires_human_review=False,
    )

    assert result.level == "OPTIMO"
    assert result.priority == "BAJA"


def test_ai_client_can_receive_fake_client_without_api_key():
    class FakeResponses:
        def parse(self, **kwargs):
            class Response:
                output_parsed = AgentAnalysis(
                    level="ATENCION",
                    confidence="Media",
                    headline="Prueba",
                    summary="Respuesta simulada",
                    evidence=[],
                    probable_causes=[],
                    recommendations=[],
                    priority="MEDIA",
                    requires_human_review=False,
                )
            return Response()

    class FakeClient:
        responses = FakeResponses()

    client = AIClient(model="test-model", client=FakeClient())

    result = client.structured_response(
        instructions="Prueba",
        input_text="Datos de prueba",
        schema=AgentAnalysis,
    )

    assert result.level == "ATENCION"


def test_ai_foundation_uses_responses_structured_output():
    source = Path("core/ai/client.py").read_text(encoding="utf-8")

    assert "client.responses.parse(" in source
    assert "text_format=schema" in source


def test_api_key_is_not_hardcoded():
    source = (
        Path("core/ai/config.py").read_text(encoding="utf-8")
        + Path("core/ai/client.py").read_text(encoding="utf-8")
    )

    assert "OPENAI_API_KEY" in source
    assert "sk-" not in source
