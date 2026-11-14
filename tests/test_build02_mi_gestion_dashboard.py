from pathlib import Path


ROOT = Path(__file__).parents[1]


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def test_admin_dashboard_service_exists():
    source = read("services/admin_dashboard.py")

    assert "def dashboard_scope" in source
    assert "def property_snapshot" in source
    assert "def portfolio_totals" in source
    assert "def property_type_distribution" in source


def test_root_scope_is_global():
    source = read("services/admin_dashboard.py")

    assert 'user.get("rol_global") == "SUPERADMIN"' in source
    assert '"scope": "GLOBAL"' in source
    assert '"Portafolio Global"' in source


def test_local_scope_uses_active_assignments():
    source = read("services/admin_dashboard.py")

    assert "JOIN usuario_inmuebles own_scope" in source
    assert "own_scope.usuario_id=%s" in source
    assert "own_scope.activo=TRUE" in source


def test_local_scope_is_limited_to_management_roles():
    source = read("services/admin_dashboard.py")

    assert '"ADMINISTRADOR"' in source
    assert '"GERENTE"' in source
    assert '"COMITE"' in source
    assert "ADMINISTRATIVE_SCOPE_REQUIRED" in source


def test_snapshot_contains_management_kpis():
    source = read("services/admin_dashboard.py")

    assert "espacios" in source
    assert "ocupados" in source
    assert "disponibles" in source
    assert "administradores" in source
    assert "ocupacion_pct" in source


def test_dashboard_is_informative_and_scope_aware():
    source = read("views/portafolio.py")

    assert '"Mi Gestión"' in source
    assert "scope['role_label']" in source
    assert "alcance autorizado" in source
    assert "Snapshot De Inmuebles Administrados" in source


def test_dashboard_has_executive_visuals():
    source = read("views/portafolio.py")

    assert "px.pie" in source
    assert "px.bar" in source
    assert "st.metric" in source
    assert "st.dataframe" in source


def test_dashboard_does_not_require_selected_property():
    source = read("views/portafolio.py")

    assert "condominio_id" not in source
    assert "cid()" not in source
    assert "st.session_state.get(\"condominio\"" not in source


def test_existing_navigation_keeps_portfolio_access():
    source = read("app.py")

    assert "('Portafolio','portafolio','views.portafolio')" in source


def test_permissions_keep_management_portfolio_access():
    source = read("core/permissions.py")

    assert "'portafolio'" in source
    assert "'ADMINISTRADOR'" in source
    assert "'GERENTE'" in source
