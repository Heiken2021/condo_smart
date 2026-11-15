from pathlib import Path


MIGRATION = Path(
    "database/migrations/"
    "021_financial_obligations_build02.sql"
).read_text(encoding="utf-8")


def test_021_creates_obligations():
    assert (
        "CREATE TABLE IF NOT EXISTS "
        "financial_obligations"
    ) in " ".join(MIGRATION.split())


def test_021_creates_payment_allocations():
    assert (
        "CREATE TABLE IF NOT EXISTS "
        "payment_allocations"
    ) in " ".join(MIGRATION.split())


def test_obligation_preserves_governance_provenance():
    for token in [
        "rule_version_id",
        "space_fee_history_id",
        "estructura_id",
        "periodo",
        "fecha_vencimiento",
    ]:
        assert token in MIGRATION


def test_obligation_amount_is_positive():
    assert "monto_original_mxn > 0" in MIGRATION


def test_obligation_has_only_operational_states():
    assert "'REGISTRADA'" in MIGRATION
    assert "'CANCELADA'" in MIGRATION


def test_balance_is_derived_not_stored():
    assert (
        "CREATE OR REPLACE VIEW "
        "financial_obligation_balances"
    ) in " ".join(MIGRATION.split())

    assert "AS saldo_mxn" in MIGRATION


def test_balance_has_derived_business_situation():
    for token in [
        "'PENDIENTE'",
        "'PARCIAL'",
        "'LIQUIDADA'",
    ]:
        assert token in MIGRATION


def test_reversed_allocations_do_not_reduce_balance():
    assert (
        "allocation.estado_codigo='ACTIVA'"
        in MIGRATION
    )


def test_obligation_scope_is_validated():
    assert (
        "validate_financial_obligation_scope"
        in MIGRATION
    )

    for token in [
        "FINANCIAL_OBLIGATION_SPACE_SCOPE_MISMATCH",
        "FINANCIAL_OBLIGATION_STRUCTURE_SCOPE_MISMATCH",
        "FINANCIAL_OBLIGATION_FEE_SCOPE_MISMATCH",
        "FINANCIAL_OBLIGATION_RULE_SCOPE_MISMATCH",
    ]:
        assert token in MIGRATION


def test_obligation_requires_approved_fee_when_provided():
    assert (
        "FINANCIAL_OBLIGATION_REQUIRES_APPROVED_FEE"
        in MIGRATION
    )


def test_obligation_requires_effective_approved_rule_when_provided():
    assert (
        "FINANCIAL_OBLIGATION_REQUIRES_EFFECTIVE_APPROVED_RULE"
        in MIGRATION
    )


def test_allocation_requires_existing_payment():
    assert (
        "FINANCIAL_ALLOCATION_PAYMENT_NOT_FOUND"
        in MIGRATION
    )


def test_allocation_rejects_cancelled_payment():
    assert (
        "FINANCIAL_ALLOCATION_PAYMENT_NOT_ACTIVE"
        in MIGRATION
    )


def test_allocation_requires_active_obligation():
    assert (
        "FINANCIAL_ALLOCATION_OBLIGATION_NOT_ACTIVE"
        in MIGRATION
    )


def test_allocation_enforces_same_property():
    assert (
        "FINANCIAL_ALLOCATION_PROPERTY_SCOPE_MISMATCH"
        in MIGRATION
    )


def test_allocation_enforces_same_space():
    assert (
        "FINANCIAL_ALLOCATION_SPACE_SCOPE_MISMATCH"
        in MIGRATION
    )


def test_payment_cannot_be_overallocated():
    assert (
        "FINANCIAL_PAYMENT_OVERALLOCATION"
        in MIGRATION
    )


def test_obligation_cannot_be_overallocated():
    assert (
        "FINANCIAL_OBLIGATION_OVERALLOCATION"
        in MIGRATION
    )


def test_exception_must_be_approved_when_used():
    assert (
        "FINANCIAL_ALLOCATION_REQUIRES_APPROVED_EXCEPTION"
        in MIGRATION
    )


