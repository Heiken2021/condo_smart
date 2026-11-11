from pathlib import Path


def src():
    return Path("views/inmuebles.py").read_text(encoding="utf-8")


def test_grid_drives_selected_property():
    s = src()
    assert 'selection_mode="single-row"' in s
    assert 'st.session_state.inmueble_gestion_id' in s
    assert 'selected_row = all_by_id.get(selected_id)' in s


def test_edit_form_is_scoped_to_selected_property():
    s = src()
    assert 'st.form(f"edit_{row[\'id\']}")' in s
    assert 'form(row, f"e_{row[\'id\']}")' in s


def test_update_uses_selected_property_id():
    view = src()
    service = Path("services/properties.py").read_text(
        encoding="utf-8"
    )
    assert "update_property(" in view
    assert 'row["id"],' in view
    assert "def update_property(pid, values, actor_id):" in service
    assert "WHERE id=%s" in service
    assert 'row["id"]' in view


def test_audit_uses_selected_property_id():
    s = src()
    assert 'audit("INMUEBLE_MODIFICAR", "condominios", row["id"], before=row, after=values)' in s


def test_independent_property_selectors_removed():
    s = src()
    for key in ("gen", "admins", "brand", "state", "delete"):
        assert f'key="{key}"' not in s
