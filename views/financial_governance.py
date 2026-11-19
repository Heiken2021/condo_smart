from datetime import date

import pandas as pd
import altair as alt
import streamlit as st

from core.authorization import authorize
from views.financial_rule_visual_builder import render_rule_visual_builder
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
from services.financial_governance_commands import (
    create_financial_rule_definition,
    set_financial_rule_applicability,
)
from services.financial_rules_grid import (
    get_financial_rule_detail,
    list_global_financial_rule_catalog,
    suggest_financial_rule_code,
    list_financial_exception_grid,
    list_financial_rule_grid,
    list_space_fee_grid,
)


def _money(value):
    return (
        f"${float(value or 0):,.2f}"
    )


def _semantic_status(value):
    raw = str(value or "").upper()
    label = business_status(value)
    if raw in {"APROBADO", "APROBADA", "VIGENTE", "ACTIVO", "ACTIVA"}:
        return f"🟢 {label}"
    if raw in {"BORRADOR", "PENDIENTE", "SIN_CONFIGURAR", "SIN_VERSION"}:
        return f"🟠 {label}"
    if raw in {"BLOQUEADO", "BLOQUEADA", "VENCIDO", "VENCIDA", "RECHAZADO", "RECHAZADA"}:
        return f"🔴 {label}"
    return f"⚪ {label}"


def _semantic_origin(value):
    label = str(value or "Sin configurar")
    upper = label.upper()
    if "HERED" in upper:
        return f"🟣 {label}"
    if "GLOBAL" in upper or "CATÁLOGO" in upper:
        return f"🔵 {label}"
    if "PROPIA" in upper:
        return f"🟢 {label}"
    if "MODIFICADA" in upper or "OVERRIDE" in upper:
        return f"🟠 {label}"
    return f"⚪ {label}"


def _semantic_assignment(value, compatible=True):
    label = str(value or "Sin configurar")
    upper = label.upper()
    if not compatible or "NO COMPATIBLE" in upper:
        return f"🔴 {label}"
    if "HERED" in upper:
        return f"🟣 {label}"
    if "DISPONIBLE" in upper:
        return f"🔵 {label}"
    if "PROPIA" in upper:
        return f"🟢 {label}"
    if "MODIFICADA" in upper or "OVERRIDE" in upper:
        return f"🟠 {label}"
    return f"⚪ {label}"


def _semantic_applicability(value, compatible=True):
    label = business_applicability(value)
    if not compatible:
        return f"🔴 {label}"
    if str(value or "").upper() == "GENERAL":
        return f"🔵 {label}"
    return f"🟢 {label}"


def _semantic_priority(value):
    label = business_priority(value)
    upper = str(label or "").upper()
    if "CRÍTICA" in upper or "CRITICA" in upper:
        return f"🔴 {label}"
    if "ALTA" in upper:
        return f"🟠 {label}"
    if "NORMAL" in upper:
        return f"🔵 {label}"
    return f"⚪ {label}"


def _visual_semantics_legend():
    st.caption(
        "Semáforo operativo: 🟢 Correcto · 🟠 Requiere atención · 🔴 Incidencia. "
        "Contexto: Global / catálogo · Heredado · Sin configurar / no aplica."
    )


def _context_label(value):
    return str(value or "Sin configurar")


def _count_by(rows, key, empty_label="Sin definir"):
    counts = {}
    for row in rows:
        value = row.get(key) or empty_label
        counts[str(value)] = counts.get(str(value), 0) + 1
    return counts


def _chart_theme(chart, height=250):
    return (
        chart.properties(height=height)
        .configure_view(stroke=None)
        .configure_axis(
            gridColor="#E8EEF5",
            domain=False,
            tickColor="#CBD5E1",
            labelColor="#475569",
            titleColor="#334155",
        )
        .configure_legend(
            labelColor="#475569",
            titleColor="#334155",
            orient="bottom",
        )
    )


