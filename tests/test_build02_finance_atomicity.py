from datetime import date
from decimal import Decimal

import pytest

import services.finance as finance


class FakeCursor:
    def __init__(self, fail_audit=False):
        self.fail_audit = fail_audit
        self.current = None
        self.statements = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=()):
        normalized = " ".join(sql.split())
        self.statements.append((normalized, params))

        if (
            self.fail_audit
            and "INSERT INTO auditoria_financiera" in normalized
        ):
            raise RuntimeError("SIMULATED_AUDIT_FAILURE")

        if "INSERT INTO cargos" in normalized:
            self.current = {
                "id": 101,
                "condominio_id": 1,
                "espacio_id": 10,
                "periodo": "2026-11",
                "tipo_codigo": "CUOTA_MANTENIMIENTO",
                "concepto": "Cuota noviembre",
                "monto_mxn": Decimal("1000.00"),
                "estado_codigo": "REGISTRADO",
                "referencia": "CARGO-TEST",
                "observaciones": None,
                "creado_por": 2,
                "activo": True,
            }
            return

        if "INSERT INTO pagos" in normalized:
            self.current = {
                "id": 201,
                "condominio_id": 1,
                "espacio_id": 10,
                "periodo": "2026-11",
                "fecha": date(2026, 11, 14),
                "monto_mxn": Decimal("750.00"),
                "estado_codigo": "REGISTRADO",
                "referencia": "PAGO-TEST",
                "observaciones": None,
                "creado_por": 2,
                "activo": True,
            }
            return

        if "INSERT INTO gastos" in normalized:
            self.current = {
                "id": 301,
                "condominio_id": 1,
                "fecha": date(2026, 11, 14),
                "categoria_codigo": "MANTENIMIENTO",
                "concepto": "Mantenimiento preventivo",
                "monto_mxn": Decimal("500.00"),
                "estado_codigo": "REGISTRADO",
                "referencia": "GASTO-TEST",
                "observaciones": None,
                "creado_por": 2,
                "activo": True,
            }
            return

        if "INSERT INTO auditoria_financiera" in normalized:
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

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self):
        return self.fake_cursor

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class FakePool:
    def __init__(self, connection):
        self.connection_instance = connection

    def connection(self):
        return self.connection_instance


ACTOR = {
    "id": 2,
    "username": "atomic-test",
    "nombre": "Atomic Test",
    "activo": True,
    "rol_global": "USUARIO",
}

SPACE = {
    "id": 10,
    "condominio_id": 1,
    "clave": "TEST-10",
    "nombre": "Espacio Test",
    "activo": True,
}


def prepare(monkeypatch, fail_audit=False):
    connection = FakeConnection(
        fail_audit=fail_audit
    )

    monkeypatch.setattr(
        finance,
        "pool",
        lambda: FakePool(connection),
    )

    monkeypatch.setattr(
        finance,
        "_require_actor",
        lambda actor_id, permission, property_id: ACTOR,
    )

    monkeypatch.setattr(
        finance,
        "_validate_space",
        lambda property_id, space_id: SPACE,
    )

    monkeypatch.setattr(
        finance,
        "new_trace_id",
        lambda: "atomic-trace-id",
    )

    return connection


def assert_atomic_success(connection):
    statements = [
        sql
        for sql, _ in connection.fake_cursor.statements
    ]

    assert connection.commits == 1
    assert connection.rollbacks == 0

    assert any(
        "INSERT INTO auditoria_financiera" in sql
        for sql in statements
    )


def assert_atomic_failure(connection):
    statements = [
        sql
        for sql, _ in connection.fake_cursor.statements
    ]

    assert connection.commits == 0
    assert connection.rollbacks == 1

    assert any(
        "INSERT INTO auditoria_financiera" in sql
        for sql in statements
    )


def test_create_charge_commits_movement_and_audit_together(
    monkeypatch,
):
    connection = prepare(monkeypatch)

    result = finance.create_charge(
        property_id=1,
        space_id=10,
        period="2026-11",
        charge_type="CUOTA_MANTENIMIENTO",
        concept="Cuota noviembre",
        amount=1000,
        actor_id=2,
        reference="CARGO-TEST",
    )

    assert result["id"] == 101
    assert result["audit_event_id"] == 999
    assert result["trace_id"] == "atomic-trace-id"

    assert_atomic_success(connection)


def test_create_charge_rolls_back_if_audit_fails(
    monkeypatch,
):
    connection = prepare(
        monkeypatch,
        fail_audit=True,
    )

    with pytest.raises(
        RuntimeError,
        match="SIMULATED_AUDIT_FAILURE",
    ):
        finance.create_charge(
            property_id=1,
            space_id=10,
            period="2026-11",
            charge_type="CUOTA_MANTENIMIENTO",
            concept="Cuota noviembre",
            amount=1000,
            actor_id=2,
            reference="CARGO-TEST",
        )

    assert_atomic_failure(connection)


def test_register_payment_commits_movement_and_audit_together(
    monkeypatch,
):
    connection = prepare(monkeypatch)

    result = finance.register_payment(
        property_id=1,
        space_id=10,
        period="2026-11",
        payment_date=date(2026, 11, 14),
        amount=750,
        actor_id=2,
        reference="PAGO-TEST",
    )

    assert result["id"] == 201
    assert result["audit_event_id"] == 999
    assert result["trace_id"] == "atomic-trace-id"

    assert_atomic_success(connection)


def test_register_payment_rolls_back_if_audit_fails(
    monkeypatch,
):
    connection = prepare(
        monkeypatch,
        fail_audit=True,
    )

    with pytest.raises(
        RuntimeError,
        match="SIMULATED_AUDIT_FAILURE",
    ):
        finance.register_payment(
            property_id=1,
            space_id=10,
            period="2026-11",
            payment_date=date(2026, 11, 14),
            amount=750,
            actor_id=2,
            reference="PAGO-TEST",
        )

    assert_atomic_failure(connection)


def test_register_expense_commits_movement_and_audit_together(
    monkeypatch,
):
    connection = prepare(monkeypatch)

    result = finance.register_expense(
        property_id=1,
        expense_date=date(2026, 11, 14),
        category="MANTENIMIENTO",
        concept="Mantenimiento preventivo",
        amount=500,
        actor_id=2,
        reference="GASTO-TEST",
    )

    assert result["id"] == 301
    assert result["audit_event_id"] == 999
    assert result["trace_id"] == "atomic-trace-id"

    assert_atomic_success(connection)


def test_register_expense_rolls_back_if_audit_fails(
    monkeypatch,
):
    connection = prepare(
        monkeypatch,
        fail_audit=True,
    )

    with pytest.raises(
        RuntimeError,
        match="SIMULATED_AUDIT_FAILURE",
    ):
        finance.register_expense(
            property_id=1,
            expense_date=date(2026, 11, 14),
            category="MANTENIMIENTO",
            concept="Mantenimiento preventivo",
            amount=500,
            actor_id=2,
            reference="GASTO-TEST",
        )

    assert_atomic_failure(connection)
