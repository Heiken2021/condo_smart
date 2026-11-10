from pathlib import Path

M = Path('database/migrations/013_general_property_hierarchy_build02.sql').read_text(encoding='utf-8')
S = Path('services/property_structure.py').read_text(encoding='utf-8')
I = Path('views/inmuebles.py').read_text(encoding='utf-8')
E = Path('views/espacios.py').read_text(encoding='utf-8')


def test_migration_evolves_without_rewriting_history():
    assert 'DROP CONSTRAINT IF EXISTS ck_estructura_tipo_privada' in M
    assert 'DROP CONSTRAINT IF EXISTS ck_estructura_privada_raiz' in M
    assert 'validar_nodo_estructura_build02' in M
    assert 'validar_estructura_espacio_build02' in M


def test_service_supports_general_hierarchy():
    for value in ['CONJUNTO_URBANO','FRACCIONAMIENTO','PRIVADA','EDIFICIO','TORRE','SECCION','ZONA']:
        assert value in S
    assert 'parent_id' in S
    assert 'node_path' in S
    assert 'INVALID_STRUCTURE_LOCATION' in S


def test_inmuebles_has_general_structure_manager():
    assert 'Agregar Estructura' in I
    assert 'Estructura Padre' in I
    assert 'Tipo De Estructura' in I
    assert 'node_path' in I


def test_espacios_uses_all_active_locations():
    assert 'list_space_locations' in E
    assert 'node_path' in E
    assert 'Espacios Directos' in E
