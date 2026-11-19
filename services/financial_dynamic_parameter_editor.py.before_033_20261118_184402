import streamlit as st


PARAMETER_LABELS = {
    "amount": "Importe",
    "frequency": "Frecuencia",
    "due_day": "Día de vencimiento",
    "minimum_payment_percentage": (
        "Pago mínimo requerido"
    ),
    "minimum_compliance": (
        "Considerar cumplido el mínimo"
    ),
    "surcharge_percentage": (
        "Porcentaje de recargo"
    ),
    "calculation_base": (
        "Base de cálculo"
    ),
    "grace_days": (
        "Días de gracia"
    ),
    "surcharge_frequency": (
        "Frecuencia del recargo"
    ),
    "maximum_surcharge_percentage": (
        "Recargo máximo"
    ),
    "minimum_coverage_percentage": (
        "Cobertura mínima requerida"
    ),
    "tolerance_days": (
        "Días de tolerancia"
    ),
    "prior_notice_required": (
        "Requiere aviso previo"
    ),
    "authorization_required": (
        "Requiere autorización"
    ),
    "operational_action": (
        "Acción operativa"
    ),
}


PARAMETER_HELP = {
    "amount": (
        "Importe concreto que utilizará esta "
        "versión para la obligación correspondiente."
    ),
    "frequency": (
        "Periodicidad con la que se genera "
        "la obligación."
    ),
    "due_day": (
        "Día del periodo en el que vence "
        "la obligación."
    ),
    "minimum_payment_percentage": (
        "Porcentaje de la obligación que debe "
        "cubrirse para satisfacer el criterio "
        "mínimo configurado. El administrador "
        "define el porcentaje; Condo_Smart no "
        "asume un valor predeterminado."
    ),
    "minimum_compliance": (
        "Determina si alcanzar el porcentaje "
        "mínimo configurado satisface el criterio "
        "de cumplimiento mínimo de esta política."
    ),
    "surcharge_percentage": (
        "Porcentaje de recargo que podrá aplicarse "
        "cuando se cumplan las condiciones de "
        "morosidad de esta versión."
    ),
    "calculation_base": (
        "Importe sobre el que se calcula el "
        "recargo por morosidad."
    ),
    "grace_days": (
        "Número de días posteriores al vencimiento "
        "durante los que todavía no se aplica "
        "el recargo."
    ),
    "surcharge_frequency": (
        "Determina con qué periodicidad puede "
        "aplicarse el recargo configurado."
    ),
    "maximum_surcharge_percentage": (
        "Límite porcentual opcional para evitar "
        "que los recargos superen el máximo "
        "establecido por la política."
    ),
    "minimum_coverage_percentage": (
        "Porcentaje mínimo de cobertura financiera "
        "que esta política utilizará para evaluar "
        "la condición operativa."
    ),
    "tolerance_days": (
        "Número de días adicionales considerados "
        "por la política operativa."
    ),
    "prior_notice_required": (
        "Indica si debe existir un aviso previo "
        "antes de ejecutar la acción operativa."
    ),
    "authorization_required": (
        "Indica si la acción operativa requiere "
        "una autorización adicional."
    ),
    "operational_action": (
        "Acción que deberá evaluar el sistema "
        "cuando se cumplan las condiciones "
        "configuradas."
    ),
}


VALUE_LABELS = {
    "MENSUAL": "Mensual",
    "QUINCENAL": "Quincenal",
    "SEMANAL": "Semanal",
    "ANUAL": "Anual",
    "SALDO_PENDIENTE": "Saldo pendiente",
    "OBLIGACION_ORIGINAL": "Obligación original",
    "UNICA": "Una sola vez",
    "DIARIA": "Diaria",
    "SIN_CAMBIO": "Sin cambio operativo",
    "REVISAR": "Revisión administrativa",
    "RESTRINGIR_SEGUN_POLITICA": (
        "Aplicar restricción según política"
    ),
}


def parameter_label(code):
    return PARAMETER_LABELS.get(
        code,
        code.replace("_", " ").title(),
    )


def parameter_help(code):
    return PARAMETER_HELP.get(
        code,
        (
            "Valor configurable de esta regla. "
            "Debe respetar los límites definidos "
            "por el catálogo."
        ),
    )


def friendly_value(value):
    return VALUE_LABELS.get(
        str(value),
        str(value),
    )


