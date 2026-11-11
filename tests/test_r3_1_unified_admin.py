from pathlib import Path

def source():
    return Path("views/inmuebles.py").read_text(encoding="utf-8")

def test_admin_grid_is_master_selector():
    s = source()
    assert "admin_management_grid_" in s
    assert 'selection_mode="single-row"' in s
    assert 'on_select="rerun"' in s

def test_admin_management_id_exists():
    s = source()
    assert "admin_gestion_id" in s
    assert "admin_selected_rows" in s
    assert "admin_by_id" in s

def test_old_admin_dropdown_removed():
    s = source()
    assert "admin_master_" not in s
    assert "selected_admin_label" not in s

def test_grid_selection_drives_admin():
    s = source()
    assert 'admins[admin_index]["id"]' in s
    assert 'admin = get_admin(row["id"], admin_id, user["id"])' in s

def test_username_remains_editable():
    s = source()
    assert 'admin_username = c1.text_input(' in s
    assert '"Usuario"' in s

def test_password_policy_preserved():
    assert "La contraseña no cumple la política de seguridad" in source()
