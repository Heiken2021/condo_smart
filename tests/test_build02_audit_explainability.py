from pathlib import Path


S = Path(
    "services/audit_service.py"
).read_text(encoding="utf-8")

V = Path(
    "views/auditoria.py"
).read_text(encoding="utf-8")


def test_system_status_explanation_exists():
    assert "def system_status_explanation(" in S
    assert '"summary"' in S
    assert '"reason"' in S
    assert '"trigger"' in S
    assert '"criteria"' in S
    assert '"recommendation"' in S


def test_financial_status_explanation_exists():
    assert "def financial_status_explanation(" in S


def test_critical_system_status_explains_reason():
    assert "Se detectaron" in S
    assert "evento(s) críticos" in S
    assert "resultado fallido" in S
    assert "acceso denegado" in S


def test_warning_system_status_explains_reason():
    assert "revocaciones" in S
    assert "desactivaciones" in S
    assert "cambios de configuración" in S


def test_normal_system_status_explains_reason():
    assert '"severity": "NORMAL"' in S
    assert "No se detectaron eventos críticos" in S
    assert "El estado permanece Normal" in S
    assert "No se requiere una acción inmediata" in S


def test_financial_critical_status_explains_reason():
    assert "cancelación" in S
    assert "anulación" in S
    assert "reversión" in S


def test_financial_warning_status_explains_reason():
    assert "ajustes" in S
    assert "correcciones" in S


def test_financial_normal_status_explains_reason():
    assert "El ledger financiero está activo" in S


def test_status_card_shows_explanation_fields():
    assert "¿Por qué?" in V
    assert "Evento detonante:" in V
    assert "Criterio utilizado:" in V
    assert "Recomendación:" in V


def test_status_card_identifies_rule_based_evaluation():
    assert (
        "Evaluación automática basada en reglas"
        in V
    )


def test_system_dashboard_uses_explanation():
    assert "system_status_explanation(" in V


def test_financial_dashboard_uses_explanation():
    assert "financial_status_explanation(" in V


def test_explanation_does_not_claim_ai_analysis():
    forbidden = [
        "Evaluación realizada por OpenAI",
        "Diagnóstico generado por IA",
        "Copilot determinó",
    ]

    for text in forbidden:
        assert text not in V
        assert text not in S


def test_future_ai_can_remain_separate_from_rule_engine():
    assert "system_severity(" in S
    assert "financial_severity(" in S
    assert "system_status_explanation(" in S
    assert "financial_status_explanation(" in S
