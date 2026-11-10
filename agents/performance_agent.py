import json
from datetime import datetime

from core.ai import AIClient, AgentAnalysis


PROMPT_VERSION = "performance-v1"

SYSTEM_PROMPT = """
Eres el Agente de Inteligencia de Rendimiento de Condo_Smart.

Tu función es analizar exclusivamente la telemetría técnica proporcionada
por Condo_Smart para identificar degradaciones, anomalías, cuellos de
botella y posibles regresiones de rendimiento.

PRINCIPIOS OBLIGATORIOS:

1. La telemetría proporcionada por Condo_Smart es la fuente de verdad.
2. No inventes métricas, eventos, módulos, errores ni causas.
3. No recalcules ni sustituyas las métricas proporcionadas.
4. Distingue claramente hechos observados de causas probables.
5. Si no existe evidencia suficiente para una causa, indícalo.
6. Analiza P95, errores, tendencia, SQL, procesamiento de aplicación,
   operaciones y módulos cuando estos datos estén disponibles.
7. Prioriza las recomendaciones por impacto esperado y riesgo.
8. No recomiendes optimizaciones genéricas si la evidencia no las respalda.
9. No modifiques código, configuración, infraestructura ni datos.
10. Tu función es exclusivamente diagnóstica y consultiva.
11. Un estado crítico requiere atención prioritaria, pero no autoriza
    cambios automáticos.
12. Si los datos son insuficientes, utiliza SIN_DATOS.
13. El campo health.level proporcionado por Condo_Smart es la
    clasificación oficial de severidad. Respétalo exactamente en
    el campo level de tu respuesta.
14. Puedes asignar una prioridad superior y solicitar revisión humana
    cuando la evidencia lo justifique, pero no debes sustituir ni
    recalcular health.level.
15. Devuelve siempre la respuesta conforme al esquema estructurado
    definido por Condo_Smart.

El análisis debe ser conciso, técnico, explicable y útil para tomar
decisiones de optimización.
""".strip()


def sanitize_snapshot(snapshot):
    """
    Reduce el snapshot a telemetría técnica explícitamente autorizada.

    No se envían históricos completos, formularios, usuarios, correos,
    nombres de residentes ni otros datos personales.
    """
    health = snapshot.get("health") or {}
    diagnostic = snapshot.get("diagnostic") or {}
    operations = snapshot.get("operations") or []

    modules = diagnostic.get("modules") or []

    sanitized_operations = []
    for item in operations[:10]:
        sanitized_operations.append({
            "module": item.get("module"),
            "operation": item.get("operation"),
            "p95_ms": item.get("p95_ms"),
            "errors": item.get("errors"),
        })

    sanitized_modules = []
    for item in modules[:10]:
        sanitized_modules.append({
            "module": item.get("module"),
            "p95_ms": item.get("p95_ms"),
            "errors": item.get("errors"),
        })

    return {
        "health": {
            "level": health.get("level"),
            "label": health.get("label"),
            "score": health.get("score"),
            "trend": health.get("trend"),
            "recent_p95_ms": health.get("recent_p95_ms"),
            "error_rate": health.get("error_rate"),
            "recent_total": health.get("recent_total"),
            "baseline_total": health.get("baseline_total"),
        },
        "diagnostic": {
            "dominant_cause": diagnostic.get("dominant_cause"),
            "sql_pct": diagnostic.get("sql_pct"),
            "app_render_pct": diagnostic.get("app_render_pct"),
            "modules": sanitized_modules,
        },
        "operations": sanitized_operations,
    }


def _local_fallback(local_interpretation, reason):
    """
    Adapta el motor determinista existente al contrato común del agente.
    """
    level = local_interpretation.get("level", "SIN_DATOS")

    priority = {
        "OPTIMO": "BAJA",
        "ATENCION": "MEDIA",
        "CRITICO": "CRITICA",
        "SIN_DATOS": "BAJA",
    }.get(level, "MEDIA")

    return {
        "source": "LOCAL",
        "prompt_version": PROMPT_VERSION,
        "fallback_reason": reason,
        "generated_at": datetime.now().astimezone(),
        "analysis": AgentAnalysis(
            level=level,
            confidence=local_interpretation.get("confidence", "Baja"),
            headline=local_interpretation.get(
                "headline",
                "Análisis local de rendimiento",
            ),
            summary=local_interpretation.get(
                "summary",
                "La IA no está disponible; se utilizó el motor local.",
            ),
            evidence=local_interpretation.get("evidence", []),
            probable_causes=[],
            recommendations=local_interpretation.get("recommendations", []),
            priority=priority,
            requires_human_review=(level == "CRITICO"),
        ),
    }


class PerformanceAgent:
    def __init__(self, ai_client=None):
        self.ai_client = ai_client or AIClient()

    def analyze(self, snapshot, local_interpretation):
        if not self.ai_client.configured:
            return _local_fallback(
                local_interpretation,
                "IA_NO_CONFIGURADA",
            )

        payload = sanitize_snapshot(snapshot)

        try:
            analysis = self.ai_client.structured_response(
                instructions=SYSTEM_PROMPT,
                input_text=json.dumps(
                    payload,
                    ensure_ascii=False,
                    default=str,
                ),
                schema=AgentAnalysis,
            )

            official_level = (
                (snapshot.get("health") or {}).get("level")
                or local_interpretation.get("level")
                or "SIN_DATOS"
            )

            ai_original_level = analysis.level
            severity_aligned = (
                ai_original_level == official_level
            )

            if not severity_aligned:
                analysis = analysis.model_copy(
                    update={"level": official_level}
                )

            return {
                "source": "IA",
                "prompt_version": PROMPT_VERSION,
                "fallback_reason": None,
                "generated_at": datetime.now().astimezone(),
                "analysis": analysis,
                "official_level": official_level,
                "ai_original_level": ai_original_level,
                "severity_aligned": severity_aligned,
            }

        except Exception as exc:
            return _local_fallback(
                local_interpretation,
                f"IA_NO_DISPONIBLE:{type(exc).__name__}",
            )
