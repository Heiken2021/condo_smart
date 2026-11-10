from pathlib import Path
M=Path('database/migrations/009_property_hierarchy_build02.sql').read_text()
S=Path('services/property_structure.py').read_text()
I=Path('views/inmuebles.py').read_text()
E=Path('views/espacios.py').read_text()
P=Path('services/spaces.py').read_text()
def test_schema():
 assert "estructura_inmueble" in M
 assert "estructura_id" in M
 migration_010=Path("database/migrations/010_correct_property_hierarchy_build02.sql").read_text(encoding="utf-8")
 for x in ["EDIFICIO","CONDOMINIO","FRACCIONAMIENTO","CHECK(tipo_codigo='PRIVADA')"]:
  assert x in migration_010
def test_rules():
 assert "validate_space_structure" in S
 assert "INVALID_STRUCTURE_LOCATION" in S
 assert "INVALID_STRUCTURE_LOCATION" in S
 assert "PRIVADA_REQUIRED" not in S
def test_ui():
 assert '"Agregar Estructura"' in I and '"Estructura Padre"' in I
 assert '"Agregar Estructura"' in I
 assert 'list_space_locations(pid' in E
 assert 'key=f"spaces_location_grid_{pid}"' in E
 assert '"Espacios Directos"' in E
 assert 'n.get("tipo_codigo")' in E
 assert 'selection_mode="single-row"' in E
def test_create_sql():
 assert 'responsable_relacion,estructura_id,cuota_base,indiviso_pct' in P
 assert 'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,TRUE)' in P


def test_applied_009_is_preserved_and_010_corrects_schema():
 import hashlib
 assert hashlib.sha256(Path('database/migrations/009_property_hierarchy_build02.sql').read_bytes()).hexdigest() == 'ac9e3ddf0477a0c92e858637ce355e767b0f5fb6395db174a7c628f6e6557e0b'
 migration_010=Path('database/migrations/010_correct_property_hierarchy_build02.sql').read_text()
 assert 'ck_estructura_tipo_privada' in migration_010
 assert "CHECK(tipo_codigo='PRIVADA')" in migration_010
 assert 'CHECK(parent_id IS NULL)' in migration_010
