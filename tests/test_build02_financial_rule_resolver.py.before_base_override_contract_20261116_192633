from pathlib import Path


SERVICE = Path(
    "services/financial_governance.py"
).read_text(encoding="utf-8")


def test_resolver_exposes_effective_rule_contract():
    assert "def resolve_effective_rule(" in SERVICE


def test_resolver_requires_governance_authorization():
    assert (
        "FINANZAS_GOBIERNO_CONSULTAR"
        in SERVICE
    )
    assert (
        "from core.authorization import require"
        in SERVICE
    )


def test_resolver_builds_property_space_context():
    assert "def _context(" in SERVICE
    assert "FROM condominios" in SERVICE
    assert "FROM espacios" in SERVICE


def test_resolver_builds_structure_ancestry():
    assert "WITH RECURSIVE ancestry AS" in SERVICE
    assert "parent.id=child.parent_id" in SERVICE


def test_resolver_knows_supported_dimensions():
    for token in [
        '"TIPO_INMUEBLE"',
        '"TIPO_ESTRUCTURA"',
        '"TIPO_ESPACIO"',
        '"GIRO"',
    ]:
        assert token in SERVICE


def test_resolver_does_not_invent_business_type():
    assert (
        "business_use_code"
        in SERVICE
    )
    assert (
        'context["dimensions"]["GIRO"].add'
        not in SERVICE
    )


def test_resolver_checks_definition_applicability():
    assert "def _definition_applicable(" in SERVICE
    assert "EXPLICITLY_EXCLUDED" in SERVICE
    assert "NO_INCLUDED_VALUE_MATCH" in SERVICE


def test_resolver_has_explicit_precedence():
    for token in [
        '"CORE": 100',
        '"TIPOLOGIA": 200',
        '"INMUEBLE": 300',
        '"ESTRUCTURA": 400',
        '"ESPACIO": 500',
    ]:
        assert token in SERVICE


def test_resolver_supports_ancestor_structure_rules():
    assert "def _structure_rank(" in SERVICE
    assert "structure_path" in SERVICE


def test_resolver_uses_only_approved_effective_versions():
    assert "version.estado_codigo='APROBADO'" in SERVICE
    assert "version.vigente_desde <= %s" in SERVICE
    assert "version.vigente_hasta >= %s" in SERVICE


def test_resolver_requires_specific_rules_to_be_overrides():
    assert (
        "SPECIFIC_RULE_REQUIRES_OVERRIDE"
        in SERVICE
    )


def test_resolver_uses_priority_and_version_order():
    assert "row[\"prioridad\"]" in SERVICE
    assert "row[\"version_num\"]" in SERVICE
    assert "reverse=True" in SERVICE


def test_resolver_supports_approved_exceptions():
    assert "def _approved_exception(" in SERVICE
    assert "estado_codigo='APROBADA'" in SERVICE
    assert "exception.get(\"parametros\")" in SERVICE


def test_resolver_returns_policy_and_objective():
    assert "FROM financial_policies" in SERVICE
    assert "FROM financial_objectives" in SERVICE
    assert '"policy": policy' in SERVICE
    assert '"objective": objective' in SERVICE


def test_resolver_returns_traceable_explanation():
    assert '"explanation": explanation' in SERVICE
    assert '"winner_scope"' in SERVICE
    assert '"candidate_count"' in SERVICE
    assert '"exception_applied"' in SERVICE


def test_resolver_returns_kpi_and_ai_flags():
    assert '"context_kpi"' in SERVICE
    assert '"context_ai"' in SERVICE


def test_ai_context_builder_exists():
    assert (
        "def build_financial_ai_context("
        in SERVICE
    )


def test_ai_context_is_read_and_recommend_only():
    for token in [
        '"ai_may_interpret": True',
        '"ai_may_recommend": True',
        '"ai_may_modify_rules": False',
        '"ai_may_approve_rules": False',
        (
            '"ai_may_execute_financial_actions": '
            "False"
        ),
    ]:
        assert token in SERVICE


def test_service_does_not_write_governance_data():
    forbidden = [
        "INSERT INTO financial_rules",
        "UPDATE financial_rules",
        "DELETE FROM financial_rules",
        "INSERT INTO financial_rule_versions",
        "UPDATE financial_rule_versions",
        "DELETE FROM financial_rule_versions",
        "INSERT INTO financial_rule_exceptions",
        "UPDATE financial_rule_exceptions",
        "DELETE FROM financial_rule_exceptions",
    ]

    for token in forbidden:
        assert token not in SERVICE


def test_service_has_no_ui_dependency():
    assert "import streamlit" not in SERVICE
    assert "st." not in SERVICE
