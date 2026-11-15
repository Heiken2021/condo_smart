from pathlib import Path


SERVICE = Path(
    "services/financial_obligations.py"
).read_text(encoding="utf-8")


def test_generator_exists():
    assert (
        "def generate_governed_obligation("
        in SERVICE
    )


def test_generator_resolves_rule():
    assert (
        "resolve_effective_rule("
        in SERVICE
    )


def test_generator_requires_effective_rule():
    assert (
        "EFFECTIVE_FINANCIAL_RULE_REQUIRED"
        in SERVICE
    )


def test_generator_reads_effective_fee():
    assert (
        "def _effective_space_fee("
        in SERVICE
    )
    assert "FROM space_fee_history" in SERVICE


def test_generator_requires_approved_fee():
    assert (
        "estado_codigo='APROBADO'"
        in SERVICE
    )
    assert (
        "EFFECTIVE_APPROVED_SPACE_FEE_REQUIRED"
        in SERVICE
    )


def test_generator_uses_fee_effective_date():
    assert "vigente_desde <= %s" in SERVICE
    assert "vigente_hasta >= %s" in SERVICE


def test_generator_validates_rule_fee_provenance():
    assert (
        "SPACE_FEE_RULE_VERSION_MISMATCH"
        in SERVICE
    )


def test_generator_requires_space_context():
    assert (
        "FINANCIAL_RULE_SPACE_CONTEXT_REQUIRED"
        in SERVICE
    )


def test_generator_checks_duplicate_periodic_obligation():
    assert "FROM financial_obligations" in SERVICE
    assert (
        "ACTIVE_PERIODIC_OBLIGATION_ALREADY_EXISTS"
        in SERVICE
    )


def test_duplicate_check_is_property_scoped():
    assert "condominio_id=%s" in SERVICE


def test_duplicate_check_is_space_scoped():
    assert "espacio_id=%s" in SERVICE


def test_duplicate_check_is_period_scoped():
    assert "periodo=%s" in SERVICE


def test_duplicate_check_is_type_scoped():
    assert "tipo_codigo=%s" in SERVICE


def test_generator_creates_obligation_through_service():
    assert (
        "create_financial_obligation("
        in SERVICE
    )


def test_generator_uses_fee_amount():
    assert 'amount=fee["monto_mxn"]' in SERVICE


def test_generator_freezes_rule_version():
    assert (
        'rule_version_id=('
        in SERVICE
    )
    assert (
        'selected["version_id"]'
        in SERVICE
    )


def test_generator_freezes_fee_version():
    assert (
        "space_fee_history_id="
        in SERVICE
    )


def test_generator_returns_governance_context():
    assert (
        '"governance_context"'
        in SERVICE
    )


def test_governance_context_supports_kpi():
    assert '"context_kpi"' in SERVICE


def test_governance_context_supports_ai():
    assert '"context_ai"' in SERVICE


def test_generator_does_not_modify_legacy_charge():
    for token in [
        "INSERT INTO cargos",
        "UPDATE cargos",
        "DELETE FROM cargos",
    ]:
        assert token not in SERVICE


def test_generator_does_not_create_payment():
    assert "INSERT INTO pagos" not in SERVICE


def test_generator_has_no_ui_dependency():
    assert "import streamlit" not in SERVICE
    assert "st." not in SERVICE
