from pathlib import Path


MIGRATION = Path(
    "database/migrations/"
    "027_property_service_catalog_build02.sql"
).read_text(encoding="utf-8")

SERVICE = Path(
    "services/property_service_catalog.py"
).read_text(encoding="utf-8")


def test_service_catalog_is_property_scoped():
    for token in (
        "CREATE TABLE IF NOT EXISTS "
        "property_service_catalog",
        "condominio_id BIGINT NOT NULL",
        "UNIQUE(",
        "condominio_id,",
        "codigo",
    ):
        assert token in MIGRATION


def test_availability_supports_hierarchy():
    for token in (
        "property_service_availability",
        "'INMUEBLE'",
        "'ESTRUCTURA'",
        "'ESPACIO'",
        "estructura_id",
        "espacio_id",
        "hereda",
        "es_override",
        "prioridad",
        "vigente_desde",
        "vigente_hasta",
    ):
        assert token in MIGRATION


def test_continuity_policy_is_selective():
    for token in (
        "continuity_service_policy",
        "rule_version_id",
        "service_id",
        "treatment_code",
        "'MANTENER'",
        "'LIMITAR'",
        "'BLOQUEAR'",
        "restriction_detail",
        "restoration_detail",
    ):
        assert token in MIGRATION


def test_no_service_is_seeded_or_blocked():
    forbidden = (
        "Recepción de Paquetería",
        "Vigilancia",
        "Conserjería",
        "INSERT INTO property_service_catalog",
        "INSERT INTO continuity_service_policy",
        "operational_service_restriction",
    )

    for token in forbidden:
        assert token not in MIGRATION


def test_foundation_does_not_touch_financial_records():
    forbidden = (
        "INSERT INTO financial_obligations",
        "UPDATE financial_obligations",
        "INSERT INTO payment_allocations",
        "UPDATE payment_allocations",
        "INSERT INTO space_fee_history",
        "UPDATE space_fee_history",
    )

    for token in forbidden:
        assert token not in MIGRATION


def test_financial_thresholds_are_not_duplicated():
    forbidden = (
        "minimum_payment_percentage",
        "coverage_threshold",
        "'minimum_payment_percentage', 80",
        "'grace_days', 3",
    )

    for token in forbidden:
        assert token not in MIGRATION
        assert token not in SERVICE


def test_cross_property_integrity_is_enforced():
    for token in (
        "validate_property_service_availability_scope",
        "PROPERTY_SERVICE_STRUCTURE_SCOPE_MISMATCH",
        "PROPERTY_SERVICE_SPACE_SCOPE_MISMATCH",
        "validate_continuity_service_policy",
        "CONTINUITY_SERVICE_POLICY_PROPERTY_MISMATCH",
        "CONTINUITY_SERVICE_POLICY_INVALID_RULE",
    ):
        assert token in MIGRATION


def test_service_has_business_friendly_presentation():
    for token in (
        '"MANTENER": "Mantener disponible"',
        '"LIMITAR": "Aplicar restricción parcial"',
        '"BLOQUEAR": "Bloquear temporalmente"',
        "continuity_service_policy_rows",
        '"Servicio"',
        '"Tratamiento"',
        '"Detalle de restricción"',
        '"Criterio de restitución"',
    ):
        assert token in SERVICE


def test_service_has_no_streamlit_dependency():
    assert "import streamlit" not in SERVICE
    assert "st." not in SERVICE


def test_continuity_policy_active_contract_matches():
    assert "activo BOOLEAN NOT NULL" in MIGRATION
    assert "policy.activo" in SERVICE
    assert "policy.active" not in SERVICE
