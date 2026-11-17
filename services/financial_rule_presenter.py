PARAMETER_DESCRIPTIONS = {
    "amount": (
        "Importe periódico utilizado para "
        "generar la obligación correspondiente."
    ),
    "frequency": (
        "Periodicidad con la que la regla puede "
        "generar obligaciones."
    ),
    "due_day": (
        "Día del periodo en el que vence la "
        "obligación. Si no se configura, se "
        "utiliza el comportamiento predeterminado."
    ),
}

PARAMETER_LABELS = {
    "amount": "Importe",
    "frequency": "Frecuencia",
    "due_day": "Día de vencimiento",
    "minimum_payment_percentage": "Pago mínimo requerido",
    "minimum_compliance": "Considerar cumplido el mínimo",
    "surcharge_percentage": "Porcentaje de recargo",
    "calculation_base": "Base de cálculo",
    "grace_days": "Días de gracia",
    "surcharge_frequency": "Frecuencia del recargo",
    "maximum_surcharge_percentage": "Recargo máximo",
    "minimum_coverage_percentage": "Cobertura mínima requerida",
    "tolerance_days": "Días de tolerancia",
    "prior_notice_required": "Requiere aviso previo",
    "authorization_required": "Requiere autorización",
    "operational_action": "Acción operativa",
}

TYPE_LABELS = {
    "number": "Monetario",
    "integer": "Número entero",
    "string": "Selección",
    "boolean": "Sí / No",
}

VALUE_LABELS = {
    "MENSUAL": "Mensual",
    "SEMANAL": "Semanal",
    "QUINCENAL": "Quincenal",
    "ANUAL": "Anual",
    "SALDO_PENDIENTE": "Saldo pendiente",
    "OBLIGACION_ORIGINAL": "Obligación original",
    "UNICA": "Una sola vez",
    "DIARIA": "Diaria",
    "SIN_CAMBIO": "Sin cambio operativo",
    "REVISAR": "Revisión administrativa",
    "RESTRINGIR_SEGUN_POLITICA": "Aplicar restricción según política",
}

STATUS_LABELS = {
    "SIN_CONFIGURAR": "Sin configurar",
    "SIN_VERSION": "Sin versión",
    "BORRADOR": "Borrador",
    "APROBADO": "Aprobado",
    "VIGENTE": "Vigente",
    "CERRADO": "Finalizado",
    "RECHAZADO": "Rechazado",
    "PENDIENTE": "Pendiente",
}

SCOPE_LABELS = {
    "CORE": "Base del sistema",
    "INMUEBLE": "Todo el inmueble",
    "ESTRUCTURA": "Estructura",
    "ESPACIO": "Espacio",
}


def business_status(value):
    return STATUS_LABELS.get(
        value,
        str(value or "Sin estado"),
    )


def business_scope(value):
    return SCOPE_LABELS.get(
        value,
        str(value or "Base del sistema"),
    )


def business_value(value):
    if value is None:
        return "—"

    if isinstance(value, bool):
        return "Sí" if value else "No"

    if isinstance(value, list):
        return ", ".join(
            business_value(item)
            for item in value
        )

    return VALUE_LABELS.get(
        str(value),
        str(value),
    )


def _numeric_condition(
    specification,
    *,
    currency=None,
):
    minimum = specification.get("minimum")
    maximum = specification.get("maximum")

    unit = (
        specification.get("unit")
        or currency
    )

    if (
        minimum is not None
        and maximum is not None
    ):
        if unit == "PERCENT":
            return (
                f"De {minimum:g} % a "
                f"{maximum:g} %"
            )

        if unit == "MXN":
            return (
                f"De ${float(minimum):,.2f} "
                f"a ${float(maximum):,.2f} MXN"
            )

        return (
            f"De {minimum} a {maximum}"
        )

    if minimum is not None:
        if unit == "PERCENT":
            return f"Mínimo {minimum:g} %"

        if unit == "MXN":
            return (
                f"Mínimo "
                f"${float(minimum):,.2f} MXN"
            )

        return f"Mínimo {minimum}"

    if maximum is not None:
        if unit == "PERCENT":
            return f"Máximo {maximum:g} %"

        if unit == "MXN":
            return (
                f"Máximo "
                f"${float(maximum):,.2f} MXN"
            )

        return f"Máximo {maximum}"

    return "Sin límites definidos"