def _donut_chart(labels, values, colors, title):
    frame = pd.DataFrame({"Categoría": labels, "Reglas": values})
    chart = (
        alt.Chart(frame)
        .mark_arc(innerRadius=62, outerRadius=98, cornerRadius=5)
        .encode(
            theta=alt.Theta("Reglas:Q", stack=True),
            color=alt.Color(
                "Categoría:N",
                scale=alt.Scale(domain=labels, range=colors),
                legend=alt.Legend(title=None),
            ),
            tooltip=["Categoría:N", "Reglas:Q"],
        )
        .properties(title=title)
    )
    st.altair_chart(_chart_theme(chart, height=260), use_container_width=True)


def _horizontal_bar(counts, title, color="#2563EB"):
    if not counts:
        return
    frame = pd.DataFrame(
        [{"Categoría": key, "Reglas": value} for key, value in counts.items()]
    ).sort_values("Reglas", ascending=False)
    chart = (
        alt.Chart(frame)
        .mark_bar(cornerRadiusEnd=6, size=20, color=color)
        .encode(
            x=alt.X("Reglas:Q", title="Reglas", axis=alt.Axis(tickMinStep=1)),
            y=alt.Y("Categoría:N", sort="-x", title=None),
            tooltip=["Categoría:N", "Reglas:Q"],
        )
        .properties(title=title)
    )
    labels = chart.mark_text(align="left", baseline="middle", dx=5, color="#334155").encode(
        text=alt.Text("Reglas:Q", format="d")
    )
    st.altair_chart(_chart_theme(chart + labels, height=max(220, 30 * len(frame))), use_container_width=True)


def _status_stack(rows):
    if not rows:
        return
    data = []
    for row in rows:
        status = str(row.get("status") or "SIN_CONFIGURAR").upper()
        if status in {"APROBADO", "APROBADA", "VIGENTE", "ACTIVO", "ACTIVA"}:
            health = "Correcto"
        elif status in {"BLOQUEADO", "BLOQUEADA", "VENCIDO", "VENCIDA", "RECHAZADO", "RECHAZADA"}:
            health = "Incidencia"
        else:
            health = "Atención"
        data.append({"Dominio": row.get("dominio_codigo") or "Sin definir", "Salud": health})
    frame = pd.DataFrame(data).groupby(["Dominio", "Salud"]).size().reset_index(name="Reglas")
    chart = (
        alt.Chart(frame)
        .mark_bar(cornerRadius=3)
        .encode(
            y=alt.Y("Dominio:N", title=None),
            x=alt.X("Reglas:Q", stack="normalize", title="Composición", axis=alt.Axis(format="%")),
            color=alt.Color(
                "Salud:N",
                scale=alt.Scale(
                    domain=["Correcto", "Atención", "Incidencia"],
                    range=["#22C55E", "#F59E0B", "#EF4444"],
                ),
                legend=alt.Legend(title=None),
            ),
            tooltip=["Dominio:N", "Salud:N", "Reglas:Q"],
        )
        .properties(title="Mapa de salud por dominio")
    )
    st.altair_chart(_chart_theme(chart, height=max(250, 32 * frame["Dominio"].nunique())), use_container_width=True)


def _priority_chart(rows):
    counts = {}
    for row in rows:
        label = business_priority(row.get("prioridad")) if row.get("prioridad") else "Sin definir"
        counts[label] = counts.get(label, 0) + 1
    if not counts:
        return
    order = ["Crítica", "Alta", "Normal", "Baja", "Sin definir"]
    colors = ["#DC2626", "#F59E0B", "#2563EB", "#60A5FA", "#CBD5E1"]
    frame = pd.DataFrame([{"Prioridad": k, "Reglas": v} for k, v in counts.items()])
    chart = (
        alt.Chart(frame)
        .mark_bar(cornerRadiusEnd=6, size=24)
        .encode(
            x=alt.X("Reglas:Q", title="Reglas", axis=alt.Axis(tickMinStep=1)),
            y=alt.Y("Prioridad:N", sort=order, title=None),
            color=alt.Color("Prioridad:N", scale=alt.Scale(domain=order, range=colors), legend=None),
            tooltip=["Prioridad:N", "Reglas:Q"],
        )
        .properties(title="Prioridad de las reglas")
    )
    st.altair_chart(_chart_theme(chart, height=250), use_container_width=True)


