from pathlib import Path

def src(): return Path("views/inmuebles.py").read_text(encoding="utf-8")

def test_property_search_and_filters_exist():
    s=src()
    for token in ["property_grid_search", "property_grid_type", "property_grid_status", "property_grid_currency"]: assert token in s

def test_property_grid_single_row_selection():
    s=src(); assert 'selection_mode="single-row"' in s and 'on_select="rerun"' in s

def test_property_management_id_is_single_source_of_truth():
    s=src(); assert "st.session_state.inmueble_gestion_id" in s and "selected_row = all_by_id.get(selected_id)" in s

def test_old_independent_selectors_removed():
    s=src()
    for key in ["gen", "admins", "brand", "state", "delete"]: assert f'key="{key}"' not in s

def test_all_management_tabs_use_master_selected_row():
    s=src(); assert s.count("row = selected_row") == 5

def test_filter_does_not_silently_change_selection():
    s=src(); assert "La selección se conserva" in s

def test_create_tab_remains_available():
    s=src(); assert 'with tabs[0]:' in s and 'INMUEBLE_CREAR' in s
