import textwrap
import pandas as pd
import streamlit as st

from components.ui import title
from core.access import authorized_properties, cid
from services.audit_service import (
    financial_severity,
    financial_status_explanation,
    list_financial_audit,
    list_system_audit,
    overall_severity,
    system_severity,
    system_status_explanation,
)


SEVERITY_COLORS = {
    "NORMAL": "#16A34A",
    "ATENCION": "#F59E0B",
    "CRITICO": "#DC2626",
}

SEVERITY_ICONS = {
    "NORMAL": "🟢",
    "ATENCION": "🟡",
    "CRITICO": "🔴",
}


def _property_options(user):
    rows = authorized_properties(
        user,
        include_inactive=True,
    )

    return {
        f"{row.get('clave') or ''} · {row.get('nombre') or ''}": row["id"]
        for row in rows
    }


def _selected_property(user):
    if user.get("rol_global") != "SUPERADMIN":
        return cid()

    options = {
        "Todos Los Inmuebles": None,
        **_property_options(user),
    }

    label = st.selectbox(
        "Inmueble",
        list(options),
        key="audit_property_filter",
    )

    return options[label]


def _status_card(
    explanation,
    title_text,
):
    severity = explanation["severity"]

    color = SEVERITY_COLORS[severity]
    icon = SEVERITY_ICONS[severity]

    display = {
        "NORMAL": "Normal",
        "ATENCION": "Atención",
        "CRITICO": "Crítico",
    }[severity]

    html = f"""
        <div style="
            border-left:8px solid {color};
            border-radius:10px;
            padding:16px 20px;
            background:rgba(255,255,255,.78);
            box-shadow:0 2px 8px rgba(0,0,0,.06);
            margin-bottom:12px;
        ">
            <div style="
                font-size:12px;
                color:#667085;
                font-weight:600;
                text-transform:uppercase;
            ">
                {title_text}
            </div>

            <div style="
                font-size:25px;
                font-weight:700;
                color:{color};
                margin-top:4px;
            ">
                {icon} {display}
            </div>

            <div style="
                font-size:14px;
                color:#344054;
                margin-top:10px;
                font-weight:600;
            ">
                {explanation["summary"]}
            </div>

            <div style="
                margin-top:12px;
                padding-top:10px;
                border-top:1px solid #E4E7EC;
                font-size:13px;
                color:#475467;
                line-height:1.55;
            ">
                <b>¿Por qué?</b>
                {explanation["reason"]}
                <br>

                <b>Evento detonante:</b>
                {explanation["trigger"]}
                <br>

                <b>Criterio utilizado:</b>
                {explanation["criteria"]}
                <br>

                <b>Recomendación:</b>
                {explanation["recommendation"]}
            </div>

            <div style="
                font-size:11px;
                color:#98A2B3;
                margin-top:10px;
            ">
                Evaluación automática basada en reglas
                determinísticas de auditoría.
            </div>
        </div>
        """

    st.markdown(
        textwrap.dedent(html).strip(),
        unsafe_allow_html=True,
    )


def _severity_counts(rows, classifier):
    totals = {
        "NORMAL": 0,
        "ATENCION": 0,
        "CRITICO": 0,
    }

    for row in rows:
        totals[classifier(row)] += 1

    return totals


def _system_dataframe(rows):
    return pd.DataFrame(
        [
            {
                "Fecha": row.get("fecha"),
                "Usuario": row.get("username") or "sistema",
                "Módulo": row.get("modulo") or "",
                "Acción": row.get("accion") or "",
                "Entidad": row.get("entidad") or "",
                "Registro": row.get("entidad_id"),
                "Resultado": row.get("resultado") or "",
                "Severidad": system_severity(row),
                "Detalle": row.get("detalle") or "",
            }
            for row in rows
        ]
    )


def _financial_dataframe(rows):
    return pd.DataFrame(
        [
            {
                "Fecha": row.get("fecha"),
                "Usuario": row.get("username") or "",
                "Operación": row.get("tipo_operacion") or "",
                "Entidad": row.get("entidad") or "",
                "Registro": row.get("entidad_id"),
                "Espacio": row.get("espacio_id"),
                "Monto MXN": row.get("monto_mxn"),
                "Estado Anterior":
                    row.get("estado_anterior") or "",
                "Estado Nuevo":
                    row.get("estado_nuevo") or "",
                "Referencia":
                    row.get("referencia") or "",
                "Severidad": financial_severity(row),
                "Detalle": row.get("detalle") or "",
            }
            for row in rows
        ]
    )


