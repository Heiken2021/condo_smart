from datetime import date
from decimal import Decimal

import pytest

import services.financial_obligations as obligations


class FakeCursor:
    def __init__(self, fail_audit=False):
        self.fail_audit = fail_audit
        self.current = None
        self.statements = []

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        return False

    def execute(self, sql, params=()):
        normalized = " ".join(
            sql.split()
        )

        self.statements.append(
            (normalized, params)
        )

        if (
            self.fail_audit
            and
            "INSERT INTO auditoria_financiera"
            in normalized
        ):
            raise RuntimeError(
                "SIMULATED_OBLIGATION_AUDIT_FAILURE"
            )

        if (
            "FROM espacios"
            in normalized
            and "WHERE id=%s"
            in normalized
        ):
            self.current = {
                "id": 4,
                "condominio_id": 2,
                "estructura_id": 1,
                "clave": "4A",
                "activo": True,
            }
            return

        if (
            "INSERT INTO financial_obligations"
            in normalized
        ):
            self.current = {
                "id": 101,
                "condominio_id": 2,
                "estructura_id": 1,
                "espacio_id": 4,
                "periodo": "2026-11",
                "fecha_generacion": date(
                    2026,
                    11,
                    1,
                ),
                "fecha_vencimiento": date(
                    2026,
                    11,
                    30,
                ),
                "tipo_codigo":
                    "MANTENIMIENTO_ORDINARIO",
                "concepto":
                    "Cuota ordinaria noviembre",
                "monto_original_mxn":
                    Decimal("500.00"),
                "estado_codigo": "REGISTRADA",
                "rule_version_id": None,
                "space_fee_history_id": None,
            }
            return

        if (
            "FROM financial_obligations"
            in normalized
            and "FOR UPDATE"
            in normalized
        ):
            self.current = {
                "id": 101,
                "condominio_id": 2,
                "estructura_id": 1,
                "espacio_id": 4,
                "periodo": "2026-11",
                "monto_original_mxn":
                    Decimal("500.00"),
                "estado_codigo": "REGISTRADA",
            }
            return

        if (
            "UPDATE financial_obligations"
            in normalized
            and
            "estado_codigo='CANCELADA'"
            in normalized
        ):
            self.current = {
                "id": 101,
                "condominio_id": 2,
                "estructura_id": 1,
                "espacio_id": 4,
                "periodo": "2026-11",
                "monto_original_mxn":
                    Decimal("500.00"),
                "estado_codigo": "CANCELADA",
                "motivo_cancelacion":
                    "Cancelación controlada",
            }
            return

        if (
            "FROM pagos"
            in normalized
            and "FOR UPDATE"
            in normalized
        ):
            self.current = {
                "id": 201,
                "condominio_id": 2,
                "espacio_id": 4,
                "monto_mxn":
                    Decimal("400.00"),
                "estado_codigo": "REGISTRADO",
                "activo": True,
            }
            return

        if (
            "INSERT INTO payment_allocations"
            in normalized
        ):
            self.current = {
                "id": 301,
                "condominio_id": 2,
                "pago_id": 201,
                "obligation_id": 101,
                "monto_aplicado_mxn":
                    Decimal("400.00"),
                "financial_rule_exception_id":
                    None,
                "estado_codigo": "ACTIVA",
            }
            return

        if (
            "FROM payment_allocations"
            in normalized
            and "FOR UPDATE"
            in normalized
        ):
            self.current = {
                "id": 301,
                "condominio_id": 2,
                "pago_id": 201,
                "obligation_id": 101,
                "monto_aplicado_mxn":
                    Decimal("400.00"),
                "estado_codigo": "ACTIVA",
            }
            return

        if (
            "UPDATE payment_allocations"
            in normalized
            and
            "estado_codigo='REVERSADA'"
            in normalized
        ):
            self.current = {
                "id": 301,
                "condominio_id": 2,
                "pago_id": 201,
                "obligation_id": 101,
                "monto_aplicado_mxn":
                    Decimal("400.00"),
                "estado_codigo": "REVERSADA",
                "motivo_reversion":
                    "Reverso controlado",
            }
            return

        if (
            "INSERT INTO auditoria_financiera"
            in normalized
        ):
            self.current = {
                "id": 999,
            }
            return

        raise AssertionError(
            f"SQL_NO_ESPERADO: {normalized}"
        )

    def fetchone(self):
        return self.current


class FakeConnection:
    def __init__(self, fail_audit=False):
        self.fake_cursor = FakeCursor(
            fail_audit=fail_audit
        )

        self.commits = 0
        self.rollbacks = 0

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        return False

    def cursor(self):
        return self.fake_cursor

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class FakePool:
    def __init__(self, connection):
        self.connection_instance = (
            connection
        )

    def connection(self):
        return self.connection_instance


ACTOR = {
    "id": 2,
    "username": "obligation-test",
    "nombre": "Obligation Test",
    "activo": True,
}


