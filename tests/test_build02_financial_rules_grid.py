from pathlib import Path

GRID = Path("services/financial_rules_grid.py").read_text(encoding="utf-8")

from pathlib import Path


SOURCE = Path(
    "services/financial_rules_grid.py"
).read_text(encoding="utf-8")


def test_rules_grid_service_exists():
    assert (
        "def list_financial_rule_grid("
        in SOURCE
    )


def test_rule_detail_service_exists():
    assert (
        "def get_financial_rule_detail("
        in SOURCE
    )


def test_fee_grid_service_exists():
    assert (
        "def list_space_fee_grid("
        in SOURCE
    )


def test_exception_grid_service_exists():
    assert (
        "def list_financial_exception_grid("
        in SOURCE
    )


def test_grid_reads_rule_definitions():
    assert (
        "FROM financial_rule_definitions"
        in SOURCE
    )


def test_grid_reads_applicability():
    assert (
        "FROM financial_rule_applicability"
        in SOURCE
    )


def test_grid_reads_rules_and_versions():
    assert "financial_rules rule" in SOURCE
    assert (
        "financial_rule_versions"
        in SOURCE
    )


def test_grid_supports_all_scopes():
    for token in (
        "CORE",
        "INMUEBLE",
        "ESTRUCTURA",
        "ESPACIO",
    ):
        assert token in SOURCE


def test_grid_exposes_inheritance():
    assert "inheritance_label" in SOURCE
    assert "override_label" in SOURCE


def test_grid_exposes_ai_and_kpi():
    assert "kpi_enabled" in SOURCE
    assert "ai_enabled" in SOURCE


def test_grid_filters_property_type():
    assert (
        "TIPO_INMUEBLE"
        in SOURCE
    )
    assert (
        "NATURALEZA_INMUEBLE"
        in SOURCE
    )


def test_service_has_no_write_sql():
    forbidden = (
        "INSERT INTO",
        "UPDATE ",
        "DELETE FROM",
        "TRUNCATE ",
    )

    for token in forbidden:
        assert token not in SOURCE

def test_global_catalog_read_model_exposes_compatibility_and_assignment():
    assert "def list_global_financial_rule_catalog(" in GRID
    assert '"assignment_label"' in GRID
    assert '"can_adopt"' in GRID
    assert '"can_override"' in GRID
    assert "FROM financial_rule_definitions" in GRID

def test_governed_rule_code_uses_acronym_year_rn_sequence():
    assert "def suggest_financial_rule_code(" in GRID
    assert 'stopwords={"DE","DEL","LA","LAS","EL","LOS","Y","EN","PARA","POR","CON","A"}' in GRID
    assert 'f"%-{code_year}-RN%"' in GRID
    assert 'highest+1:03d' in GRID

def test_unconfigured_definition_does_not_fake_core_configuration():
    assert 'row.get("scope_level")\n            if configured\n            else None' in GRID
    assert '"Catálogo de reglas" if row.get("rule_id") is None' in GRID
    assert '"Por definir"\n                    if not configured' in GRID
    assert '"Sin configurar"\n                    if not configured' in GRID