def _timeline_chart(rows):
    timeline=[]
    for row in rows:
        start=row.get("vigente_desde")
        if not start:
            continue
        end=row.get("vigente_hasta")
        status=str(row.get("status") or "SIN_CONFIGURAR").upper()
        if status in {"APROBADO","APROBADA","VIGENTE","ACTIVO","ACTIVA"}:
            health="Correcto"
        elif status in {"BLOQUEADO","BLOQUEADA","VENCIDO","VENCIDA","RECHAZADO","RECHAZADA"}:
            health="Incidencia"
        else:
            health="Atención"
        timeline.append({
            "Regla": row.get("display_name") or row.get("display_code") or "Regla",
            "Desde": start,
            "Hasta": end,
            "HastaVisual": end or date.today(),
            "Vigencia": "Abierta" if end is None else "Definida",
            "Estado": business_status(row.get("status")),
            "Prioridad": business_priority(row.get("prioridad")) if row.get("prioridad") else "Sin definir",
            "Versión": row.get("version_label") or "Sin versión",
            "Salud": health,
        })
    st.markdown("##### Timeline de vigencias")
    if not timeline:
        st.info("No hay reglas con fecha Desde para representar en la línea temporal con los filtros actuales.")
        return
    frame=pd.DataFrame(timeline)
    chart=(
        alt.Chart(frame)
        .mark_bar(cornerRadius=5, size=17)
        .encode(
            x=alt.X("Desde:T", title="Vigencia", axis=alt.Axis(format="%d/%m/%Y")),
            x2="HastaVisual:T",
            y=alt.Y("Regla:N", sort=alt.SortField(field="Desde", order="descending"), title=None),
            color=alt.Color(
                "Salud:N",
                scale=alt.Scale(domain=["Correcto","Atención","Incidencia"], range=["#22C55E","#F59E0B","#EF4444"]),
                legend=alt.Legend(title="Estado operativo"),
            ),
            opacity=alt.condition(alt.datum.Vigencia == "Abierta", alt.value(0.72), alt.value(1.0)),
            tooltip=[
                alt.Tooltip("Regla:N"), alt.Tooltip("Estado:N"), alt.Tooltip("Prioridad:N"),
                alt.Tooltip("Versión:N"), alt.Tooltip("Desde:T", format="%d/%m/%Y"),
                alt.Tooltip("Hasta:T", format="%d/%m/%Y"), alt.Tooltip("Vigencia:N"),
            ],
        )
        .properties(title="Desde → Hasta · Las vigencias abiertas se extienden visualmente hasta hoy")
    )
    st.altair_chart(_chart_theme(chart, height=max(260, 30*len(frame))), use_container_width=True)
    st.caption("Las reglas sin fecha Hasta conservan su vigencia abierta; la fecha actual se usa sólo como extremo visual del timeline.")


