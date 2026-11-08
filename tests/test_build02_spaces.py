from pathlib import Path


SERVICE = Path("services/spaces.py")
SCHEMA = Path("database/schema.sql")


def service_source():
    return SERVICE.read_text(encoding="utf-8")


def test_b02_01_spaces_service_exists():
    assert SERVICE.exists()


def test_b02_02_required_operations_exist():
    source = service_source()
    required = [
        "def list_spaces(",
        "def get_space(",
        "def create_space(",
        "def update_space(",
        "def set_active(",
        "def dependencies(",
        "def deletable(",
        "def delete_space(",
    ]
    for operation in required:
        assert operation in source


def test_b02_03_space_lookup_is_scoped_to_property():
    source = service_source()
    assert "WHERE id=%s AND condominio_id=%s" in source


def test_b02_04_space_update_is_scoped_to_property():
    source = service_source()
    assert "UPDATE espacios" in source
    assert "WHERE id=%s AND condominio_id=%s" in source


def test_b02_05_space_activation_is_scoped_to_property():
    source = service_source()
    assert "SET activo=%s" in source
    assert "WHERE id=%s AND condominio_id=%s" in source


def test_b02_06_space_delete_is_scoped_to_property():
    source = service_source()
    assert (
        '"DELETE FROM espacios WHERE id=%s AND condominio_id=%s"'
        in source
    )


def test_b02_07_dependencies_cover_existing_relations():
    source = service_source()
    for relation in [
        "persona_espacios",
        "usuario_espacios",
        "cargos",
        "pagos",
    ]:
        assert relation in source


def test_b02_08_existing_schema_supports_spaces_foundation():
    source = SCHEMA.read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS espacios" in source
    for field in [
        "condominio_id",
        "nombre",
        "tipo_codigo",
        "estado_codigo",
        "cuota_base",
        "indiviso_pct",
        "activo",
    ]:
        assert field in source
