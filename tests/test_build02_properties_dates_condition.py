from pathlib import Path
V=Path("views/inmuebles.py").read_text(encoding="utf-8")
S=Path("services/properties.py").read_text(encoding="utf-8")
M=Path("database/migrations/008_construction_dates_occupancy_build02.sql").read_text(encoding="utf-8")

def test_properties_calendar_and_age():
    assert 'date_input(' in V and '"Fecha De Construcción"' in V
    assert "Antigüedad calculada" in V

def test_properties_condition_catalog():
    assert 'options("CONDICION_FISICA")' in V
    assert '"Estado O Condición"' in V

def test_properties_persist_new_fields():
    assert "fecha_construccion,condicion_codigo" in V
    assert "c.fecha_construccion,c.condicion_codigo" in S

def test_008_supports_property_fields():
    assert "condominios ADD COLUMN IF NOT EXISTS fecha_construccion DATE" in M
    assert "condominios ADD COLUMN IF NOT EXISTS condicion_codigo" in M
