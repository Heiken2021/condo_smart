from services.financial_rule_presenter import business_applicability

def test_composite_property_type_applicability_is_business_language():
    assert business_applicability("TIPO_INMUEBLE:FRACCIONAMIENTO · TIPO_INMUEBLE:PLAZA_COMERCIAL") == "Fraccionamiento · Plaza comercial"

def test_single_property_type_applicability_still_works():
    assert business_applicability("TIPO_INMUEBLE:FRACCIONAMIENTO") == "Fraccionamiento"

def test_general_and_unknown_values_are_safe():
    assert business_applicability("General") == "General"
    assert business_applicability(None) == "—"
