from datetime import date

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
        self.statements.append((normalized, params))

        if (
            self.fail_audit
            and "INSERT INTO auditoria_financiera"
            in normalized
        ):
            raise RuntimeError(
                "SIMULATED_GOVERNANCE_AUDIT_FAILURE"
            )

        if (
            "INSERT INTO financial_objectives"
            in normalized
        ):
            self.current = {
                "id": 101,
                "condominio_id": 1,
                "estructura_id": None,
                "codigo": "TEST_OBJECTIVE",
                "nombre": "Objetivo Test",
                "estado_codigo": "BORRADOR",
            }
            return

        if (
            "INSERT INTO financial_policies"
            in normalized
        ):
            self.current = {
                "id": 201,
                "condominio_id": 1,
                "estructura_id": None,
                "objective_id": None,
                "codigo": "TEST_POLICY",
                "nombre": "Política Test",
                "estado_codigo": "BORRADOR",
            }
            return

        if (
            "INSERT INTO auditoria_financiera"
            in normalized
        ):
            self.current = {"id": 999}
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
    "username": "governance-test",
    "nombre": "Governance Test",
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
        lambda actor_id, permission, property_id: ACTOR,
    )

    monkeypatch.setattr(
        commands,
        "new_trace_id",
        lambda: "governance-atomic-trace",
    )

    return connection


def assert_success(connection):
    statements = [
        sql
        for sql, _ in connection.fake_cursor.statements
    ]

    assert connection.commits == 1
    assert connection.rollbacks == 0

    assert any(
        "INSERT INTO auditoria_financiera"
        in sql
        for sql in statements
    )


def assert_failure(connection):
    statements = [
        sql
        for sql, _ in connection.fake_cursor.statements
    ]

    assert connection.commits == 0
    assert connection.rollbacks == 1

    assert any(
        "INSERT INTO auditoria_financiera"
        in sql
        for sql in statements
    )


def test_objective_and_audit_commit_together(
    monkeypatch,
):
    connection = prepare(monkeypatch)

    result = commands.create_financial_objective(
        property_id=1,
        code="TEST_OBJECTIVE",
        name="Objetivo Test",
        effective_from=date(2026, 1, 1),
        actor_id=2,
    )

    assert result["id"] == 101
    assert result["audit_event_id"] == 999
    assert (
        result["trace_id"]
        == "governance-atomic-trace"
    )

    assert_success(connection)


def test_objective_rolls_back_if_audit_fails(
    monkeypatch,
):
    connection = prepare(
        monkeypatch,
        fail_audit=True,
    )

    with pytest.raises(
        RuntimeError,
        match="SIMULATED_GOVERNANCE_AUDIT_FAILURE",
    ):
        commands.create_financial_objective(
            property_id=1,
            code="TEST_OBJECTIVE",
            name="Objetivo Test",
            effective_from=date(2026, 1, 1),
            actor_id=2,
        )

    assert_failure(connection)


def test_policy_and_audit_commit_together(
    monkeypatch,
):
    connection = prepare(monkeypatch)

    result = commands.create_financial_policy(
        property_id=1,
        code="TEST_POLICY",
        name="Política Test",
        effective_from=date(2026, 1, 1),
        actor_id=2,
    )

    assert result["id"] == 201
    assert result["audit_event_id"] == 999
    assert (
        result["trace_id"]
        == "governance-atomic-trace"
    )

    assert_success(connection)


def test_policy_rolls_back_if_audit_fails(
    monkeypatch,
):
    connection = prepare(
        monkeypatch,
        fail_audit=True,
    )

    with pytest.raises(
        RuntimeError,
        match="SIMULATED_GOVERNANCE_AUDIT_FAILURE",
    ):
        commands.create_financial_policy(
            property_id=1,
            code="TEST_POLICY",
            name="Política Test",
            effective_from=date(2026, 1, 1),
            actor_id=2,
        )

    assert_failure(connection)
