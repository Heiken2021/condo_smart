from pathlib import Path


MIGRATION = Path(
    "database/migrations/019_financial_foundation_build02.sql"
).read_text(encoding="utf-8")


def test_financial_catalogs_are_defined():
    for token in [
        "ESTADO_MOVIMIENTO_FINANCIERO",
        "TIPO_CARGO",
        "CATEGORIA_GASTO",
        "REGISTRADO",
        "CANCELADO",
    ]:
        assert token in MIGRATION


def test_financial_permissions_are_scoped():
    for token in [
        "FINANZAS_CONSULTAR",
        "FINANZAS_CARGO_CREAR",
        "FINANZAS_PAGO_REGISTRAR",
        "FINANZAS_GASTO_REGISTRAR",
        "FINANZAS_MOVIMIENTO_CANCELAR",
        "FINANZAS_ESTADO_CUENTA",
    ]:
        assert token in MIGRATION


def test_financial_roles_are_conservative():
    assert "ADMINISTRADOR" in MIGRATION
    assert "CONTABILIDAD" in MIGRATION
    assert "GERENTE" in MIGRATION
    assert "COMITE" in MIGRATION


def test_financial_movements_have_state_and_attribution():
    for token in [
        "estado_codigo",
        "creado_en",
        "creado_por",
        "cancelado_en",
        "cancelado_por",
        "motivo_cancelacion",
        "referencia",
        "observaciones",
    ]:
        assert token in MIGRATION


def test_financial_amounts_must_be_positive():
    assert "ck_cargos_monto_positivo" in MIGRATION
    assert "ck_pagos_monto_positivo" in MIGRATION
    assert "ck_gastos_monto_positivo" in MIGRATION
    assert "CHECK (monto_mxn > 0)" in MIGRATION


def test_financial_period_format_is_controlled():
    assert "ck_cargos_periodo" in MIGRATION
    assert "ck_pagos_periodo" in MIGRATION
    assert "^[0-9]{4}-(0[1-9]|1[0-2])$" in MIGRATION


def test_space_and_property_must_match():
    assert "validate_financial_space_scope" in MIGRATION
    assert "FINANCIAL_SPACE_PROPERTY_MISMATCH" in MIGRATION
    assert "trg_cargos_validate_space_scope" in MIGRATION
    assert "trg_pagos_validate_space_scope" in MIGRATION


def test_cancellation_requires_attribution():
    assert "validate_cargo_cancellation" in MIGRATION
    assert "validate_pago_cancellation" in MIGRATION
    assert "validate_gasto_cancellation" in MIGRATION
    assert "FINANCIAL_CANCELLATION_METADATA_REQUIRED" in MIGRATION
    assert "FINANCIAL_MOVEMENT_ALREADY_CANCELLED" in MIGRATION
    assert "NEW.activo=FALSE" in MIGRATION


def test_foundation_does_not_delete_financial_data():
    assert "DELETE FROM cargos" not in MIGRATION
    assert "DELETE FROM pagos" not in MIGRATION
    assert "DELETE FROM gastos" not in MIGRATION


def test_financial_indexes_are_added():
    for token in [
        "idx_cargos_condominio_espacio_periodo",
        "idx_pagos_condominio_espacio_periodo",
        "idx_pagos_condominio_fecha",
        "idx_gastos_condominio_fecha",
        "idx_gastos_condominio_categoria",
    ]:
        assert token in MIGRATION



def test_registered_financial_movements_are_immutable():
    assert "FINANCIAL_MOVEMENT_IS_IMMUTABLE" in MIGRATION
    assert "FINANCIAL_ORIGINAL_DATA_IS_IMMUTABLE" in MIGRATION


def test_cancellation_preserves_original_economic_data():
    for token in [
        "NEW.monto_mxn IS DISTINCT FROM OLD.monto_mxn",
        "NEW.condominio_id IS DISTINCT FROM OLD.condominio_id",
        "NEW.creado_en IS DISTINCT FROM OLD.creado_en",
        "NEW.creado_por IS DISTINCT FROM OLD.creado_por",
    ]:
        assert token in MIGRATION


def test_each_financial_entity_has_its_own_cancellation_guard():
    for token in [
        "validate_cargo_cancellation",
        "validate_pago_cancellation",
        "validate_gasto_cancellation",
    ]:
        assert token in MIGRATION
