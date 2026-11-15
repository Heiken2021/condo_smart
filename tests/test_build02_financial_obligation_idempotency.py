from pathlib import Path


MIGRATION = Path(
    "database/migrations/"
    "022_financial_obligation_idempotency_build02.sql"
).read_text(encoding="utf-8")


def test_022_creates_active_obligation_unique_index():
    assert (
        "CREATE UNIQUE INDEX IF NOT EXISTS"
        in MIGRATION
    )
    assert (
        "uq_financial_obligation_active_period_type"
        in MIGRATION
    )


def test_unique_index_uses_business_identity():
    for token in [
        "condominio_id",
        "espacio_id",
        "periodo",
        "tipo_codigo",
    ]:
        assert token in MIGRATION


def test_unique_index_only_blocks_active_obligations():
    assert (
        "WHERE estado_codigo='REGISTRADA'"
        in MIGRATION
    )


def test_cancelled_obligation_is_not_in_unique_scope():
    index_section = MIGRATION.split(
        "uq_financial_obligation_active_period_type",
        1,
    )[1].split(";", 1)[0]

    assert "'CANCELADA'" not in index_section


def test_022_exposes_idempotency_query():
    assert (
        "financial_active_obligation_exists"
        in MIGRATION
    )
    assert "RETURNS BOOLEAN" in MIGRATION
    assert "SELECT EXISTS(" in MIGRATION


def test_idempotency_query_uses_same_identity():
    function_section = MIGRATION.split(
        "financial_active_obligation_exists",
        1,
    )[1]

    for token in [
        "obligation.condominio_id",
        "obligation.espacio_id",
        "obligation.periodo",
        "obligation.tipo_codigo",
        "obligation.estado_codigo",
    ]:
        assert token in function_section


def test_022_does_not_modify_021():
    assert (
        "021_financial_obligations_build02.sql"
        not in MIGRATION
    )


def test_022_does_not_modify_legacy_movements():
    forbidden = [
        "ALTER TABLE cargos",
        "ALTER TABLE pagos",
        "UPDATE cargos",
        "UPDATE pagos",
        "DELETE FROM cargos",
        "DELETE FROM pagos",
        "INSERT INTO cargos",
        "INSERT INTO pagos",
    ]

    for token in forbidden:
        assert token not in MIGRATION


def test_022_does_not_create_real_obligations():
    assert (
        "INSERT INTO financial_obligations"
        not in MIGRATION
    )


def test_022_is_transactional():
    normalized = MIGRATION.strip()

    assert normalized.startswith("BEGIN;")
    assert normalized.endswith("COMMIT;")
