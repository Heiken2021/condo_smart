from datetime import date

import pandas as pd
import streamlit as st

from core.authorization import authorize
from views.financial_rule_lifecycle import (
    render_definition_fields,
    render_governance_attributes,
    render_rule_lifecycle_actions,
)
from services.financial_dynamic_parameter_editor import (
    render_parameter_definition_cards,
)
from services.financial_rule_presenter import (
    business_applicability,
    business_priority,
    business_scope,
    business_status,
    configured_parameter_rows,
    parameter_schema_rows,
)
from services.financial_rules_grid import (
    get_financial_rule_detail,
    list_financial_exception_grid,
    list_financial_rule_grid,
    list_space_fee_grid,
)


def _money(value):
    return (
        f"${float(value or 0):,.2f}"
    )


def _date(value):
    if value is None:
        return "Sin límite"

    return value.strftime(
        "%d/%m/%Y"
    )


def _rule_key(row):
    return (
        row["definition_id"],
        row.get("rule_id"),
    )


def _render_rules(
    *,
    property_id,
    user,
):
    st.markdown("### Reglas de negocio")

    st.caption(
        "Reglas compatibles con la naturaleza "
        "del inmueble activo y reglas ya "
        "configuradas dentro de su jerarquía."
    )

    rows = list_financial_rule_grid(
        property_id=property_id,
        user=user,
        include_available=True,
    )

    if not rows:
        st.info(
            "No existen definiciones de reglas "
            "compatibles con este inmueble."
        )
        return

    domain_options = [
        "TODOS",
        *sorted(
            {
                row["dominio_codigo"]
                for row in rows
            }
        ),
    ]

    status_options = [
        "TODOS",
        *sorted(
            {
                row["status"]
                for row in rows
            }
        ),
    ]

    scope_options = [
        "TODOS",
        *sorted(
            {
                row["scope"]
                for row in rows
            }
        ),
    ]

    filter_1, filter_2, filter_3 = (
        st.columns(3)
    )

    with filter_1:
        selected_domain = st.selectbox(
            "Dominio",
            domain_options,
            key=(
                f"governance_rule_domain_"
                f"{property_id}"
            ),
        )

    with filter_2:
        selected_status = st.selectbox(
            "Estado",
            status_options,
            key=(
                f"governance_rule_status_"
                f"{property_id}"
            ),
        )

    with filter_3:
        selected_scope = st.selectbox(
            "Alcance",
            scope_options,
            key=(
                f"governance_rule_scope_"
                f"{property_id}"
            ),
        )

    filtered = [
        row
        for row in rows
        if (
            selected_domain == "TODOS"
            or row["dominio_codigo"]
               == selected_domain
        )
        and (
            selected_status == "TODOS"
            or row["status"]
               == selected_status
        )
        and (
            selected_scope == "TODOS"
            or row["scope"]
               == selected_scope
        )
    ]

    if not filtered:
        st.info(
            "No hay reglas que coincidan "
            "con los filtros seleccionados."
        )
        return

    display = pd.DataFrame(
        [
            {
                "Regla": (
                    row["display_name"]
                ),
                "Código": (
                    row["display_code"]
                ),
                "Dominio": (
                    row["dominio_codigo"]
                ),
                "Aplicabilidad": (
                    business_applicability(
                        row[
                            "applicability_label"
                        ]
                    )
                ),
                "Nivel de aplicación": (
                    business_scope(
                        row["scope"]
                    )
                ),
                "Aplica en": (
                    row["scope_label"]
                    or "—"
                ),
                "Versión": (
                    row["version_label"]
                ),
                "Desde": (
                    _date(
                        row["vigente_desde"]
                    )
                    if row["vigente_desde"]
                    is not None
                    else "—"
                ),
                "Hasta": (
                    _date(
                        row["vigente_hasta"]
                    )
                    if row["vigente_hasta"]
                    is not None
                    else "Sin fecha de término"
                ),
                "Estado": (
                    business_status(
                        row["status"]
                    )
                ),
                "Herencia permitida": (
                    "Sí"
                    if row[
                        "inheritance_label"
                    ] == "Hereda"
                    else "No"
                ),
                "Tipo de configuración": (
                    row["override_label"]
                    or "—"
                ),
                "Prioridad": (
                    business_priority(
                        row.get("prioridad")
                    )
                ),
            }
            for row in filtered
        ]
    )

    event = st.dataframe(
        display,
        hide_index=True,
        use_container_width=True,
        selection_mode="single-row",
        on_select="rerun",
        key=(
            f"governance_rules_grid_"
            f"{property_id}"
        ),
        column_config={
            "Desde": st.column_config.TextColumn(
                "Desde",
            ),
            "Hasta": st.column_config.TextColumn(
                "Hasta",
            ),
        },
    )

    selected_rows = (
        event.selection.rows
        if event
        and event.selection
        else []
    )

    if selected_rows:
        selected_index = (
            selected_rows[0]
        )

        selected = filtered[
            selected_index
        ]

        st.session_state[
            f"selected_financial_rule_"
            f"{property_id}"
        ] = _rule_key(selected)

    selected_key = st.session_state.get(
        f"selected_financial_rule_"
        f"{property_id}"
    )

    if not selected_key:
        st.info(
            "Selecciona una regla en el grid "
            "para consultar su ficha."
        )
        return

    definition_id, rule_id = (
        selected_key
    )

    detail = get_financial_rule_detail(
        property_id=property_id,
        user=user,
        definition_id=definition_id,
        rule_id=rule_id,
    )

    if not detail:
        st.warning(
            "La regla seleccionada ya no "
            "está disponible."
        )
        return

    st.divider()
    st.markdown("### Ficha de la regla")

    state_col, scope_col, intel_col = (
        st.columns(3)
    )

    with state_col:
        st.metric(
            "Estado",
            business_status(
                detail["status"]
            ),
        )

    with scope_col:
        st.metric(
            "Alcance",
            business_scope(
                detail["scope"]
            ),
        )

    with intel_col:
        enabled = []

        if detail["kpi_enabled"]:
            enabled.append("KPI")

        if detail["ai_enabled"]:
            enabled.append("IA")

        st.metric(
            "Contexto",
            " + ".join(enabled)
            or "No configurado",
        )

    (
        definition_tab,
        configuration_tab,
        version_tab,
        governance_tab,
    ) = (
        st.tabs(
            [
                "Definición",
                "Configuración",
                "Versiones",
                "Gobierno y auditoría",
            ]
        )
    )

    with definition_tab:
        render_definition_fields(
            detail
        )

        st.write(
            "**Descripción:**",
            detail.get(
                "display_description"
            )
            or "Sin descripción.",
        )

        st.markdown(
            "#### Parámetros configurables"
        )

        st.caption(
            "Estos parámetros determinan cómo "
            "puede configurarse la regla. "
            "Los valores concretos serán "
            "decididos por el administrador "
            "al crear una versión."
        )

        schema = (
            detail.get(
                "esquema_parametros"
            )
            or {}
        )

        render_parameter_definition_cards(
            schema=schema,
        )

        st.caption(
            "La estructura técnica de estos "
            "parámetros es administrada "
            "internamente por Condo_Smart y no "
            "se muestra ni se edita como código."
        )


    with configuration_tab:
        st.markdown(
            "#### Configuración de la regla"
        )

        versions = (
            detail.get("versions")
            or []
        )

        if not versions:
            st.info(
                "Esta regla todavía no tiene "
                "una configuración creada."
            )

            st.caption(
                "Selecciona **Nueva regla** "
                "para crear la configuración "
                "en el inmueble. Después podrás "
                "crear su primera versión y "
                "establecer los valores concretos "
                "de sus parámetros configurables."
            )

        else:
            selected_version = versions[0]

            configured_rows = (
                configured_parameter_rows(
                    detail.get(
                        "esquema_parametros"
                    )
                    or {},
                    selected_version.get(
                        "parametros"
                    )
                    or {},
                )
            )

            if configured_rows:
                st.dataframe(
                    pd.DataFrame(
                        configured_rows
                    ),
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                st.info(
                    "La versión seleccionada "
                    "no contiene valores "
                    "configurados."
                )

            st.caption(
                "Los valores de configuración "
                "pertenecen a una versión. "
                "Una versión aprobada no se "
                "modifica destructivamente; "
                "los cambios se realizan creando "
                "una nueva versión."
            )


    with version_tab:
        versions = detail[
            "versions"
        ]

        if not versions:
            st.info(
                "La regla todavía no tiene "
                "versiones configuradas."
            )
        else:
            version_dataframe = pd.DataFrame(
                [
                    {
                        "Versión": (
                            f"v"
                            f"{version['version_num']}"
                        ),
                        "Estado": (
                            business_status(
                                version[
                                    "estado_codigo"
                                ]
                            )
                        ),
                        "Desde": (
                            _date(
                                version[
                                    "vigente_desde"
                                ]
                            )
                            if version[
                                "vigente_desde"
                            ] is not None
                            else "—"
                        ),
                        "Hasta": (
                            _date(
                                version[
                                    "vigente_hasta"
                                ]
                            )
                            if version[
                                "vigente_hasta"
                            ] is not None
                            else "Sin fecha de término"
                        ),
                        "Aprobada": (
                            version[
                                "aprobado_en"
                            ].strftime(
                                "%d/%m/%Y %H:%M"
                            )
                            if version[
                                "aprobado_en"
                            ] is not None
                            else "—"
                        ),
                        "Motivo": (
                            version[
                                "motivo_cambio"
                            ]
                        ),
                    }
                    for version in versions
                ]
            )

            st.dataframe(
                version_dataframe,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Desde": (
                        st.column_config.DateColumn(
                            "Desde",
                            format="DD/MM/YYYY",
                        )
                    ),
                    "Hasta": (
                        st.column_config.DateColumn(
                            "Hasta",
                            format="DD/MM/YYYY",
                        )
                    ),
                },
            )

            selected_version = versions[0]

            st.markdown(
                "#### Valores de la versión"
            )

            configured_rows = (
                configured_parameter_rows(
                    detail.get(
                        "esquema_parametros"
                    )
                    or {},
                    selected_version.get(
                        "parametros"
                    )
                    or {},
                )
            )

            if configured_rows:
                st.dataframe(
                    pd.DataFrame(
                        configured_rows
                    ),
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                st.info(
                    "La versión no contiene "
                    "valores configurados."
                )

    with governance_tab:
        render_governance_attributes(
            detail
        )

        exceptions = detail[
            "exceptions"
        ]

        if not exceptions:
            st.info(
                "No hay excepciones asociadas."
            )
        else:
            st.dataframe(
                pd.DataFrame(exceptions),
                hide_index=True,
                use_container_width=True,
            )

    st.divider()

    render_rule_lifecycle_actions(
        property_id=property_id,
        user=user,
        detail=detail,
    )


def _render_fees(
    *,
    property_id,
    user,
    spaces,
):
    st.markdown("### Cuotas")

    rows = list_space_fee_grid(
        property_id=property_id,
        user=user,
    )

    if rows:
        dataframe = pd.DataFrame(
            [
                {
                    "ID": row["id"],
                    "Espacio": (
                        row["space_key"]
                    ),
                    "Nombre": (
                        row["space_name"]
                    ),
                    "Estructura": (
                        row["structure_name"]
                    ),
                    "Tipo": (
                        row[
                            "tipo_cuota_codigo"
                        ]
                    ),
                    "Importe": float(
                        row["monto_mxn"]
                    ),
                    "Desde": (
                        row["vigente_desde"]
                    ),
                    "Hasta": (
                        row["vigente_hasta"]
                    ),
                    "Estado": (
                        row["estado_codigo"]
                    ),
                    "Origen": (
                        row["origen_codigo"]
                    ),
                    "Regla": (
                        row["rule_name"]
                        or "Sin regla asociada"
                    ),
                }
                for row in rows
            ]
        )

        st.dataframe(
            dataframe,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Importe": (
                    st.column_config.NumberColumn(
                        "Importe",
                        format="$%.2f",
                    )
                ),
                "Desde": (
                    st.column_config.DateColumn(
                        "Desde",
                        format="DD/MM/YYYY",
                    )
                ),
                "Hasta": (
                    st.column_config.DateColumn(
                        "Hasta",
                        format="DD/MM/YYYY",
                    )
                ),
            },
        )
    else:
        st.info(
            "No existen cuotas configuradas."
        )

    st.caption(
        "El histórico muestra todas las "
        "vigencias registradas. La cuota "
        "actual de 4A debe aparecer como "
        "ID 2, aprobada y sin regla asociada."
    )

    st.divider()
    st.markdown("### Nueva cuota")

    actor_id = user.get("id")

    if not actor_id:
        st.warning(
            "No se pudo identificar "
            "al usuario activo."
        )
        return

    decision = authorize(
        user,
        "FINANZAS_CUOTA_GESTIONAR",
        property_id,
    )

    if not decision.allowed:
        st.info(
            "El usuario no tiene permiso "
            "para gestionar cuotas."
        )
        return

    if not spaces:
        st.info(
            "No hay espacios disponibles."
        )
        return

    labels = list(spaces)

    selected_label = st.selectbox(
        "Espacio",
        labels,
        key=(
            f"governance_fee_space_"
            f"{property_id}"
        ),
    )

    selected_space = spaces[
        selected_label
    ]

    fee_type = st.selectbox(
        "Tipo de cuota",
        [
            "MANTENIMIENTO_ORDINARIO",
        ],
        key=(
            f"governance_fee_type_"
            f"{property_id}"
        ),
    )

    amount = st.number_input(
        "Importe mensual (MXN)",
        min_value=0.01,
        value=500.00,
        step=50.00,
        format="%.2f",
        key=(
            f"governance_fee_amount_"
            f"{property_id}"
        ),
    )

    effective_from = st.date_input(
        "Vigente desde",
        value=date.today(),
        key=(
            f"governance_fee_from_"
            f"{property_id}"
        ),
    )

    reason = st.text_input(
        "Motivo de configuración",
        value=(
            "Configuración de cuota "
            "de mantenimiento"
        ),
        key=(
            f"governance_fee_reason_"
            f"{property_id}"
        ),
    )

    st.button(
        "Crear cuota en borrador",
        type="primary",
        disabled=True,
        help=(
            "Temporalmente deshabilitado "
            "hasta finalizar la consola "
            "de reglas y validar la "
            "vinculación rule_version_id."
        ),
        key=(
            f"governance_fee_create_"
            f"{property_id}"
        ),
    )

    st.warning(
        "La creación de nuevas cuotas está "
        "temporalmente bloqueada. Primero "
        "debe configurarse y aprobarse la "
        "regla que servirá como origen."
    )


