from pathlib import Path

MIGRATION = Path("database/migrations/005_spaces_permissions_build02.sql")

def source():
    return MIGRATION.read_text(encoding="utf-8")

def test_b02_spaces_permissions_migration_exists():
    assert MIGRATION.exists()

def test_b02_spaces_permissions_are_defined():
    text = source()
    for code in ["ESPACIO_CONSULTAR", "ESPACIO_CREAR", "ESPACIO_MODIFICAR", "ESPACIO_DESACTIVAR", "ESPACIO_REACTIVAR", "ESPACIO_ELIMINAR"]:
        assert code in text

def test_b02_spaces_permissions_are_assigned_to_administrador():
    text = source()
    assert "INSERT INTO rol_permisos" in text
    assert "SELECT 'ADMINISTRADOR', codigo, TRUE" in text

def test_b02_spaces_permissions_migration_is_idempotent():
    assert source().count("ON CONFLICT DO NOTHING") >= 2