def _configured_business_value(
    *,
    code,
    value,
    specification,
):
    if value is None:
        return "—"

    if isinstance(value, bool):
        return "Sí" if value else "No"

    unit = (
        specification.get("unit")
        or specification.get("currency")
    )

    if unit == "PERCENT":
        return (
            f"{float(value):,.2f} %"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    if unit == "MXN":
        return (
            f"${float(value):,.2f} MXN"
        )

    return business_value(value)


def parameter_schema_rows(schema):
    if not isinstance(schema, dict):
        return []

    rows = []

    ordered_keys = [
        key
        for key in PARAMETER_LABELS
        if key in schema
    ]

    ordered_keys.extend(
        sorted(
            key
            for key in schema
            if key not in ordered_keys
        )
    )

    for key in ordered_keys:
        specification = (
            schema.get(key) or {}
        )

        if not isinstance(
            specification,
            dict,
        ):
            specification = {
                "default": specification,
            }

        type_code = specification.get(
            "type",
            "string",
        )

        currency = specification.get(
            "currency"
        )

        unit = (
            specification.get("unit")
            or currency
        )

        allowed = specification.get(
            "allowed"
        ) or []

        optional = bool(
            specification.get(
                "optional",
                False,
            )
        )

        if allowed:
            condition = (
                "Valores permitidos: "
                + ", ".join(
                    business_value(value)
                    for value in allowed
                )
            )
        elif type_code in {
            "number",
            "integer",
        }:
            condition = _numeric_condition(
                specification,
                currency=currency,
            )
        else:
            condition = (
                "Sin restricciones adicionales"
            )

        rows.append(
            {
                "Código": key,
                "Parámetro": (
                    PARAMETER_LABELS.get(
                        key,
                        key.replace(
                            "_",
                            " ",
                        ).title(),
                    )
                ),
                "Tipo": (
                    TYPE_LABELS.get(
                        type_code,
                        type_code,
                    )
                ),
                "Descripción": (
                    PARAMETER_DESCRIPTIONS.get(
                        key,
                        "Parámetro configurable "
                        "de la regla."
                    )
                ),
                "Límites permitidos": condition,
                "Obligatorio": (
                    "No" if optional else "Sí"
                ),
                "Unidad": (
                    "%"
                    if unit == "PERCENT"
                    else (
                        unit
                        if unit
                        else "—"
                    )
                ),
                "Valor predeterminado": (
                    business_value(
                        specification.get(
                            "default"
                        )
                    )
                ),
            }
        )

    return rows


def configured_parameter_rows(
    schema,
    values,
):
    definitions = parameter_schema_rows(
        schema
    )

    values = (
        values
        if isinstance(values, dict)
        else {}
    )

    definitions_by_code = {
        row["Código"]: row
        for row in definitions
    }

    result = []

    for code, definition in (
        definitions_by_code.items()
    ):
        specification = (
            schema.get(code)
            or {}
        )

        result.append(
            {
                "Parámetro": (
                    definition["Parámetro"]
                ),
                "Valor configurado": (
                    _configured_business_value(
                        code=code,
                        value=values.get(code),
                        specification=specification,
                    )
                ),
                "Límites permitidos": (
                    definition[
                        "Límites permitidos"
                    ]
                ),
                "Unidad": (
                    definition["Unidad"]
                ),
            }
        )

    return result


def business_priority(value):
    labels = {
        100: "Baja",
        200: "Normal",
        300: "Alta",
        400: "Crítica",
    }

    if value is None:
        return "—"

    return labels.get(
        int(value),
        str(value),
    )


def business_applicability(value):
    labels = {
        "TIPO_INMUEBLE:FRACCIONAMIENTO":
            "Fraccionamiento",
    }

    return labels.get(
        value,
        value or "—",
    )