def _render_exceptions(
    *,
    property_id,
    user,
):
    st.markdown("### Excepciones")

    rows = (
        list_financial_exception_grid(
            property_id=property_id,
            user=user,
        )
    )

    if not rows:
        st.info(
            "No existen excepciones "
            "financieras registradas."
        )
        return

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
    )


def render_governance_section(
    *,
    property_id,
    user,
    spaces,
):
    st.subheader("Gobierno Financiero")

    st.caption(
        "Consola de reglas, cuotas y "
        "excepciones del inmueble activo."
    )

    rule_tab, fee_tab, exception_tab = (
        st.tabs(
            [
                "Reglas",
                "Cuotas",
                "Excepciones",
            ]
        )
    )

    with rule_tab:
        try:
            _render_rules(
                property_id=property_id,
                user=user,
            )
        except PermissionError as exc:
            st.warning(
                "Sin permiso para consultar "
                f"el Gobierno Financiero: {exc}"
            )

    with fee_tab:
        try:
            _render_fees(
                property_id=property_id,
                user=user,
                spaces=spaces,
            )
        except PermissionError as exc:
            st.warning(
                "Sin permiso para consultar "
                f"las cuotas: {exc}"
            )

    with exception_tab:
        try:
            _render_exceptions(
                property_id=property_id,
                user=user,
            )
        except PermissionError as exc:
            st.warning(
                "Sin permiso para consultar "
                f"las excepciones: {exc}"
            )
