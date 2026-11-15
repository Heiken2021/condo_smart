from pathlib import Path


MIGRATION = Path(
    "database/migrations/"
    "020_financial_governance_build02.sql"
).read_text(encoding="utf-8")


def test_rule_definition_supports_governance_capabilities():
    for token in [
        "obligatoria BOOLEAN",
        "admite_especializacion BOOLEAN",
        "admite_herencia BOOLEAN",
        "admite_override BOOLEAN",
        "admite_excepcion BOOLEAN",
        "requiere_aprobacion BOOLEAN",
    ]:
        assert token in MIGRATION


def test_rule_definition_controls_allowed_depth():
    for token in [
        "permite_nivel_inmueble",
        "permite_nivel_estructura",
        "permite_nivel_espacio",
    ]:
        assert token in MIGRATION


def test_rule_definition_declares_kpi_and_ai_context():
    assert "contexto_kpi BOOLEAN" in MIGRATION
    assert "contexto_ia BOOLEAN" in MIGRATION


def test_rule_applicability_exists():
    normalized = " ".join(
        MIGRATION.split()
    )
    assert (
        "CREATE TABLE IF NOT EXISTS "
        "financial_rule_applicability"
    ) in normalized


def test_rule_applicability_supports_typology_dimensions():
    for token in [
        "TIPO_INMUEBLE",
        "TIPO_ESTRUCTURA",
        "TIPO_ESPACIO",
        "GIRO",
    ]:
        assert token in MIGRATION


def test_rule_resolution_layers_exist():
    for token in [
        "'CORE'",
        "'TIPOLOGIA'",
        "'INMUEBLE'",
        "'ESTRUCTURA'",
        "'ESPACIO'",
    ]:
        assert token in MIGRATION


def test_rules_support_override_and_inheritance():
    assert "hereda BOOLEAN" in MIGRATION
    assert "es_override BOOLEAN" in MIGRATION
    assert "prioridad INTEGER" in MIGRATION


def test_rules_have_versioned_parameters():
    assert (
        "CREATE TABLE IF NOT EXISTS "
        "financial_rule_versions"
    ) in MIGRATION

    assert "version_num INTEGER" in MIGRATION
    assert "parametros JSONB" in MIGRATION
    assert "vigente_desde DATE" in MIGRATION
    assert "vigente_hasta DATE" in MIGRATION


def test_financial_objectives_exist():
    assert (
        "CREATE TABLE IF NOT EXISTS "
        "financial_objectives"
    ) in MIGRATION


def test_financial_policies_exist():
    assert (
        "CREATE TABLE IF NOT EXISTS "
        "financial_policies"
    ) in MIGRATION


def test_space_fee_history_is_versioned():
    assert (
        "CREATE TABLE IF NOT EXISTS "
        "space_fee_history"
    ) in MIGRATION

    for token in [
        "monto_mxn",
        "vigente_desde",
        "vigente_hasta",
        "rule_version_id",
    ]:
        assert token in MIGRATION


def test_financial_exceptions_exist():
    assert (
        "CREATE TABLE IF NOT EXISTS "
        "financial_rule_exceptions"
    ) in MIGRATION

    for token in [
        "PENDIENTE",
        "APROBADA",
        "RECHAZADA",
        "CANCELADA",
        "VENCIDA",
    ]:
        assert token in MIGRATION


def test_exceptions_are_attributable():
    for token in [
        "solicitado_por",
        "solicitado_en",
        "resuelto_por",
        "resuelto_en",
        "decision_detalle",
    ]:
        assert token in MIGRATION


def test_scope_validates_structure_and_space():
    assert (
        "validate_financial_governance_scope"
        in MIGRATION
    )

    assert (
        "FINANCIAL_GOVERNANCE_SCOPE_MISMATCH"
        in MIGRATION
    )

    assert (
        "FINANCIAL_GOVERNANCE_SPACE_SCOPE_MISMATCH"
        in MIGRATION
    )


def test_governance_supports_core_without_property():
    assert (
        "scope_level IN ("
        in MIGRATION
    )

    assert (
        "condominio_id IS NULL"
        in MIGRATION
    )


def test_governance_does_not_define_economic_values():
    forbidden = [
        "CUOTA_MINIMA=500",
        "PAGO_MINIMO=500",
        "INTERES_MORATORIO=5",
        "COBRANZA_OBJETIVO=95",
        "MOROSIDAD=10",
    ]

    for token in forbidden:
        assert token not in MIGRATION


def test_governance_does_not_create_obligations_yet():
    assert (
        "CREATE TABLE IF NOT EXISTS "
        "financial_obligations"
    ) not in MIGRATION

    assert (
        "CREATE TABLE IF NOT EXISTS "
        "payment_allocations"
    ) not in MIGRATION


def test_governance_does_not_mutate_current_movements():
    for token in [
        "ALTER TABLE cargos",
        "ALTER TABLE pagos",
        "ALTER TABLE gastos",
        "UPDATE cargos",
        "UPDATE pagos",
        "UPDATE gastos",
        "DELETE FROM cargos",
        "DELETE FROM pagos",
        "DELETE FROM gastos",
    ]:
        assert token not in MIGRATION


