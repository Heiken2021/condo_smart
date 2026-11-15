from pathlib import Path


SERVICE = Path(
    "services/finance.py"
).read_text(encoding="utf-8")


def test_finance_service_exposes_foundation_contract():
    for token in [
        "def list_charges(",
        "def create_charge(",
        "def list_payments(",
        "def register_payment(",
        "def list_expenses(",
        "def register_expense(",
        "def cancel_movement(",
        "def account_statement(",
        "def financial_summary(",
    ]:
        assert token in SERVICE


def test_finance_service_uses_server_side_authorization():
    for token in [
        "FINANZAS_CONSULTAR",
        "FINANZAS_CARGO_CREAR",
        "FINANZAS_PAGO_REGISTRAR",
        "FINANZAS_GASTO_REGISTRAR",
        "FINANZAS_MOVIMIENTO_CANCELAR",
        "FINANZAS_ESTADO_CUENTA",
    ]:
        assert token in SERVICE

    assert "from core.authorization import require" in SERVICE


def test_finance_service_requires_active_actor():
    assert "def _actor(" in SERVICE
    assert "USER_INACTIVE" in SERVICE


def test_finance_service_validates_property_space_scope():
    assert "def _validate_space(" in SERVICE
    assert "FINANCIAL_SPACE_NOT_FOUND" in SERVICE
    assert "FINANCIAL_SPACE_INACTIVE" in SERVICE
    assert "condominio_id=%s" in SERVICE


def test_finance_service_validates_positive_amount():
    assert "def _amount(" in SERVICE
    assert "FINANCIAL_AMOUNT_MUST_BE_POSITIVE" in SERVICE


def test_finance_service_validates_period():
    assert "PERIOD_PATTERN" in SERVICE
    assert "INVALID_FINANCIAL_PERIOD" in SERVICE


def test_financial_write_and_audit_share_connection():
    assert "with pool().connection() as connection:" in SERVICE
    assert "cursor.execute(" in SERVICE
    assert "_insert_financial_audit(" in SERVICE


def test_financial_service_has_explicit_commit_and_rollback():
    assert "connection.commit()" in SERVICE
    assert "connection.rollback()" in SERVICE
    assert "except Exception:" in SERVICE


def test_financial_audit_uses_shared_trace_id():
    assert "trace_id = new_trace_id()" in SERVICE
    assert "trace_id=trace_id" in SERVICE
    assert "INSERT INTO auditoria_financiera" in SERVICE


def test_financial_audit_metadata_is_sanitized():
    assert "sanitize(" in SERVICE
    assert "json.dumps(" in SERVICE


def test_financial_cancellation_uses_row_lock():
    assert "FOR UPDATE" in SERVICE
    assert "FINANCIAL_MOVEMENT_ALREADY_CANCELLED" in SERVICE


def test_financial_cancellation_does_not_delete():
    assert "DELETE FROM cargos" not in SERVICE
    assert "DELETE FROM pagos" not in SERVICE
    assert "DELETE FROM gastos" not in SERVICE


def test_financial_service_does_not_edit_economic_data():
    forbidden = [
        "SET monto_mxn=",
        "SET periodo=",
        "SET concepto=",
        "SET categoria_codigo=",
        "SET espacio_id=",
        "SET condominio_id=",
    ]

    for token in forbidden:
        assert token not in SERVICE


def test_account_statement_separates_charges_and_payments():
    assert '"charges": charges' in SERVICE
    assert '"payments": payments' in SERVICE
    assert '"balance": total_charges - total_payments' in SERVICE


def test_financial_summary_does_not_invent_kpis():
    assert '"charges": total_charges' in SERVICE
    assert '"payments": total_payments' in SERVICE
    assert '"expenses": total_expenses' in SERVICE
    assert "sustainability" not in SERVICE.lower()


def test_finance_service_has_no_ui_dependency():
    assert "import streamlit" not in SERVICE
    assert "st." not in SERVICE