def _system_dashboard(rows):
    explanation = system_status_explanation(
        rows,
    )

    severity = explanation["severity"]

    counts = _severity_counts(
        rows,
        system_severity,
    )

    successful = sum(
        1
        for row in rows
        if str(
            row.get("resultado") or "OK"
        ).upper() in {"OK", "SUCCESS"}
    )

    _status_card(
        explanation,
        "Estado General Del Sistema",
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Eventos",
        len(rows),
        border=True,
    )

    c2.metric(
        "Correctos",
        successful,
        border=True,
    )

    c3.metric(
        "Atención",
        counts["ATENCION"],
        border=True,
    )

    c4.metric(
        "Críticos",
        counts["CRITICO"],
        border=True,
    )

    if not rows:
        return

    df = _system_dataframe(rows)

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.markdown("#### Actividad En El Tiempo")

        timeline = df.copy()

        timeline["Fecha"] = pd.to_datetime(
            timeline["Fecha"],
            errors="coerce",
        )

        timeline = (
            timeline
            .dropna(subset=["Fecha"])
            .assign(
                Día=lambda x:
                    x["Fecha"].dt.strftime("%Y-%m-%d")
            )
            .groupby("Día")
            .size()
            .rename("Eventos")
        )

        st.line_chart(
            timeline,
            height=260,
        )

    with chart_right:
        st.markdown("#### Eventos Por Acción")

        actions = (
            df["Acción"]
            .replace("", "SIN ACCION")
            .value_counts()
            .head(10)
        )

        st.bar_chart(
            actions,
            height=260,
        )

    st.markdown("#### Distribución Por Severidad")

    severity_df = pd.DataFrame(
        {
            "Severidad": [
                "Normal",
                "Atención",
                "Crítico",
            ],
            "Eventos": [
                counts["NORMAL"],
                counts["ATENCION"],
                counts["CRITICO"],
            ],
        }
    ).set_index("Severidad")

    st.bar_chart(
        severity_df,
        height=220,
    )

    incidents = df[
        df["Severidad"].isin(
            ["ATENCION", "CRITICO"]
        )
    ]

    st.markdown(
        "#### 🚨 Incidentes Que Requieren Atención"
    )

    if incidents.empty:
        st.success(
            "No existen incidentes clasificados "
            "como Atención o Crítico."
        )
    else:
        st.dataframe(
            incidents[
                [
                    "Fecha",
                    "Usuario",
                    "Acción",
                    "Entidad",
                    "Resultado",
                    "Severidad",
                    "Detalle",
                ]
            ],
            hide_index=True,
            use_container_width=True,
        )


def _financial_dashboard(rows):
    explanation = financial_status_explanation(
        rows,
    )

    severity = explanation["severity"]

    counts = _severity_counts(
        rows,
        financial_severity,
    )

    total_amount = sum(
        float(row.get("monto_mxn") or 0)
        for row in rows
    )

    _status_card(
        explanation,
        "Estado De Auditoría Financiera",
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Movimientos",
        len(rows),
        border=True,
    )

    c2.metric(
        "Importe Auditado",
        f"${total_amount:,.2f}",
        border=True,
    )

    c3.metric(
        "Revisión",
        counts["ATENCION"],
        border=True,
    )

    c4.metric(
        "Críticos",
        counts["CRITICO"],
        border=True,
    )

    if not rows:
        st.info(
            "El ledger financiero está activo y no "
            "registra movimientos todavía. Cuando "
            "Finanzas entre en operación, cargos, "
            "pagos, gastos, ajustes, cancelaciones "
            "y reversiones aparecerán aquí."
        )
        return

    df = _financial_dataframe(rows)

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.markdown(
            "#### Movimientos En El Tiempo"
        )

        timeline = df.copy()

        timeline["Fecha"] = pd.to_datetime(
            timeline["Fecha"],
            errors="coerce",
        )

        timeline = (
            timeline
            .dropna(subset=["Fecha"])
            .assign(
                Día=lambda x:
                    x["Fecha"].dt.strftime("%Y-%m-%d")
            )
            .groupby("Día")
            .size()
            .rename("Movimientos")
        )

        st.line_chart(
            timeline,
            height=260,
        )

    with chart_right:
        st.markdown(
            "#### Movimientos Por Operación"
        )

        operations = (
            df["Operación"]
            .replace("", "SIN OPERACION")
            .value_counts()
            .head(10)
        )

        st.bar_chart(
            operations,
            height=260,
        )

    st.markdown(
        "#### Distribución Por Severidad"
    )

    severity_df = pd.DataFrame(
        {
            "Severidad": [
                "Normal",
                "Revisión",
                "Crítico",
            ],
            "Movimientos": [
                counts["NORMAL"],
                counts["ATENCION"],
                counts["CRITICO"],
            ],
        }
    ).set_index("Severidad")

    st.bar_chart(
        severity_df,
        height=220,
    )

    incidents = df[
        df["Severidad"].isin(
            ["ATENCION", "CRITICO"]
        )
    ]

    st.markdown(
        "#### 🚨 Operaciones Que Requieren Revisión"
    )

    if incidents.empty:
        st.success(
            "No existen operaciones financieras "
            "clasificadas para revisión."
        )
    else:
        st.dataframe(
            incidents[
                [
                    "Fecha",
                    "Usuario",
                    "Operación",
                    "Entidad",
                    "Monto MXN",
                    "Severidad",
                    "Referencia",
                    "Detalle",
                ]
            ],
            hide_index=True,
            use_container_width=True,
        )


