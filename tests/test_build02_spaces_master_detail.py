from pathlib import Path
M=Path("database/migrations/006_spaces_master_detail_build02.sql")
S=Path("services/spaces.py").read_text(encoding="utf-8")
V=Path("views/espacios.py").read_text(encoding="utf-8")
def test_b02_master_detail_migration():
    base=M.read_text(encoding="utf-8")
    extension=Path("database/migrations/007_spaces_history_condition_build02.sql").read_text(encoding="utf-8")
    for x in ["clave","superficie_m2","ubicacion","nivel","uso_codigo","descripcion","responsable_persona_id","responsable_relacion"]: assert x in base
    for x in ["edificio_zona","anio_construccion","condicion_codigo"]: assert x in extension
def test_b02_responsible_is_related_to_personas():
    t=M.read_text(encoding="utf-8"); assert "REFERENCES personas(id)" in t and "LEFT JOIN personas" in S
def test_b02_space_fields_in_service():
    for x in ["superficie_m2","edificio_zona","nivel","uso_codigo","descripcion","anio_construccion","condicion_codigo","responsable_persona_id"]: assert x in S
def test_b02_grid_selection_drives_detail():
    assert 'selection_mode="single-row"' in V
    assert "selected=filtered[selected_index]" in V
    assert "0 <= selected_index < len(filtered)" in V
def test_b02_no_duplicate_space_status_labels():
    f=Path("core/formatting.py").read_text(encoding="utf-8")
    assert "'estado_codigo':'Estado De Ocupación'" in f
    assert "'activo':'Activo'" in f
def test_b02_reference_categories_preserved_by_catalogs():
    base=M.read_text(encoding="utf-8")
    extension=Path("database/migrations/007_spaces_history_condition_build02.sql").read_text(encoding="utf-8")
    assert "USO_ESPACIO" in base and "AREA_COMUN" in base
    assert "CONDICION_FISICA" in extension and "SOLO_TERRENO" in extension


def test_b02_occupancy_history_contract():
    assert "def list_occupancy_history" in S and "ORDER BY pe.fecha_inicio DESC" in S
    assert "def sync_responsible_history" in S and "fecha_fin=COALESCE" in S

def test_b02_building_zone_age_condition_contract():
    for x in ["Edificio / Zona","Fecha de construccion","Edad:","Condicion fisica","Historial cronologico de ocupacion"]: assert x in V