def limits_text(specification):
    if not isinstance(
        specification,
        dict,
    ):
        return "Sin límites adicionales"

    parameter_type = specification.get(
        "type"
    )

    unit = specification.get(
        "unit"
    ) or specification.get(
        "currency"
    )

    allowed = (
        specification.get("allowed")
        or []
    )

    if allowed:
        return (
            "Opciones permitidas: "
            + ", ".join(
                friendly_value(value)
                for value in allowed
            )
        )

    minimum = specification.get(
        "minimum"
    )

    maximum = specification.get(
        "maximum"
    )

    pieces = []

    if minimum is not None:
        pieces.append(
            f"Mínimo {minimum}"
        )

    if maximum is not None:
        pieces.append(
            f"Máximo {maximum}"
        )

    if unit == "PERCENT":
        pieces = [
            f"{piece} %"
            for piece in pieces
        ]

    elif unit == "MXN":
        pieces = [
            f"{piece} MXN"
            for piece in pieces
        ]

    if pieces:
        return " · ".join(pieces)

    if parameter_type == "boolean":
        return "Sí o No"

    return "Sin límites adicionales"


def _number_default(
    *,
    specification,
    current_value,
):
    if current_value is not None:
        return float(current_value)

    return None


def _integer_default(
    *,
    specification,
    current_value,
):
    if current_value is not None:
        return int(current_value)

    return None


def missing_required_parameters(
    *,
    schema,
    values,
):
    schema = (
        schema
        if isinstance(schema, dict)
        else {}
    )

    values = (
        values
        if isinstance(values, dict)
        else {}
    )

    missing = []

    for code, specification in schema.items():
        specification = (
            specification
            if isinstance(
                specification,
                dict,
            )
            else {}
        )

        if specification.get(
            "optional",
            False,
        ):
            continue

        if (
            code not in values
            or values[code] is None
            or values[code] == ""
        ):
            missing.append(code)

    return missing


def render_parameter_inputs(
    *,
    schema,
    current_values=None,
    key_prefix,
):
    schema = (
        schema
        if isinstance(schema, dict)
        else {}
    )

    current_values = (
        current_values
        if isinstance(
            current_values,
            dict,
        )
        else {}
    )

    values = {}

    for code, specification in (
        schema.items()
    ):
        specification = (
            specification
            if isinstance(
                specification,
                dict,
            )
            else {}
        )

        label = parameter_label(code)

        help_text = parameter_help(code)

        parameter_type = (
            specification.get(
                "type",
                "string",
            )
        )

        optional = bool(
            specification.get(
                "optional",
                False,
            )
        )

        current_value = (
            current_values.get(code)
        )

        enabled = True

        if optional:
            enabled = st.checkbox(
                f"Configurar {label}",
                value=(
                    current_value
                    is not None
                ),
                key=(
                    f"{key_prefix}_"
                    f"{code}_enabled"
                ),
                help=(
                    "Este parámetro es opcional. "
                    "Actívalo únicamente si deseas "
                    "establecer un valor explícito."
                ),
            )

        if not enabled:
            continue

        unit = (
            specification.get("unit")
            or specification.get(
                "currency"
            )
        )

        if parameter_type == "number":
            minimum = specification.get(
                "minimum"
            )

            maximum = specification.get(
                "maximum"
            )

            display_label = label

            if unit == "PERCENT":
                display_label = (
                    f"{label} (%)"
                )

            elif unit == "MXN":
                display_label = (
                    f"{label} (MXN)"
                )

            values[code] = st.number_input(
                display_label,
                min_value=(
                    float(minimum)
                    if minimum is not None
                    else None
                ),
                max_value=(
                    float(maximum)
                    if maximum is not None
                    else None
                ),
                value=_number_default(
                    specification=specification,
                    current_value=current_value,
                ),
                step=(
                    0.5
                    if unit == "PERCENT"
                    else 0.01
                ),
                format="%.2f",
                placeholder=(
                    "Introduce el valor aprobado"
                ),
                required=not optional,
                key=(
                    f"{key_prefix}_{code}"
                ),
                help=(
                    help_text
                    + "\n\nLímites permitidos: "
                    + limits_text(
                        specification
                    )
                ),
            )

        elif parameter_type == "integer":
            minimum = specification.get(
                "minimum"
            )

            maximum = specification.get(
                "maximum"
            )

            integer_value = st.number_input(
                label,
                min_value=(
                    int(minimum)
                    if minimum is not None
                    else None
                ),
                max_value=(
                    int(maximum)
                    if maximum is not None
                    else None
                ),
                value=_integer_default(
                    specification=specification,
                    current_value=current_value,
                ),
                step=1,
                placeholder=(
                    "Introduce el valor aprobado"
                ),
                required=not optional,
                key=(
                    f"{key_prefix}_{code}"
                ),
                help=(
                    help_text
                    + "\n\nLímites permitidos: "
                    + limits_text(
                        specification
                    )
                ),
            )

            values[code] = (
                int(integer_value)
                if integer_value is not None
                else None
            )

        elif parameter_type == "boolean":
            boolean_options = [
                True,
                False,
            ]

            boolean_index = None

            if current_value is True:
                boolean_index = 0

            elif current_value is False:
                boolean_index = 1

            values[code] = st.selectbox(
                label,
                boolean_options,
                index=boolean_index,
                format_func=lambda value: (
                    "Sí"
                    if value is True
                    else "No"
                ),
                placeholder=(
                    "Selecciona Sí o No"
                ),
                key=(
                    f"{key_prefix}_{code}"
                ),
                help=(
                    help_text
                    + "\n\nEsta decisión debe "
                    "ser seleccionada "
                    "expresamente."
                ),
            )

        elif parameter_type == "string":
            allowed = (
                specification.get(
                    "allowed"
                )
                or []
            )

            if allowed:
                index = None

                if current_value in allowed:
                    index = allowed.index(
                        current_value
                    )

                values[code] = (
                    st.selectbox(
                        label,
                        allowed,
                        index=index,
                        format_func=(
                            friendly_value
                        ),
                        placeholder=(
                            "Selecciona un valor"
                        ),
                        key=(
                            f"{key_prefix}_{code}"
                        ),
                        help=(
                            help_text
                            + "\n\n"
                            + limits_text(
                                specification
                            )
                        ),
                    )
                )

            else:
                values[code] = (
                    st.text_input(
                        label,
                        value=str(
                            current_value
                            or ""
                        ),
                        key=(
                            f"{key_prefix}_{code}"
                        ),
                        help=help_text,
                    )
                )

        else:
            raise ValueError(
                "UNSUPPORTED_PARAMETER_TYPE:"
                + str(parameter_type)
            )

    return values


