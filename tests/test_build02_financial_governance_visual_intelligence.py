from pathlib import Path

VIEW=Path("views/financial_governance.py").read_text(encoding="utf-8")

def test_both_grids_share_visual_semantics():
    assert "def _visual_semantics_legend(" in VIEW
    assert "_semantic_status(" in VIEW
    assert "_semantic_origin(" in VIEW
    assert "_semantic_assignment(" in VIEW
    assert "_semantic_applicability(" in VIEW
    assert "_semantic_priority(" in VIEW
    assert VIEW.count("_visual_semantics_legend()") >= 3

def test_semantic_legend_uses_operational_semaphore():
    for token in (
        "Semáforo operativo:",
        "🟢 Correcto",
        "🟠 Requiere atención",
        "🔴 Incidencia",
        "Contexto: Global / catálogo",
        "Heredado",
        "Sin configurar / no aplica",
    ):
        assert token in VIEW


def test_dashboard_is_read_only_and_has_two_contexts():
    assert "def _render_governance_dashboard(" in VIEW
    assert '"Gobierno global"' in VIEW
    assert '"Inmueble activo"' in VIEW
    assert "list_global_financial_rule_catalog(" in VIEW


def test_dashboard_has_executive_kpis_and_attention_required():
    for token in (
        "Dashboard ejecutivo de Gobierno Financiero",
        "Reglas",
        "Activas",
        "Compatibles",
        "No compatibles",
        "Cobertura compatible",
        "Reglas visibles",
        "Configuradas",
        "Con versión",
        "Requieren atención",
        "Cobertura configurada",
        "Atención prioritaria",
    ):
        assert token in VIEW


def test_dashboard_has_mixed_financial_governance_visuals():
    for token in (
        "mark_arc",
        "mark_bar",
        "Mapa de salud por dominio",
        "Compatibilidad del catálogo",
        "Cobertura de configuración",
    ):
        assert token in VIEW


def test_dashboard_uses_same_read_models():
    assert "list_global_financial_rule_catalog(" in VIEW
    assert "property_rows=filtered" in VIEW
    assert "_count_by(" in VIEW

def test_visual_intelligence_has_no_direct_database_writes():
    dashboard=VIEW[VIEW.index("def _render_governance_dashboard("):VIEW.index("def _render_rules(")]
    for token in ("INSERT INTO","UPDATE financial_","DELETE FROM","pool().connection"):
        assert token not in dashboard
