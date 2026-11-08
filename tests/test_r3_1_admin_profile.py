from pathlib import Path
def r(p):return Path(p).read_text(encoding="utf-8")
def test_active_property_green_badge():
 s=r("core/access.py");assert "#D9F5E5" in s and "#087D45" in s
def test_admin_profile_migration():
 s=r("database/migrations/004_admin_profile_r3_1.sql")
 for x in ["telefono_of_casa","telefono_celular","direccion","origen_codigo","ORIGEN_ADMIN","EMPRESA","INQUILINO","PRIVADO"]:assert x in s
def test_admin_profile_editor():
 s=r("views/inmuebles.py")
 for x in ["Tel. Of / Casa","Tel. Celular","Dirección","Origen","Guardar Datos Del Administrador"]:assert x in s
def test_admin_profile_service():assert "def update_admin_profile(" in r("services/property_admins.py")
def test_admin_profile_audit():assert "ADMINISTRADOR_MODIFICAR" in r("views/inmuebles.py")