def _system_tab(user, property_id):
    st.markdown("### Actividad Del Sistema")

    rows = list_system_audit(
        user,
        property_id,
        limit=1000,
    )

    _system_dashboard(rows)

    st.markdown("---")
    st.markdown("### Explorador De Eventos")

    if not rows:
        st.info(
            "No existen eventos de auditoría para "
            "los filtros actuales."
        )
        return

    df = _system_dataframe(rows)

    f1, f2, f3, f4 = st.columns(4)

    user_filter = f1.text_input(
        "Usuario",
        key="audit_system_user_filter",
    ).strip().lower()

    action_filter = f2.text_input(
        "Acción",
        key="audit_system_action_filter",
    ).strip().lower()

    entity_filter = f3.text_input(
        "Entidad",
        key="audit_system_entity_filter",
    ).strip().lower()

    severity_filter = f4.selectbox(
        "Severidad",
        [
            "Todas",
            "Normal",
            "Atención",
            "Crítico",
        ],
        key="audit_system_severity_filter",
    )

    if user_filter:
        df = df[
            df["Usuario"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.contains(user_filter)
        ]

    if action_filter:
        df = df[
            df["Acción"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.contains(action_filter)
        ]

    if entity_filter:
        df = df[
            df["Entidad"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.contains(entity_filter)
        ]

    severity_map = {
        "Normal": "NORMAL",
        "Atención": "ATENCION",
        "Crítico": "CRITICO",
    }

    if severity_filter != "Todas":
        df = df[
            df["Severidad"]
            == severity_map[severity_filter]
        ]

    st.caption(
        f"{len(df)} evento(s) del sistema."
    )

    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
    )


def _financial_tab(user, property_id):
    st.markdown("### Auditoría Financiera")

    rows = list_financial_audit(
        user,
        property_id,
        limit=1000,
    )

    _financial_dashboard(rows)

    st.markdown("---")
    st.markdown(
        "### Explorador De Movimientos"
    )

    if not rows:
        return

    df = _financial_dataframe(rows)

    f1, f2, f3, f4 = st.columns(4)

    operation_filter = f1.text_input(
        "Operación",
        key="audit_fin_operation_filter",
    ).strip().lower()

    entity_filter = f2.text_input(
        "Entidad",
        key="audit_fin_entity_filter",
    ).strip().lower()

    reference_filter = f3.text_input(
        "Referencia",
        key="audit_fin_reference_filter",
    ).strip().lower()

    severity_filter = f4.selectbox(
        "Severidad",
        [
            "Todas",
            "Normal",
            "Revisión",
            "Crítico",
        ],
        key="audit_fin_severity_filter",
    )

    if operation_filter:
        df = df[
            df["Operación"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.contains(operation_filter)
        ]

    if entity_filter:
        df = df[
            df["Entidad"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.contains(entity_filter)
        ]

    if reference_filter:
        df = df[
            df["Referencia"]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.contains(reference_filter)
        ]

    severity_map = {
        "Normal": "NORMAL",
        "Revisión": "ATENCION",
        "Crítico": "CRITICO",
    }

    if severity_filter != "Todas":
        df = df[
            df["Severidad"]
            == severity_map[severity_filter]
        ]

    st.caption(
        f"{len(df)} movimiento(s) financieros."
    )

    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
    )


def render():
    title(
        "Auditoría",
        "Trazabilidad Operativa Y Financiera",
    )

    user = st.session_state.get("user") or {}

    property_id = _selected_property(user)

    if (
        user.get("rol_global") != "SUPERADMIN"
        and not property_id
    ):
        st.info(
            "Selecciona un inmueble autorizado "
            "para consultar su auditoría."
        )
        return

    system_tab, financial_tab = st.tabs(
        [
            "Actividad Del Sistema",
            "Auditoría Financiera",
        ]
    )

    with system_tab:
        try:
            _system_tab(
                user,
                property_id,
            )
        except PermissionError:
            st.warning(
                "Tu perfil no tiene permiso para "
                "consultar esta auditoría."
            )

    with financial_tab:
        try:
            _financial_tab(
                user,
                property_id,
            )
        except PermissionError:
            st.warning(
                "Tu perfil no tiene permiso para "
                "consultar la auditoría financiera."
            )
