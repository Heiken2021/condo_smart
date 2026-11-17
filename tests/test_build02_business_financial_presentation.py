from services.financial_rule_presenter import (
    business_applicability,
    business_priority,
    business_status,
    configured_parameter_rows,
)


def test_priority_is_business_friendly():
    assert business_priority(100) == "Baja"
    assert business_priority(200) == "Normal"
    assert business_priority(300) == "Alta"
    assert business_priority(400) == "Crítica"
    assert business_priority(None) == "—"


def test_status_is_business_friendly():
    assert (
        business_status("BORRADOR")
        == "Borrador"
    )

    assert (
        business_status("SIN_CONFIGURAR")
        == "Sin configurar"
    )


def test_applicability_is_business_friendly():
    assert (
        business_applicability(
            "TIPO_INMUEBLE:FRACCIONAMIENTO"
        )
        == "Fraccionamiento"
    )


def test_partial_payment_is_business_friendly():
    schema = {
        "minimum_compliance": {
            "type": "boolean",
        },
        "minimum_payment_percentage": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "unit": "PERCENT",
        },
    }

    rows = configured_parameter_rows(
        schema,
        {
            "minimum_compliance": True,
            "minimum_payment_percentage": 80.0,
        },
    )

    by_name = {
        row["Parámetro"]: row
        for row in rows
    }

    compliance = by_name[
        "Considerar cumplido el mínimo"
    ]

    percentage = by_name[
        "Pago mínimo requerido"
    ]

    assert (
        compliance["Valor configurado"]
        == "Sí"
    )

    assert (
        percentage["Valor configurado"]
        == "80,00 %"
    )

    assert (
        percentage["Límites permitidos"]
        == "De 0 % a 100 %"
    )

    assert percentage["Unidad"] == "%"


def test_none_is_not_exposed():
    assert business_priority(None) == "—"
