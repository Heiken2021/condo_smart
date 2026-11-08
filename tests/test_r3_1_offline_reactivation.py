from pathlib import Path

def read(path):
    return Path(path).read_text(encoding="utf-8")

def test_offline_property_keeps_management_pointer():
    s = read("core/access.py")
    marker = "Keep inmueble_gestion_id"
    assert marker in s

def test_inactive_grid_row_does_not_become_global_active():
    s = read("views/inmuebles.py")
    assert 'if selected_property.get("activo")' in s
    assert "offline property remains selected" in s.lower()

def test_state_change_is_explicit_not_toggle():
    s = read("views/inmuebles.py")
    assert "activo=NOT activo" not in s
    assert "UPDATE condominios SET activo=%s" in s

def test_offline_and_reactivation_require_confirmation():
    s = read("views/inmuebles.py")
    assert "poner este inmueble Offline temporalmente" in s
    assert "deseo reactivar este inmueble" in s

def test_state_audit_has_before_after():
    s = read("views/inmuebles.py")
    assert 'before={"activo": is_active}' in s
    assert 'after={"activo": target_state}' in s