def prepare(
    monkeypatch,
    *,
    fail_audit=False,
):
    connection = FakeConnection(
        fail_audit=fail_audit
    )

    monkeypatch.setattr(
        obligations,
        "pool",
        lambda: FakePool(connection),
    )

    monkeypatch.setattr(
        obligations,
        "_require_actor",
        lambda actor_id,
        permission,
        property_id: ACTOR,
    )

    monkeypatch.setattr(
        obligations,
        "new_trace_id",
        lambda:
            "obligation-atomic-trace",
    )

    return connection


def assert_atomic_success(connection):
    assert connection.commits == 1
    assert connection.rollbacks == 0

    assert any(
        "INSERT INTO auditoria_financiera"
        in sql
        for sql, _ in
        connection.fake_cursor.statements
    )


def assert_atomic_failure(connection):
    assert connection.commits == 0
    assert connection.rollbacks == 1

    assert any(
        "INSERT INTO auditoria_financiera"
        in sql
        for sql, _ in
        connection.fake_cursor.statements
    )


def test_obligation_and_audit_commit_together(
    monkeypatch,
):
    connection = prepare(monkeypatch)

    result = (
        obligations.create_financial_obligation(
            property_id=2,
            space_id=4,
            period="2026-11",
            obligation_type=(
                "MANTENIMIENTO_ORDINARIO"
            ),
            concept=(
                "Cuota ordinaria noviembre"
            ),
            amount=500,
            generation_date=date(
                2026,
                11,
                1,
            ),
            due_date=date(
                2026,
                11,
                30,
            ),
            actor_id=2,
        )
    )

    assert result["id"] == 101
    assert result["audit_event_id"] == 999
    assert (
        result["trace_id"]
        == "obligation-atomic-trace"
    )

    assert_atomic_success(connection)


def test_obligation_rolls_back_if_audit_fails(
    monkeypatch,
):
    connection = prepare(
        monkeypatch,
        fail_audit=True,
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "SIMULATED_OBLIGATION_AUDIT_FAILURE"
        ),
    ):
        obligations.create_financial_obligation(
            property_id=2,
            space_id=4,
            period="2026-11",
            obligation_type=(
                "MANTENIMIENTO_ORDINARIO"
            ),
            concept=(
                "Cuota ordinaria noviembre"
            ),
            amount=500,
            generation_date=date(
                2026,
                11,
                1,
            ),
            actor_id=2,
        )

    assert_atomic_failure(connection)


def test_cancellation_and_audit_commit_together(
    monkeypatch,
):
    connection = prepare(monkeypatch)

    result = (
        obligations.cancel_financial_obligation(
            property_id=2,
            obligation_id=101,
            actor_id=2,
            cancellation_reason=(
                "Cancelación controlada"
            ),
        )
    )

    assert (
        result["estado_codigo"]
        == "CANCELADA"
    )
    assert result["audit_event_id"] == 999

    assert_atomic_success(connection)


def test_cancellation_rolls_back_if_audit_fails(
    monkeypatch,
):
    connection = prepare(
        monkeypatch,
        fail_audit=True,
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "SIMULATED_OBLIGATION_AUDIT_FAILURE"
        ),
    ):
        obligations.cancel_financial_obligation(
            property_id=2,
            obligation_id=101,
            actor_id=2,
            cancellation_reason=(
                "Cancelación controlada"
            ),
        )

    assert_atomic_failure(connection)


def test_allocation_and_audit_commit_together(
    monkeypatch,
):
    connection = prepare(monkeypatch)

    result = (
        obligations.apply_payment_to_obligation(
            property_id=2,
            payment_id=201,
            obligation_id=101,
            amount=400,
            actor_id=2,
        )
    )

    assert result["id"] == 301
    assert (
        result["estado_codigo"]
        == "ACTIVA"
    )
    assert result["audit_event_id"] == 999

    assert_atomic_success(connection)


def test_allocation_rolls_back_if_audit_fails(
    monkeypatch,
):
    connection = prepare(
        monkeypatch,
        fail_audit=True,
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "SIMULATED_OBLIGATION_AUDIT_FAILURE"
        ),
    ):
        obligations.apply_payment_to_obligation(
            property_id=2,
            payment_id=201,
            obligation_id=101,
            amount=400,
            actor_id=2,
        )

    assert_atomic_failure(connection)


def test_reversal_and_audit_commit_together(
    monkeypatch,
):
    connection = prepare(monkeypatch)

    result = (
        obligations.reverse_payment_allocation(
            property_id=2,
            allocation_id=301,
            actor_id=2,
            reversal_reason=(
                "Reverso controlado"
            ),
        )
    )

    assert (
        result["estado_codigo"]
        == "REVERSADA"
    )
    assert result["audit_event_id"] == 999

    assert_atomic_success(connection)


def test_reversal_rolls_back_if_audit_fails(
    monkeypatch,
):
    connection = prepare(
        monkeypatch,
        fail_audit=True,
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "SIMULATED_OBLIGATION_AUDIT_FAILURE"
        ),
    ):
        obligations.reverse_payment_allocation(
            property_id=2,
            allocation_id=301,
            actor_id=2,
            reversal_reason=(
                "Reverso controlado"
            ),
        )

    assert_atomic_failure(connection)