def _render_governance_dashboard(*, property_id, user, property_rows):
    st.divider()
    st.markdown("#### Dashboard ejecutivo de Gobierno Financiero")
    st.caption(
        "Vista ejecutiva de sólo lectura. Resume catálogo, compatibilidad, configuración, "
        "versionado y atención requerida con el mismo modelo filtrado de los grids."
    )

    catalog = list_global_financial_rule_catalog(property_id=property_id, user=user)
    global_tab, property_tab = st.tabs(["Gobierno global", "Inmueble activo"])

    with global_tab:
        total = len(catalog)
        active = sum(1 for row in catalog if row.get("activo"))
        compatible = sum(1 for row in catalog if row.get("compatible"))
        incompatible = total - compatible
        health = round((compatible / total) * 100) if total else 0
        configured = sum(1 for row in catalog if not row.get("can_adopt") and row.get("compatible"))

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Reglas", total)
        c2.metric("Activas", active)
        c3.metric("Compatibles", compatible)
        c4.metric("No compatibles", incompatible)
        c5.metric("Cobertura compatible", f"{health}%")

        left, right = st.columns([0.9, 1.6])
        with left:
            _donut_chart(
                ["Compatibles", "No compatibles"],
                [compatible, incompatible],
                ["#22C55E", "#EF4444"],
                "Compatibilidad del catálogo",
            )
        with right:
            _horizontal_bar(_count_by(catalog, "dominio_codigo"), "Reglas por dominio")

        lower_left, lower_right = st.columns(2)
        with lower_left:
            _horizontal_bar(
                _count_by(catalog, "assignment_label"),
                "Relación con el inmueble activo",
                color="#4F46E5",
            )
        with lower_right:
            assignment_total = len(catalog)
            available = sum(1 for row in catalog if row.get("can_adopt"))
            related = max(0, assignment_total - available - incompatible)
            _donut_chart(
                ["Relacionadas", "Disponibles", "No compatibles"],
                [related, available, incompatible],
                ["#2563EB", "#F59E0B", "#EF4444"],
                "Cobertura sobre el inmueble",
            )

        if incompatible:
            st.warning(f"Atención global: {incompatible} regla(s) del catálogo no son compatibles con el inmueble activo.")
        elif total:
            st.success("El catálogo visible no presenta incompatibilidades con el inmueble activo.")

    with property_tab:
        total = len(property_rows)
        configured = sum(1 for row in property_rows if row.get("configured"))
        unconfigured = total - configured
        with_version = sum(1 for row in property_rows if row.get("current_version_id"))
        pending = sum(
            1 for row in property_rows
            if str(row.get("status") or "").upper()
            in {"BORRADOR", "PENDIENTE", "SIN_CONFIGURAR", "SIN_VERSION"}
        )
        incidents = sum(
            1 for row in property_rows
            if str(row.get("status") or "").upper()
            in {"BLOQUEADO", "BLOQUEADA", "VENCIDO", "VENCIDA", "RECHAZADO", "RECHAZADA"}
        )
        coverage = round((configured / total) * 100) if total else 0

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Reglas visibles", total)
        c2.metric("Configuradas", configured)
        c3.metric("Con versión", with_version)
        c4.metric("Requieren atención", pending + incidents)
        c5.metric("Cobertura configurada", f"{coverage}%")

        left, right = st.columns([0.9, 1.6])
        with left:
            _donut_chart(
                ["Configuradas", "Sin configurar"],
                [configured, unconfigured],
                ["#22C55E", "#CBD5E1"],
                "Cobertura de configuración",
            )
        with right:
            _status_stack(property_rows)

        lower_left, lower_right = st.columns(2)
        with lower_left:
            _horizontal_bar(_count_by(property_rows, "status"), "Estado del gobierno", color="#0F766E")
        with lower_right:
            _priority_chart(property_rows)

        _timeline_chart(property_rows)

        with st.expander("Origen de la configuración", expanded=False):
            _horizontal_bar(_count_by(property_rows, "origin_label"), "Origen de la configuración", color="#7C3AED")

        attention = [
            row for row in property_rows
            if not row.get("configured")
            or not row.get("current_version_id")
            or str(row.get("status") or "").upper()
               in {"BORRADOR", "PENDIENTE", "BLOQUEADO", "BLOQUEADA", "VENCIDO", "VENCIDA", "RECHAZADO", "RECHAZADA"}
        ]
        st.markdown("##### Atención prioritaria")
        if attention:
            st.dataframe(
                pd.DataFrame([
                    {
                        "Semáforo": _semantic_status(row.get("status")),
                        "Regla": row.get("display_name"),
                        "Estado": business_status(row.get("status")),
                        "Origen": _context_label(row.get("origin_label")),
                        "Versión": row.get("version_label") or "Sin versión",
                    }
                    for row in attention
                ]),
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.success("No hay reglas que requieran atención con los filtros actuales.")

def _date(value):
    if value is None:
        return "Sin límite"

    return value.strftime(
        "%d/%m/%Y"
    )


def _suggest_business_code(value):
    import re
    import unicodedata

    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^A-Za-z0-9]+", "_", text.upper()).strip("_")
    return text[:100]


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

    _render_dynamic_rule_catalog(property_id=property_id, user=user)

    st.divider()
    st.markdown("#### Configuración del inmueble")

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
            "Actualmente no hay reglas compatibles asignables para esta tipología. "
            "Puedes crear una nueva regla global, ampliar la aplicabilidad de una regla "
            "existente o crear una regla propia para este inmueble."
        )
        return

    domain_options = [
        "TODOS",
        *sorted(
            {
                row.get("dominio_codigo")
                for row in rows
                if isinstance(row.get("dominio_codigo"), str)
                and row.get("dominio_codigo").strip()
            }
        ),
    ]

    status_options = [
        "TODOS",
        *sorted(
            {
                row.get("status")
                for row in rows
                if isinstance(row.get("status"), str)
                and row.get("status").strip()
            }
        ),
    ]

    scope_options = [
        "TODOS",
        *sorted(
            {
                row.get("scope")
                for row in rows
                if isinstance(row.get("scope"), str)
                and row.get("scope").strip()
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
                "Origen": _context_label(row.get("origin_label")),
                "Aplicabilidad": business_applicability(row["applicability_label"]),
                "Nivel de aplicación": (
                    business_scope(row["scope"])
                    if row.get("configured")
                    else "—"
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
                "Estado": _semantic_status(row["status"]),
                "Herencia permitida": (
                    "Por definir"
                    if not row.get("configured")
                    else (
                        "Sí"
                        if row["inheritance_label"] == "Hereda"
                        else "No"
                    )
                ),
                "Tipo de configuración": _context_label(row.get("override_label")),
                "Prioridad": business_priority(row.get("prioridad")) if row.get("prioridad") else "—",
            }
            for row in filtered
        ]
    )

    _visual_semantics_legend()
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

    _render_governance_dashboard(
        property_id=property_id,
        user=user,
        property_rows=filtered,
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

    if st.session_state.pop(f"assignment_flow_notice_{property_id}", False):
        st.success(
            "Asignación iniciada. Revisa y confirma la configuración del inmueble; "
            "todavía no se ha creado ninguna versión."
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

    rule_tab, visual_builder_tab, fee_tab, exception_tab = (
        st.tabs(
            [
                "Reglas",
                "Rule Visual Builder",
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

    with visual_builder_tab:
        try:
            render_rule_visual_builder(
                property_id=property_id,
                user=user,
            )
        except PermissionError as exc:
            st.warning(
                "Sin permiso para consultar "
                f"Rule Visual Builder: {exc}"
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

def _render_dynamic_rule_catalog(*, property_id, user):
    st.markdown("#### Catálogo y asignación de reglas")
    st.caption(
        "Consulta las reglas disponibles en Condo_Smart, su compatibilidad y "
        "la forma en que se aplican al inmueble activo."
    )

    catalog = list_global_financial_rule_catalog(
        property_id=property_id,
        user=user,
    )

    if catalog:
        catalog_display = pd.DataFrame([
            {
                "Regla": row["definition_name"],
                "Código": row["definition_code"],
                "Origen": _context_label(row["origin_label"]),
                "Disponible para": business_applicability(row["applicability_label"]),
                "Asignación al inmueble": _context_label(row["assignment_label"]),
                "Semáforo": ("🔴 No compatible" if not row["compatible"] else ("🟢 Operativa" if row["activo"] else "🟠 Inactiva")),
                "Estado": "Activa" if row["activo"] else "Inactiva",
            }
            for row in catalog
        ])
        _visual_semantics_legend()
        catalog_event = st.dataframe(
            catalog_display,
            hide_index=True,
            use_container_width=True,
            selection_mode="single-row",
            on_select="rerun",
            key=f"global_rule_catalog_grid_{property_id}",
        )
        selected_rows = (
            catalog_event.selection.rows
            if catalog_event and catalog_event.selection
            else []
        )
        if selected_rows:
            selected = catalog[selected_rows[0]]
            st.session_state[f"selected_global_catalog_rule_{property_id}"] = selected["definition_id"]
    else:
        st.info("El catálogo global todavía no contiene definiciones activas.")

    action_left, action_right = st.columns(2)
    with action_left:
        new_global = st.button(
            "+ Nueva regla global",
            type="primary",
            key=f"new_global_definition_{property_id}",
        )
    with action_right:
        new_property = st.button(
            "+ Nueva regla propia del inmueble",
            key=f"new_property_definition_{property_id}",
        )

    action_key=f"new_rule_business_action_{property_id}"
    if new_global:
        st.session_state[action_key]="GLOBAL"
    if new_property:
        st.session_state[action_key]="INMUEBLE"

    selected_definition_id=st.session_state.get(f"selected_global_catalog_rule_{property_id}")
    selected=next((row for row in catalog if row["definition_id"]==selected_definition_id),None)
    if selected:
        st.markdown("##### Acciones de la regla seleccionada")
        st.write(f"**{selected['definition_name']}** · {selected['assignment_label']}")

        is_global_admin = user.get("rol_global") in {"ROOT", "SUPERADMIN"}
        if is_global_admin:
            with st.expander("Administrar disponibilidad", expanded=False):
                st.caption(
                    "Define en qué tipos de inmueble puede utilizarse esta plantilla global. "
                    "Esto no asigna ni crea una regla en ningún inmueble."
                )
                property_type_options={
                    "Fraccionamiento": "FRACCIONAMIENTO",
                    "Plaza comercial": "PLAZA_COMERCIAL",
                    "Condominio vertical": "VERTICAL",
                }
                applicability_text=str(selected.get("applicability_label") or "")
                current_labels=[
                    label for label, code in property_type_options.items()
                    if f"TIPO_INMUEBLE:{code}" in applicability_text
                ]
                with st.form(
                    f"template_availability_{property_id}_{selected['definition_id']}",
                    enter_to_submit=False,
                ):
                    selected_labels=st.multiselect(
                        "Tipos de inmueble permitidos",
                        list(property_type_options),
                        default=current_labels,
                        help=(
                            "Selecciona uno o varios tipos. Los cambios controlan la "
                            "disponibilidad de la plantilla en el catálogo y el Workflow."
                        ),
                    )
                    save_availability=st.form_submit_button(
                        "Guardar disponibilidad", type="primary"
                    )
                if save_availability:
                    selected_codes={property_type_options[label] for label in selected_labels}
                    if not selected_codes:
                        st.error("Selecciona al menos un tipo de inmueble.")
                    else:
                        for property_type_code in property_type_options.values():
                            set_financial_rule_applicability(
                                property_id=property_id,
                                definition_id=selected["definition_id"],
                                dimension_code="TIPO_INMUEBLE",
                                value_code=property_type_code,
                                included=(property_type_code in selected_codes),
                                actor_id=user["id"],
                            )
                        st.success("Disponibilidad actualizada. El catálogo y el Workflow usarán esta configuración.")
                        st.rerun()
        if selected["can_adopt"]:
            st.info("Esta regla está disponible para el inmueble y todavía no está asignada.")
            if st.button("Asignar a este inmueble", type="primary", key=f"assign_catalog_rule_{property_id}_{selected['definition_id']}"):
                st.session_state[f"selected_financial_rule_{property_id}"] = (selected["definition_id"], None)
                st.session_state[f"governance_rule_action_{property_id}"] = "CREATE_RULE"
                st.session_state[f"assignment_flow_notice_{property_id}"] = True
                st.session_state[f"assignment_from_catalog_{property_id}"] = True
                st.session_state[f"rule_new_scope_{property_id}"] = "INMUEBLE"
                st.rerun()
        elif selected["can_override"]:
            st.info("La regla ya tiene una configuración heredada o existente y admite una especialización para este inmueble.")
            if st.button("Configurar para este inmueble", key=f"override_catalog_rule_{property_id}_{selected['definition_id']}"):
                st.session_state[f"selected_financial_rule_{property_id}"] = (selected["definition_id"], selected.get("rule_id"))
                st.info("Continúa en Configuración del inmueble para revisar la ficha y las acciones gobernadas disponibles.")
        elif not selected["compatible"]:
            st.warning("Esta regla no es compatible con la tipología del inmueble activo.")
            st.caption("La aplicabilidad sólo puede modificarse desde el gobierno global del catálogo y con los permisos correspondientes.")
        else:
            st.info("Consulta Configuración del inmueble para revisar versiones, vigencia, auditoría y acciones disponibles.")

    mode=st.session_state.get(action_key)
    if not mode:
        return

    title=("Nueva regla global" if mode=="GLOBAL" else "Nueva regla propia del inmueble")
    with st.expander(title, expanded=True):
        st.caption(
            "Define la regla en lenguaje de negocio. Los detalles técnicos se mantienen internos."
        )
        name_key=f"business_rule_name_{mode}_{property_id}"
        code_key=f"business_rule_code_{mode}_{property_id}"
        last_name_key=f"business_rule_last_name_{mode}_{property_id}"

        name=st.text_input(
            "Nombre de la regla",
            key=name_key,
        )
        previous_name=st.session_state.get(last_name_key, "")
        code_generated=False
        if name.strip() and name != previous_name:
            st.session_state[code_key]=suggest_financial_rule_code(name=name)
            st.session_state[last_name_key]=name
            code_generated=True

        if code_generated:
            st.success(
                f"Código de la regla generado: {st.session_state.get(code_key, '')}. "
                "Puedes editarlo antes de guardar."
            )
        elif name.strip() and st.session_state.get(code_key):
            st.caption("Código sugerido por Condo_Smart. Puedes editarlo antes de guardar.")

        with st.form(
            f"business_rule_definition_{mode}_{property_id}",
            enter_to_submit=False,
        ):
            code=st.text_input(
                "Código de la regla",
                key=code_key,
                help=(
                    "Condo_Smart propone esta clave a partir del nombre. "
                    "Puedes editarla antes de guardar; el sistema validará su formato y unicidad."
                ),
            )
            description=st.text_area("Descripción y propósito")
            availability=st.selectbox(
                "¿En qué inmuebles podrá utilizarse esta regla?",
                ["Todos los inmuebles", "Sólo en ciertos tipos de inmueble"],
                disabled=(mode=="INMUEBLE"),
                help=(
                    "La disponibilidad determina dónde puede utilizarse la regla. "
                    "No la asigna automáticamente a los inmuebles."
                ),
            )
            property_types=[]
            if mode=="GLOBAL" and availability=="Sólo en ciertos tipos de inmueble":
                property_type_options={
                    "Fraccionamiento": "FRACCIONAMIENTO",
                    "Plaza comercial": "PLAZA_COMERCIAL",
                    "Condominio vertical": "VERTICAL",
                }
                selected_type_labels=st.multiselect(
                    "Selecciona los tipos de inmueble",
                    list(property_type_options),
                    help="Puedes seleccionar uno o varios tipos de inmueble.",
                )
                property_types=[property_type_options[label] for label in selected_type_labels]
                st.caption(
                    "La disponibilidad sólo habilita el uso de la regla en esos tipos de inmueble; "
                    "la asignación se realiza posteriormente desde la configuración de cada inmueble."
                )
            save=st.form_submit_button(
                "Guardar definición",
                type="primary",
                help="Guardar es la única acción que registra la definición.",
            )
            cancel=st.form_submit_button("Cancelar")
        if cancel:
            st.session_state.pop(action_key,None)
            st.session_state.pop(name_key,None)
            st.session_state.pop(code_key,None)
            st.session_state.pop(last_name_key,None)
            st.rerun()
        if save:
            try:
                definition=create_financial_rule_definition(
                    property_id=property_id,
                    code=code,
                    name=name,
                    description=description,
                    domain_code="FINANZAS",
                    result_type="JSON",
                    actor_id=user["id"],
                    parameter_schema={},
                    allows_inheritance=True,
                    allows_override=True,
                    allows_property=True,
                    allows_structure=True,
                    allows_space=False,
                )
                if mode=="GLOBAL" and availability=="Sólo en ciertos tipos de inmueble" and not property_types:
                    raise ValueError("SELECCIONA_AL_MENOS_UN_TIPO_DE_INMUEBLE")
                for property_type in property_types:
                    set_financial_rule_applicability(
                        property_id=property_id,
                        definition_id=definition["id"],
                        dimension_code="TIPO_INMUEBLE",
                        value_code=property_type,
                        included=True,
                        actor_id=user["id"],
                    )
                st.session_state.pop(action_key,None)
                st.session_state.pop(name_key,None)
                st.session_state.pop(code_key,None)
                st.session_state.pop(last_name_key,None)
                st.success("Definición guardada. Ya puede configurarse mediante su ciclo de vida gobernado.")
                st.rerun()
            except Exception as exc:
                st.error(f"No fue posible guardar la definición: {exc}")
