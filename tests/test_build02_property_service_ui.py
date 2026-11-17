from pathlib import Path


VIEW = Path(
    "views/property_service_catalog.py"
).read_text(encoding="utf-8")

GOVERNANCE = Path(
    "views/financial_governance.py"
).read_text(encoding="utf-8")


INMUEBLES = Path(
    "views/inmuebles.py"
).read_text(encoding="utf-8")


def test_service_catalog_has_business_grid():
    for token in (
        "Catálogo de Servicios",
        "Nuevo servicio",
        "Editar",
        "Desactivar",
        "Activar",
        "Disponibilidad",
        "selection_mode=\"single-row\"",
    ):
        assert token in VIEW


def test_service_catalog_has_governed_forms():
    for token in (
        "create_property_service(",
        "update_property_service(",
        "set_property_service_active(",
        "create_service_availability(",
        "FINANZAS_REGLA_GESTIONAR",
    ):
        assert token in VIEW


def test_availability_supports_hierarchy():
    for token in (
        "Todo el inmueble",
        "Estructura",
        "Espacio",
        "Heredar a niveles inferiores",
        "Es una configuración específica",
        "Prioridad",
        "Vigente desde",
        "Vigente hasta",
    ):
        assert token in VIEW


def test_ui_does_not_apply_restrictions():
    forbidden = (
        "operational_service_restriction",
        "minimum_payment_percentage",
        "grace_days",
        "UPDATE espacios",
        "Bloquear temporalmente",
    )

    for token in forbidden:
        assert token not in VIEW


def test_property_services_live_under_inmuebles():
    assert (
        '"Estructura", "Servicios", "Administradores"'
        in INMUEBLES
    )
    assert (
        "render_property_service_catalog("
        in INMUEBLES
    )


def test_financial_governance_has_no_service_catalog_tab():
    governance_render = GOVERNANCE[
        GOVERNANCE.index(
            "def render_governance_section("
        ):
    ]

    assert "service_tab" not in governance_render
    assert (
        "render_property_service_catalog("
        not in governance_render
    )


def test_services_are_primary_and_active_by_default():
    assert '"Catálogo Servicios"' in VIEW
    assert '"Categorías"' in VIEW
    assert VIEW.index('"Catálogo Servicios"') < VIEW.rindex('"Categorías"')
    assert "Mostrar servicios inactivos" in VIEW
    assert "active_only=not include_inactive" in VIEW
