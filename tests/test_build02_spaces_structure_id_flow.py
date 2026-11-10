from pathlib import Path

S = Path("services/spaces.py").read_text(encoding="utf-8")
E = Path("views/espacios.py").read_text(encoding="utf-8")


def test_list_spaces_returns_structure_id():
    list_query = S.split("def list_spaces", 1)[1].split("def get_space", 1)[0]
    assert "e.estructura_id" in list_query


def test_location_counts_use_structure_id():
    assert 'r.get("estructura_id") is None' in E
    assert 'r.get("estructura_id")==n["id"]' in E


def test_selected_location_filters_by_structure_id():
    assert (
        'r.get("estructura_id")==selected_structure_id'
        in E
    )
