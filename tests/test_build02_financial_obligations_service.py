from pathlib import Path


SERVICE = Path(
    "services/financial_obligations.py"
).read_text(encoding="utf-8")


def test_service_exposes_obligation_commands():
    assert "def create_financial_obligation(" in SERVICE
    assert "def cancel_financial_obligation(" in SERVICE


def test_service_exposes_allocation_commands():
    assert "def apply_payment_to_obligation(" in SERVICE
    assert "def reverse_payment_allocation(" in SERVICE


def test_service_exposes_read_contracts():
    assert "def get_obligation_balance(" in SERVICE
    assert "def list_financial_obligations(" in SERVICE


def test_service_uses_server_side_authorization():
    assert "from core.authorization import require" in SERVICE


def test_create_obligation_uses_permission():
    assert "FINANZAS_OBLIGACION_CREAR" in SERVICE


def test_cancel_obligation_uses_permission():
    assert "FINANZAS_OBLIGACION_CANCELAR" in SERVICE


def test_apply_payment_uses_permission():
    assert "FINANZAS_PAGO_APLICAR" in SERVICE


def test_reverse_allocation_uses_permission():
    assert (
        "FINANZAS_PAGO_REVERTIR_APLICACION"
        in SERVICE
    )


def test_reads_use_governance_read_permission():
    assert "FINANZAS_GOBIERNO_CONSULTAR" in SERVICE


def test_service_validates_positive_money():
    assert "def _money(" in SERVICE
    assert "amount <= Decimal" in SERVICE


def test_service_validates_period():
    assert "def _period(" in SERVICE
    assert "INVALID_FINANCIAL_OBLIGATION_PERIOD" in SERVICE


def test_obligation_uses_real_space_context():
    assert "FROM espacios" in SERVICE
    assert (
        "FINANCIAL_OBLIGATION_STRUCTURE_CONTEXT_MISMATCH"
        in SERVICE
    )


def test_obligation_preserves_governance_provenance():
    assert "rule_version_id" in SERVICE
    assert "space_fee_history_id" in SERVICE


def test_obligation_creation_is_audited():
    assert "FINANCIAL_OBLIGATION_CREATED" in SERVICE


def test_obligation_cancellation_is_locked():
    assert "FROM financial_obligations" in SERVICE
    assert "FOR UPDATE" in SERVICE
    assert (
        "FINANCIAL_OBLIGATION_NOT_CANCELLABLE"
        in SERVICE
    )


def test_obligation_cancellation_is_audited():
    assert "FINANCIAL_OBLIGATION_CANCELLED" in SERVICE


def test_allocation_locks_payment_and_obligation():
    assert "FROM pagos" in SERVICE
    assert SERVICE.count("FOR UPDATE") >= 4


def test_allocation_supports_approved_exception_reference():
    assert "financial_rule_exception_id" in SERVICE
    assert "exception_id" in SERVICE


def test_allocation_is_audited():
    assert (
        "PAYMENT_ALLOCATED_TO_OBLIGATION"
        in SERVICE
    )


def test_reversal_is_explicit_and_attributed():
    for token in [
        "reversado_por",
        "reversado_en",
        "motivo_reversion",
    ]:
        assert token in SERVICE


def test_reversal_requires_reason():
    assert (
        "PAYMENT_ALLOCATION_REVERSAL_REASON_REQUIRED"
        in SERVICE
    )


def test_reversal_is_audited():
    assert "PAYMENT_ALLOCATION_REVERSED" in SERVICE


def test_commands_are_atomic():
    assert "connection.commit()" in SERVICE
    assert "connection.rollback()" in SERVICE


def test_commands_return_traceability():
    assert '["audit_event_id"]' in SERVICE
    assert '["trace_id"]' in SERVICE


def test_service_uses_derived_balance_view():
    assert "financial_obligation_balances" in SERVICE


def test_service_does_not_modify_legacy_charges():
    for token in [
        "INSERT INTO cargos",
        "UPDATE cargos",
        "DELETE FROM cargos",
    ]:
        assert token not in SERVICE


def test_service_does_not_create_payments():
    assert "INSERT INTO pagos" not in SERVICE


def test_service_has_no_ui_dependency():
    assert "import streamlit" not in SERVICE
    assert "st." not in SERVICE
