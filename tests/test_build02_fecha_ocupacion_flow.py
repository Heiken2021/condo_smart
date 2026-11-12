from pathlib import Path
V=Path("views/espacios.py").read_text(encoding="utf-8")
def test_fecha_ocupacion_not_forwarded_to_space_service():
    assert V.count('fecha_ocupacion=data.pop("fecha_ocupacion", None)') >= 2
    assert 'update_space(pid,row["id"],actor_id=user["id"],**data)' in V
    assert 'record=create_space(pid,actor_id=user["id"],**data)' in V
def test_fecha_ocupacion_is_forwarded_to_history():
    assert 'data.get("responsable_relacion"),fecha_ocupacion,user["id"])' in V
