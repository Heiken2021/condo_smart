from pathlib import Path


VIEW = Path(
    "views/finanzas.py"
).read_text(encoding="utf-8")


def test_finance_view_is_functional():
    assert "Módulo reservado" not in VIEW
    assert 'title(' in VIEW
    assert '"Finanzas"' in VIEW


def test_finance_view_has_required_sections():
    for token in [
        '"Resumen"',
        '"Cargos"',
        '"Pagos"',
        '"Gastos"',
        '"Estado De Cuenta"',
    ]:
        assert token in VIEW


def test_finance_view_uses_service_layer():
    for token in [
        "financial_summary(",
        "list_charges(",
        "create_charge(",
        "list_payments(",
        "register_payment(",
        "list_expenses(",
        "register_expense(",
        "cancel_movement(",
        "account_statement(",
    ]:
        assert token in VIEW


def test_finance_view_checks_permissions():
    for token in [
        "FINANZAS_CONSULTAR",
        "FINANZAS_CARGO_CREAR",
        "FINANZAS_PAGO_REGISTRAR",
        "FINANZAS_GASTO_REGISTRAR",
        "FINANZAS_MOVIMIENTO_CANCELAR",
        "FINANZAS_ESTADO_CUENTA",
    ]:
        assert token in VIEW


def test_finance_view_requires_property_context():
    assert "property_id = cid()" in VIEW
    assert "if not property_id:" in VIEW


def test_finance_view_uses_property_header():
    assert "property_header(" in VIEW


def test_finance_view_uses_money_formatter():
    assert "from core.formatting import money" in VIEW
    assert "money(" in VIEW


def test_finance_view_has_period_filter():
    assert '"Periodo"' in VIEW
    assert '"AAAA-MM"' in VIEW


def test_finance_view_uses_active_spaces():
    assert "list_spaces(" in VIEW
    assert 'row.get("activo")' in VIEW
    assert "allowed_space_ids" in VIEW


def test_finance_view_cancellation_requires_reason():
    assert '"Motivo de cancelación"' in VIEW
    assert '"Confirmo la cancelación del movimiento"' in VIEW


def test_finance_view_explains_cancellation_traceability():
    assert (
        "conserva el movimiento "
        "original"
    ) in VIEW
    assert "trazabilidad financiera" in VIEW


def test_finance_view_does_not_expose_future_features():
    forbidden = [
        "Conciliación bancaria",
        "Índice De Sostenibilidad",
        "Reserva calculada",
        "Interés moratorio",
        "Facturación Fiscal",
    ]

    for token in forbidden:
        assert token not in VIEW


def test_finance_summary_does_not_claim_sustainability_kpi():
    assert (
        "No representa todavía un KPI de "
        "sostenibilidad financiera."
    ) in VIEW


def test_finance_view_does_not_write_sql_directly():
    for token in [
        "INSERT INTO cargos",
        "INSERT INTO pagos",
        "INSERT INTO gastos",
        "UPDATE cargos",
        "UPDATE pagos",
        "UPDATE gastos",
        "DELETE FROM cargos",
        "DELETE FROM pagos",
        "DELETE FROM gastos",
    ]:
        assert token not in VIEW
