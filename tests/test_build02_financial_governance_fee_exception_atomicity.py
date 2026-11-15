from datetime import date
from decimal import Decimal

import pytest

import services.financial_governance_commands as commands


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

        self.statements.append(
            (normalized, params)
        )

        if (
            self.fail_audit
            and "INSERT INTO auditoria_financiera"
            in normalized
        ):
            raise RuntimeError(
                "SIMULATED_FEE_EXCEPTION_AUDIT_FAILURE"
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
                "nombre": "Espacio Test",
                "activo": True,
            }
            return

        if (
            "INSERT INTO space_fee_history"
            in normalized
        ):
            self.current = {
                "id": 101,
                "condominio_id": 2,
                "espacio_id": 4,
                "tipo_cuota_codigo":
                    "MANTENIMIENTO_ORDINARIO",
                "monto_mxn": Decimal("500.00"),
                "vigente_desde":
                    date(2026, 11, 1),
                "vigente_hasta": None,
                "origen_codigo":
                    "CONFIGURACION",
                "rule_version_id": None,
                "estado_codigo": "BORRADOR",
            }
            return

        if (
            "FROM space_fee_history"
            in normalized
            and "FOR UPDATE"
            in normalized
        ):
            self.current = {
                "id": 101,
                "condominio_id": 2,
                "espacio_id": 4,
                "tipo_cuota_codigo":
                    "MANTENIMIENTO_ORDINARIO",
                "monto_mxn": Decimal("500.00"),
                "vigente_desde":
                    date(2026, 11, 1),
                "vigente_hasta": None,
                "rule_version_id": None,
                "estado_codigo": "BORRADOR",
            }
            return

        if (
            "UPDATE space_fee_history"
            in normalized
            and "estado_codigo='APROBADO'"
            in normalized
        ):
            self.current = {
                "id": 101,
                "condominio_id": 2,
                "espacio_id": 4,
                "tipo_cuota_codigo":
                    "MANTENIMIENTO_ORDINARIO",
                "monto_mxn": Decimal("500.00"),
                "vigente_desde":
                    date(2026, 11, 1),
                "vigente_hasta": None,
                "rule_version_id": None,
                "estado_codigo": "APROBADO",
            }
            return

        if (
            "FROM financial_rule_versions version"
            in normalized
            and "definition.admite_excepcion"
            in normalized
        ):
            self.current = {
                "id": 201,
                "estado_codigo": "APROBADO",
                "vigente_desde":
                    date(2026, 1, 1),
                "vigente_hasta": None,
                "condominio_id": 2,
                "estructura_id": 1,
                "espacio_id": None,
                "admite_excepcion": True,
            }
            return

        if (
            "INSERT INTO financial_rule_exceptions"
            in normalized
        ):
            self.current = {
                "id": 301,
                "condominio_id": 2,
                "estructura_id": 1,
                "espacio_id": 4,
                "rule_version_id": 201,
                "tipo_excepcion":
                    "PAGO_PARCIAL",
                "parametros": {
                    "monto_autorizado": 400
                },
                "motivo":
                    "Prueba controlada",
                "estado_codigo": "PENDIENTE",
                "vigente_desde":
                    date(2026, 11, 1),
                "vigente_hasta":
                    date(2026, 11, 30),
            }
            return

        if (
            "FROM financial_rule_exceptions"
            in normalized
            and "FOR UPDATE"
            in normalized
        ):
            self.current = {
                "id": 301,
                "condominio_id": 2,
                "estructura_id": 1,
                "espacio_id": 4,
                "rule_version_id": 201,
                "tipo_excepcion":
                    "PAGO_PARCIAL",
                "estado_codigo": "PENDIENTE",
            }
            return

        if (
            "UPDATE financial_rule_exceptions"
            in normalized
        ):
            self.current = {
                "id": 301,
                "condominio_id": 2,
                "estructura_id": 1,
                "espacio_id": 4,
                "rule_version_id": 201,
                "tipo_excepcion":
                    "PAGO_PARCIAL",
                "estado_codigo": "APROBADA",
                "decision_detalle":
                    "Aprobación controlada",
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
    "username": "fee-exception-test",
    "nombre": "Fee Exception Test",
    "activo": True,
}


def prepare(
    monkeypatch,
    fail_audit=False,
):
    connection = FakeConnection(
        fail_audit=fail_audit
    )

    monkeypatch.setattr(
        commands,
        "pool",
        lambda: FakePool(connection),
    )

    monkeypatch.setattr(
        commands,
        "_require_actor",
        lambda actor_id, permission, property_id:
            ACTOR,
    )

    monkeypatch.setattr(
        commands,
        "new_trace_id",
        lambda:
            "fee-exception-atomic-trace",
    )

    return connection