def test_exception_scope_is_validated():
    assert (
        "FINANCIAL_ALLOCATION_EXCEPTION_SCOPE_MISMATCH"
        in MIGRATION
    )
    assert (
        "FINANCIAL_ALLOCATION_EXCEPTION_SPACE_MISMATCH"
        in MIGRATION
    )


def test_allocation_supports_reversal_not_delete():
    assert "'REVERSADA'" in MIGRATION
    assert (
        "FINANCIAL_PAYMENT_ALLOCATION_DELETE_NOT_ALLOWED"
        in MIGRATION
    )


def test_reversal_requires_attribution():
    for token in [
        "reversado_por",
        "reversado_en",
        "motivo_reversion",
        "FINANCIAL_ALLOCATION_REVERSAL_METADATA_REQUIRED",
    ]:
        assert token in MIGRATION


def test_active_allocation_is_immutable():
    assert (
        "ACTIVE_PAYMENT_ALLOCATION_IS_IMMUTABLE"
        in MIGRATION
    )


def test_reversed_allocation_is_immutable():
    assert (
        "REVERSED_PAYMENT_ALLOCATION_IS_IMMUTABLE"
        in MIGRATION
    )


def test_obligation_with_allocations_cannot_be_cancelled():
    assert (
        "FINANCIAL_OBLIGATION_HAS_ACTIVE_ALLOCATIONS"
        in MIGRATION
    )


def test_obligation_cancellation_requires_attribution():
    assert (
        "FINANCIAL_OBLIGATION_CANCELLATION_METADATA_REQUIRED"
        in MIGRATION
    )


def test_obligation_history_is_immutable():
    assert (
        "FINANCIAL_OBLIGATION_HISTORY_IS_IMMUTABLE"
        in MIGRATION
    )


def test_021_is_additive():
    forbidden = [
        "ALTER TABLE cargos",
        "ALTER TABLE pagos",
        "UPDATE cargos",
        "UPDATE pagos",
        "DELETE FROM cargos",
        "DELETE FROM pagos",
        "DROP TABLE cargos",
        "DROP TABLE pagos",
    ]

    for token in forbidden:
        assert token not in MIGRATION


def test_021_does_not_migrate_existing_charge():
    assert "INSERT INTO financial_obligations SELECT" not in (
        " ".join(MIGRATION.split())
    )


def test_021_does_not_define_partial_payment_policy():
    forbidden = [
        "PAGO_PARCIAL_PERMITIDO",
        "PAGO_MINIMO",
        "CUOTA_MINIMA",
        "REQUIERE_APROBACION",
    ]

    for token in forbidden:
        assert token not in MIGRATION


def test_021_adds_governed_permissions():
    for token in [
        "FINANZAS_OBLIGACION_CREAR",
        "FINANZAS_OBLIGACION_CANCELAR",
        "FINANZAS_PAGO_APLICAR",
        "FINANZAS_PAGO_REVERTIR_APLICACION",
    ]:
        assert token in MIGRATION



def test_obligation_structure_matches_space_context():
    assert (
        "FINANCIAL_OBLIGATION_STRUCTURE_CONTEXT_MISMATCH"
        in MIGRATION
    )
    assert (
        "NEW.estructura_id"
        in MIGRATION
    )
    assert (
        "space_row.estructura_id"
        in MIGRATION
    )


def test_fee_must_be_effective_for_obligation_period():
    assert (
        "FINANCIAL_OBLIGATION_FEE_NOT_EFFECTIVE"
        in MIGRATION
    )
    assert (
        "TO_DATE(NEW.periodo || '-01'"
        in MIGRATION
    )


def test_rule_must_be_effective_for_obligation_period():
    assert (
        "FINANCIAL_OBLIGATION_REQUIRES_EFFECTIVE_APPROVED_RULE"
        in MIGRATION
    )
    assert (
        "version.vigente_desde"
        in MIGRATION
    )
    assert (
        "version.vigente_hasta"
        in MIGRATION
    )


def test_exception_must_be_effective_for_payment_date():
    assert (
        "FINANCIAL_ALLOCATION_EXCEPTION_NOT_EFFECTIVE"
        in MIGRATION
    )
    assert "payment_row.fecha" in MIGRATION
    assert "exception_row.vigente_desde" in MIGRATION
    assert "exception_row.vigente_hasta" in MIGRATION
