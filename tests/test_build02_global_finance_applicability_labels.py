from pathlib import Path
FIN=Path("views/finanzas.py").read_text(encoding="utf-8")
PRES=Path("services/financial_rule_presenter.py").read_text(encoding="utf-8")

def test_global_catalog_uses_business_applicability_presenter():
    assert 'from services.financial_rule_presenter import business_applicability' in FIN
    assert '"Disponible para": business_applicability(row.get("applicability_label"))' in FIN

def test_presenter_knows_plaza_and_fraccionamiento():
    assert 'TIPO_INMUEBLE:FRACCIONAMIENTO' in PRES
    assert 'TIPO_INMUEBLE:PLAZA_COMERCIAL' in PRES
    assert 'Plaza comercial' in PRES