def assert_success(connection):
    assert connection.commits == 1
    assert connection.rollbacks == 0

    assert any(
        "INSERT INTO auditoria_financiera"
        in sql
        for sql, _ in
        connection.fake_cursor.statements
    )


def assert_failure(connection):
    assert connection.commits == 0
    assert connection.rollbacks == 1

    assert any(
        "INSERT INTO auditoria_financiera"
        in sql
        for sql, _ in
        connection.fake_cursor.statements
    )


def test_fee_and_audit_commit_together(
    monkeypatch,
):
    connection = prepare(monkeypatch)

    result = commands.create_space_fee_version(
        property_id=2,
        space_id=4,
        fee_type="MANTENIMIENTO_ORDINARIO",
        amount=500,
        effective_from=date(2026, 11, 1),
        actor_id=2,
    )

    assert result["id"] == 101
    assert result["audit_event_id"] == 999
    assert (
        result["trace_id"]
        == "fee-exception-atomic-trace"
    )

    assert_success(connection)


def test_fee_rolls_back_if_audit_fails(
    monkeypatch,
):
    connection = prepare(
        monkeypatch,
        fail_audit=True,
    )

    with pytest.raises(
        RuntimeError,
        match="SIMULATED_FEE_EXCEPTION_AUDIT_FAILURE",
    ):
        commands.create_space_fee_version(
            property_id=2,
            space_id=4,
            fee_type="MANTENIMIENTO_ORDINARIO",
            amount=500,
            effective_from=date(2026, 11, 1),
            actor_id=2,
        )

    assert_failure(connection)


def test_fee_approval_and_audit_commit_together(
    monkeypatch,
):
    connection = prepare(monkeypatch)

    result = commands.approve_space_fee_version(
        property_id=2,
        fee_version_id=101,
        actor_id=2,
        approval_reason=(
            "Cuota aprobada para prueba"
        ),
    )

    assert result["estado_codigo"] == "APROBADO"
    assert result["audit_event_id"] == 999

    assert_success(connection)


def test_fee_approval_rolls_back_if_audit_fails(
    monkeypatch,
):
    connection = prepare(
        monkeypatch,
        fail_audit=True,
    )

    with pytest.raises(
        RuntimeError,
        match="SIMULATED_FEE_EXCEPTION_AUDIT_FAILURE",
    ):
        commands.approve_space_fee_version(
            property_id=2,
            fee_version_id=101,
            actor_id=2,
            approval_reason=(
                "Cuota aprobada para prueba"
            ),
        )

    assert_failure(connection)


def test_exception_and_audit_commit_together(
    monkeypatch,
):
    connection = prepare(monkeypatch)

    result = commands.request_financial_exception(
        property_id=2,
        structure_id=1,
        space_id=4,
        rule_version_id=201,
        exception_type="PAGO_PARCIAL",
        parameters={
            "monto_autorizado": 400
        },
        reason="Prueba controlada",
        effective_from=date(2026, 11, 1),
        effective_to=date(2026, 11, 30),
        actor_id=2,
    )

    assert result["id"] == 301
    assert (
        result["estado_codigo"]
        == "PENDIENTE"
    )
    assert result["audit_event_id"] == 999

    assert_success(connection)


def test_exception_rolls_back_if_audit_fails(
    monkeypatch,
):
    connection = prepare(
        monkeypatch,
        fail_audit=True,
    )

    with pytest.raises(
        RuntimeError,
        match="SIMULATED_FEE_EXCEPTION_AUDIT_FAILURE",
    ):
        commands.request_financial_exception(
            property_id=2,
            structure_id=1,
            space_id=4,
            rule_version_id=201,
            exception_type="PAGO_PARCIAL",
            parameters={
                "monto_autorizado": 400
            },
            reason="Prueba controlada",
            effective_from=date(2026, 11, 1),
            effective_to=date(2026, 11, 30),
            actor_id=2,
        )

    assert_failure(connection)


def test_exception_resolution_and_audit_commit_together(
    monkeypatch,
):
    connection = prepare(monkeypatch)

    result = commands.resolve_financial_exception(
        property_id=2,
        exception_id=301,
        decision="APROBADA",
        decision_detail=(
            "Aprobación controlada"
        ),
        actor_id=2,
    )

    assert (
        result["estado_codigo"]
        == "APROBADA"
    )
    assert result["audit_event_id"] == 999

    assert_success(connection)


def test_exception_resolution_rolls_back_if_audit_fails(
    monkeypatch,
):
    connection = prepare(
        monkeypatch,
        fail_audit=True,
    )

    with pytest.raises(
        RuntimeError,
        match="SIMULATED_FEE_EXCEPTION_AUDIT_FAILURE",
    ):
        commands.resolve_financial_exception(
            property_id=2,
            exception_id=301,
            decision="APROBADA",
            decision_detail=(
                "Aprobación controlada"
            ),
            actor_id=2,
        )

    assert_failure(connection)
