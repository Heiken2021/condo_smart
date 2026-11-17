from pathlib import Path


MIGRATION = Path(
    "database/migrations/"
    "028_property_service_categories_build02.sql"
).read_text(encoding="utf-8")

SERVICE = Path(
    "services/property_service_categories.py"
).read_text(encoding="utf-8")


def test_categories_are_property_scoped():
    for token in (
        "property_service_categories",
        "condominio_id BIGINT NOT NULL",
        "codigo VARCHAR(100) NOT NULL",
        "nombre VARCHAR(160) NOT NULL",
        "descripcion TEXT",
        "orden INTEGER",
        "activo BOOLEAN",
    ):
        assert token in MIGRATION


def test_categories_are_not_seeded():
    assert (
        "INSERT INTO property_service_categories"
        not in MIGRATION
    )

    for value in (
        "Seguridad",
        "Limpieza e Higiene",
        "Mantenimiento",
        "Conserjería",
        "Administración",
        "Servicios Públicos",
    ):
        assert value not in MIGRATION
        assert value not in SERVICE


def test_category_property_integrity_exists():
    for token in (
        "categoria_id",
        "validate_property_service_category",
        "PROPERTY_SERVICE_CATEGORY_PROPERTY_MISMATCH",
    ):
        assert token in MIGRATION


def test_suggested_service_code_uses_property_key():
    for token in (
        "SELECT clave",
        "FROM condominios",
        "FROM property_service_catalog",
        "maximum + 1",
        'f"{prefix}-S{sequence:03d}"',
    ):
        assert token in SERVICE


def test_service_code_uses_maximum_not_count():
    function = SERVICE[
        SERVICE.index(
            "def suggest_service_code("
        ):
    ]

    assert "maximum = 0" in function
    assert "max(" in function
    assert "COUNT(" not in function


def test_category_service_has_no_writes():
    forbidden = (
        "INSERT INTO",
        "UPDATE ",
        "DELETE FROM",
    )

    for token in forbidden:
        assert token not in SERVICE