def test_existing_cuota_base_is_preserved():
    assert "DROP COLUMN cuota_base" not in MIGRATION


def test_ai_does_not_receive_auto_execution_permissions():
    forbidden = [
        "AI_AUTO_APPROVE",
        "AI_AUTO_EXECUTE",
        "IA_AUTO_APROBAR",
        "IA_AUTO_EJECUTAR",
    ]

    for token in forbidden:
        assert token not in MIGRATION


def test_governance_permissions_exist():
    for token in [
        "FINANZAS_GOBIERNO_CONSULTAR",
        "FINANZAS_OBJETIVO_GESTIONAR",
        "FINANZAS_POLITICA_GESTIONAR",
        "FINANZAS_REGLA_GESTIONAR",
        "FINANZAS_REGLA_APROBAR",
        "FINANZAS_CUOTA_GESTIONAR",
        "FINANZAS_EXCEPCION_SOLICITAR",
        "FINANZAS_EXCEPCION_RESOLVER",
    ]:
        assert token in MIGRATION



def test_rule_capabilities_are_enforced():
    assert (
        "validate_financial_rule_capabilities"
        in MIGRATION
    )

    for token in [
        "FINANCIAL_RULE_SPECIALIZATION_NOT_ALLOWED",
        "FINANCIAL_RULE_OVERRIDE_NOT_ALLOWED",
        "FINANCIAL_RULE_INHERITANCE_NOT_ALLOWED",
        "FINANCIAL_RULE_STRUCTURE_LEVEL_NOT_ALLOWED",
        "FINANCIAL_RULE_SPACE_LEVEL_NOT_ALLOWED",
        "FINANCIAL_MANDATORY_RULE_CANNOT_BE_REDEFINED",
    ]:
        assert token in MIGRATION


def test_objective_and_policy_scope_are_enforced():
    assert (
        "validate_financial_property_structure_scope"
        in MIGRATION
    )
    assert (
        "validate_financial_policy_objective"
        in MIGRATION
    )
    assert (
        "FINANCIAL_POLICY_OBJECTIVE_SCOPE_MISMATCH"
        in MIGRATION
    )


def test_approved_records_require_attribution():
    assert (
        "validate_financial_approval_metadata"
        in MIGRATION
    )
    assert (
        "FINANCIAL_APPROVAL_METADATA_REQUIRED"
        in MIGRATION
    )


def test_rule_versions_cannot_overlap():
    assert (
        "validate_financial_rule_version_overlap"
        in MIGRATION
    )
    assert "daterange(" in MIGRATION
    assert (
        "FINANCIAL_RULE_VERSION_OVERLAP"
        in MIGRATION
    )


def test_space_fee_versions_cannot_overlap():
    assert (
        "validate_space_fee_overlap"
        in MIGRATION
    )
    assert (
        "FINANCIAL_SPACE_FEE_OVERLAP"
        in MIGRATION
    )


def test_exceptions_respect_rule_capabilities():
    assert (
        "validate_financial_rule_exception"
        in MIGRATION
    )
    assert (
        "FINANCIAL_RULE_EXCEPTION_NOT_ALLOWED"
        in MIGRATION
    )
    assert (
        "FINANCIAL_EXCEPTION_RULE_SCOPE_MISMATCH"
        in MIGRATION
    )


def test_exception_resolution_is_attributable():
    assert (
        "FINANCIAL_EXCEPTION_REQUESTER_REQUIRED"
        in MIGRATION
    )
    assert (
        "FINANCIAL_EXCEPTION_DECISION_REQUIRED"
        in MIGRATION
    )


def test_approved_rule_versions_are_immutable():
    assert (
        "prevent_approved_financial_rule_version_mutation"
        in MIGRATION
    )
    assert (
        "APPROVED_FINANCIAL_RULE_VERSION_IS_IMMUTABLE"
        in MIGRATION
    )
    assert "BEFORE UPDATE OR DELETE" in MIGRATION



def test_approved_rule_version_supports_controlled_closure():
    for token in [
        "cerrado_por",
        "cerrado_en",
        "motivo_cierre",
        "FINANCIAL_RULE_VERSION_CLOSURE_METADATA_REQUIRED",
    ]:
        assert token in MIGRATION


def test_rule_version_closure_preserves_economic_content():
    assert "to_jsonb(NEW)" in MIGRATION
    assert "to_jsonb(OLD)" in MIGRATION
    assert "'vigente_hasta'" in MIGRATION
    assert "'motivo_cierre'" in MIGRATION


def test_closed_rule_version_cannot_change_again():
    assert (
        "CLOSED_FINANCIAL_RULE_VERSION_IS_IMMUTABLE"
        in MIGRATION
    )


def test_approved_rule_version_cannot_be_deleted():
    assert "TG_OP='DELETE'" in MIGRATION
    assert (
        "APPROVED_FINANCIAL_RULE_VERSION_IS_IMMUTABLE"
        in MIGRATION
    )
