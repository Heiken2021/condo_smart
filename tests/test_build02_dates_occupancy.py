from pathlib import Path
M=Path("database/migrations/008_construction_dates_occupancy_build02.sql").read_text(encoding="utf-8")
V=Path("views/espacios.py").read_text(encoding="utf-8")
S=Path("services/spaces.py").read_text(encoding="utf-8")
def test_008_dates_schema():
 assert "condominios ADD COLUMN IF NOT EXISTS fecha_construccion DATE" in M
 assert "espacios ADD COLUMN IF NOT EXISTS fecha_construccion DATE" in M
def test_spaces_use_calendar_dates():
 assert 'date_input("Fecha de construccion"' in V
 assert 'date_input("Fecha de ocupacion / inicio de relacion"' in V
def test_occupancy_history_accepts_start_date():
 assert "def sync_responsible_history(" in S
 assert '"ESPACIO_MODIFICAR"' in S
 assert "actor_id=None" in S
 assert "COALESCE(%s,CURRENT_DATE)" in S
