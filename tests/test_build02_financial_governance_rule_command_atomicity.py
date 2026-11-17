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
        self.statements.append(
            (normalized, params)
        )

        if (
            self.fail_audit
            and "INSERT INTO auditoria_financiera"
            in normalized
        ):
            raise RuntimeError(
                "SIMULATED_RULE_AUDIT_FAILURE"
            )

        if (
            "SELECT id, codigo, activo"
            in normalized
            and "FROM financial_rule_definitions"
            in normalized
        ):
            self.current = {
                "id": 10,
                "codigo": "TEST_RULE",
                "activo": True,
            }
            return

        if (
            "SELECT codigo, esquema_parametros"
            in normalized
            and "FROM financial_rule_definitions"
            in normalized
        ):
            self.current = {
                "codigo": "TEST_RULE",
                "esquema_parametros": {
                    "policy": {
                        "type": "string",
                    }
                },
            }
            return

        if (
            "INSERT INTO financial_rules"
            in normalized
        ):
            self.current = {
                "id": 101,
                "rule_definition_id": 10,
                "policy_id": None,
                "scope_level": "INMUEBLE",
                "condominio_id": 1,
                "estructura_id": None,
                "espacio_id": None,
                "codigo": "TEST_RULE",
                "nombre": "Regla Test",
                "hereda": True,
                "es_override": True,
                "prioridad": 100,
                "activo": True,
            }
            return

        if (
            "FROM financial_rules"
            in normalized
            and "condominio_id"
            in normalized
            and "activo=TRUE"
            in normalized
        ):
            self.current = {
                "id": 101,
                "codigo": "TEST_RULE",
                "condominio_id": 1,
                "rule_definition_id": 10,
                "activo": True,
            }
            return

        if (
            "INSERT INTO financial_rule_versions"
            in normalized
        ):
            self.current = {
                "id": 201,
                "rule_id": 101,
                "version_num": 1,
                "vigente_desde": date(2026, 1, 1),
                "vigente_hasta": None,
                "estado_codigo": "BORRADOR",
                "parametros": {
                    "policy": "TEST"
                },
            }
            return

        if (
            "FROM financial_rule_versions version"
            in normalized
            and "FOR UPDATE"
            in normalized
        ):
            self.current = {
                "id": 201,
                "rule_id": 101,
                "version_num": 1,
                "vigente_desde": date(2026, 1, 1),
                "vigente_hasta": None,
                "estado_codigo": "BORRADOR",
                "parametros": {
                    "policy": "TEST"
                },
                "condominio_id": 1,
                "rule_code": "TEST_RULE",
            }
            return

        if (
            "FROM financial_rule_dependencies"
            in normalized
        ):
            self.current = []
            return

        if (
            "UPDATE financial_rule_versions"
            in normalized
            and "estado_codigo='APROBADO'"
            in normalized
        ):
            self.current = {
                "id": 201,
                "rule_id": 101,
                "version_num": 1,
                "vigente_desde": date(2026, 1, 1),
                "vigente_hasta": None,
                "estado_codigo": "APROBADO",
                "parametros": {
                    "policy": "TEST"
                },
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

    def fetchall(self):
        if self.current is None:
            return []

        if isinstance(
            self.current,
            list,
        ):
            return self.current

        return [self.current]


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
    "username": "rule-command-test",
    "nombre": "Rule Command Test",
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
        lambda: "rule-command-atomic-trace",
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


def test_rule_and_audit_commit_together(
    monkeypatch,
):
    connection = prepare(
        monkeypatch
    )

    result = commands.create_financial_rule(
        property_id=1,
        definition_id=10,
        scope_level="INMUEBLE",
        code="TEST_RULE",
        name="Regla Test",
        actor_id=2,
        is_override=True,
    )

    assert result["id"] == 101
    assert result["audit_event_id"] == 999
    assert (
        result["trace_id"]
        == "rule-command-atomic-trace"
    )

    assert_atomic_success(connection)


def test_rule_rolls_back_if_audit_fails(
    monkeypatch,
):
    connection = prepare(
        monkeypatch,
        fail_audit=True,
    )

    with pytest.raises(
        RuntimeError,
        match="SIMULATED_RULE_AUDIT_FAILURE",
    ):
        commands.create_financial_rule(
            property_id=1,
            definition_id=10,
            scope_level="INMUEBLE",
            code="TEST_RULE",
            name="Regla Test",
            actor_id=2,
            is_override=True,
        )

    assert_atomic_failure(connection)


def test_version_and_audit_commit_together(
    monkeypatch,
):
    connection = prepare(
        monkeypatch
    )

    result = commands.create_rule_version(
        property_id=1,
        rule_id=101,
        version_num=1,
        effective_from=date(2026, 1, 1),
        parameters={
            "policy": "TEST"
        },
        actor_id=2,
    )

    assert result["id"] == 201
    assert result["audit_event_id"] == 999
    assert (
        result["trace_id"]
        == "rule-command-atomic-trace"
    )

    assert_atomic_success(connection)


def test_version_rolls_back_if_audit_fails(
    monkeypatch,
):
    connection = prepare(
        monkeypatch,
        fail_audit=True,
    )

    with pytest.raises(
        RuntimeError,
        match="SIMULATED_RULE_AUDIT_FAILURE",
    ):
        commands.create_rule_version(
            property_id=1,
            rule_id=101,
            version_num=1,
            effective_from=date(2026, 1, 1),
            parameters={
                "policy": "TEST"
            },
            actor_id=2,
        )

    assert_atomic_failure(connection)


def test_version_approval_and_audit_commit_together(
    monkeypatch,
):
    connection = prepare(
        monkeypatch
    )

    result = commands.approve_rule_version(
        property_id=1,
        version_id=201,
        actor_id=2,
        approval_reason=(
            "Aprobación controlada"
        ),
    )

    assert result["id"] == 201
    assert (
        result["estado_codigo"]
        == "APROBADO"
    )
    assert result["audit_event_id"] == 999

    assert_atomic_success(connection)


def test_version_approval_rolls_back_if_audit_fails(
    monkeypatch,
):
    connection = prepare(
        monkeypatch,
        fail_audit=True,
    )

    with pytest.raises(
        RuntimeError,
        match="SIMULATED_RULE_AUDIT_FAILURE",
    ):
        commands.approve_rule_version(
            property_id=1,
            version_id=201,
            actor_id=2,
            approval_reason=(
                "Aprobación controlada"
            ),
        )

    assert_atomic_failure(connection)
