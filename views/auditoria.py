import pandas as pd
import streamlit as st

from components.ui import title
from core.access import authorized_properties, cid
from services.audit_service import (
    list_financial_audit,
    list_system_audit,
)


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


def _system_tab(user, property_id):
    st.markdown("### Actividad Del Sistema")

    rows = list_system_audit(
        user,
        property_id,
        limit=1000,
    )

    if not rows:
        st.info(
            "No existen eventos de auditoría para "
            "los filtros actuales."
        )
        return

    df = pd.DataFrame(
        [
            {
                "Fecha": row.get("fecha"),
                "Usuario": row.get("username") or "sistema",
                "Módulo": row.get("modulo") or "",
                "Acción": row.get("accion") or "",
                "Entidad": row.get("entidad") or "",
                "Registro": row.get("entidad_id"),
                "Resultado": row.get("resultado") or "",
                "Detalle": row.get("detalle") or "",
            }
            for row in rows
        ]
    )

    f1, f2, f3 = st.columns(3)

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

    if not rows:
        st.info(
            "Todavía no existen eventos financieros "
            "registrados. El ledger ya está preparado "
            "para cargos, pagos, gastos, ajustes, "
            "cancelaciones y reversiones."
        )
        return

    df = pd.DataFrame(
        [
            {
                "Fecha": row.get("fecha"),
                "Usuario": row.get("username") or "",
                "Operación": row.get("tipo_operacion") or "",
                "Entidad": row.get("entidad") or "",
                "Registro": row.get("entidad_id"),
                "Espacio": row.get("espacio_id"),
                "Monto MXN": row.get("monto_mxn"),
                "Estado Anterior": row.get("estado_anterior") or "",
                "Estado Nuevo": row.get("estado_nuevo") or "",
                "Referencia": row.get("referencia") or "",
                "Detalle": row.get("detalle") or "",
            }
            for row in rows
        ]
    )

    f1, f2, f3 = st.columns(3)

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

    st.caption(
        f"{len(df)} evento(s) financieros."
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
            _system_tab(user, property_id)
        except PermissionError:
            st.warning(
                "Tu perfil no tiene permiso para "
                "consultar esta auditoría."
            )

    with financial_tab:
        try:
            _financial_tab(user, property_id)
        except PermissionError:
            st.warning(
                "Tu perfil no tiene permiso para "
                "consultar la auditoría financiera."
            )
