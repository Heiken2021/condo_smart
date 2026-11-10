from pathlib import Path
E=Path('views/espacios.py').read_text(encoding='utf-8')
S=Path('services/property_structure.py').read_text(encoding='utf-8')
M=Path('database/migrations/011_spaces_direct_private_integrity_build02.sql').read_text(encoding='utf-8')
def test_location_grid_is_selectable_and_scoped_by_property():
 assert 'key=f"spaces_location_grid_{pid}"' in E and 'selection_mode="single-row"' in E
 assert '"Espacios Directos"' in E and 'list_space_locations' in E and 'node_path' in E
def test_space_grid_remains_selectable_and_scoped_by_property():
 assert 'key=f"spaces_master_grid_{pid}"' in E and 'Espacio / Casa' in E
def test_create_uses_selected_location():
 assert 'forced_structure_id=selected_structure_id' in E and 'lock_structure=True' in E
def test_direct_spaces_are_allowed():
 assert 'if structure_id is None:' in S and 'return None' in S
 assert 'PRIVADA_REQUIRED' not in S
def test_database_integrity_trigger():
 assert 'trg_validar_estructura_espacio_build02' in M
 assert "inmueble_tipo <> 'FRACCIONAMIENTO'" in M

def test_space_master_detail_standard():
 assert '"+ Alta De Espacio"' in E
 assert 'space_create_mode' in E
 assert 'management_section=st.radio(' in E
 assert 'if management_section=="Editar":' in E
 assert 'if management_section=="Cambiar Estado":' in E
 assert 'if management_section=="Eliminar":' in E
 assert 'tabs=st.tabs(["Editar","Cambiar Estado","Eliminar"])' not in E
 assert E.index('if selected:') < E.index('management_section=st.radio(')
 assert E.index('if location_selected is not None:') < E.index('"+ Alta De Espacio"')
