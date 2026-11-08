from pathlib import Path
def r(p):return Path(p).read_text(encoding="utf-8")
def test_origin_catalog_uses_real_schema():
 s=r("database/migrations/004_admin_profile_r3_1.sql")
 assert "INSERT INTO catalogos(codigo,nombre,activo)" in s
 assert "INSERT INTO catalogo_valores(catalogo_id,codigo,nombre,activo)" in s
 assert "categoria" not in s
def test_origin_admin_seed_values():
 s=r("database/migrations/004_admin_profile_r3_1.sql")
 for x in ["ORIGEN_ADMIN","EMPRESA","INQUILINO","PRIVADO"]: assert x in s
def test_db_runner_rolls_back_failed_migration():
 s=r("core/db.py"); assert "conn.rollback()" in s