PARAMETER_ICONS = {
    "amount": "💰",
    "frequency": "🔄",
    "due_day": "📅",
    "minimum_payment_percentage": "📊",
    "minimum_compliance": "✅",
    "surcharge_percentage": "📈",
    "calculation_base": "🧮",
    "grace_days": "⏳",
    "surcharge_frequency": "🔁",
    "maximum_surcharge_percentage": "🛡️",
    "minimum_coverage_percentage": "📊",
    "tolerance_days": "⏱️",
    "prior_notice_required": "📣",
    "authorization_required": "🔐",
    "operational_action": "⚙️",
}


def parameter_icon(code):
    return PARAMETER_ICONS.get(
        code,
        "⚙️",
    )


def parameter_type_label(
    specification,
):
    specification = (
        specification
        if isinstance(
            specification,
            dict,
        )
        else {}
    )

    parameter_type = (
        specification.get(
            "type",
            "string",
        )
    )

    unit = (
        specification.get("unit")
        or specification.get(
            "currency"
        )
    )

    if unit == "PERCENT":
        return "Porcentaje"

    if unit == "MXN":
        return "Importe monetario"

    labels = {
        "number": "Número decimal",
        "integer": "Número entero",
        "string": "Selección",
        "boolean": "Decisión Sí / No",
    }

    return labels.get(
        parameter_type,
        "Valor configurable",
    )


def render_parameter_definition_cards(
    *,
    schema,
):
    schema = (
        schema
        if isinstance(schema, dict)
        else {}
    )

    if not schema:
        st.info(
            "Esta definición no contiene "
            "parámetros configurables."
        )
        return

    for code, specification in (
        schema.items()
    ):
        specification = (
            specification
            if isinstance(
                specification,
                dict,
            )
            else {}
        )

        label = parameter_label(code)
        help_text = parameter_help(code)
        icon = parameter_icon(code)

        optional = bool(
            specification.get(
                "optional",
                False,
            )
        )

        with st.container(
            border=True
        ):
            title_column, help_column = (
                st.columns(
                    [8, 1],
                    vertical_alignment="center",
                )
            )

            with title_column:
                st.markdown(
                    f"### {icon} {label}"
                )

            with help_column:
                with st.popover(
                    "ⓘ",
                    type="tertiary",
                    help=(
                        "¿Qué significa "
                        "este parámetro?"
                    ),
                ):
                    st.write(help_text)

            st.write(
                "**¿Qué configura?** "
                + help_text
            )

            st.write(
                "**Tipo de valor:** "
                + parameter_type_label(
                    specification
                )
            )

            st.write(
                "**Límites permitidos:** "
                + limits_text(
                    specification
                )
            )

            st.write(
                "**Obligatorio:** "
                + (
                    "No"
                    if optional
                    else "Sí"
                )
            )

            if optional:
                st.caption(
                    "Este parámetro es opcional. "
                    "El administrador puede decidir "
                    "si establece un valor explícito "
                    "en cada versión."
                )

    st.caption(
        "Los límites permitidos determinan qué "
        "valores puede configurar el administrador. "
        "No representan los valores actuales de "
        "ninguna versión."
    )
