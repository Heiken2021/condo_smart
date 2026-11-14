import pandas as pd
import plotly.express as px
import streamlit as st

from components.ui import (
    clickable_image,
    metrics,
    title,
)
from core.formatting import money
from services.admin_dashboard import (
    dashboard_scope,
    management_periods,
    portfolio_totals,
    property_snapshot,
    property_type_distribution,
)
from services.analytics import prop_rows


STATUS_COLORS = {
    "ACTIVO": "#18A76F",
    "SIN ESPACIOS": "#F2B134",
    "INACTIVO": "#D94B4B",
}


def _portfolio_grid(rows):
    data = []

    for row in rows:
        data.append(
            {
                "Estado": (
                    f"{row['semaforo']} "
                    f"{row['estado_snapshot'].title()}"
                ),
                "Inmueble": row.get("nombre") or "",
                "Clave": row.get("clave") or "",
                "Tipo": row.get("tipo_codigo") or "Sin Tipo",
                "Rol": row.get("rol_usuario") or "",
                "Espacios": row.get("espacios") or 0,
                "Ocupados": row.get("ocupados") or 0,
                "Disponibles": row.get("disponibles") or 0,
                "Ocupación": (
                    f"{row.get('ocupacion_pct', 0):.1f}%"
                ),
                "Administradores": (
                    row.get("administradores") or 0
                ),
                "Dirección": row.get("direccion") or "",
            }
        )

    return pd.DataFrame(data)


def _render_property_cards(rows):
    st.markdown("#### Inmuebles Administrados")

    cols=st.columns(min(4,len(rows)))

    for i, item in enumerate(rows):
        with cols[i % len(cols)]:
            if item.get("portada_data"):
                clickable_image(
                    item["portada_data"],
                    item.get("portada_mime") or "image/jpeg",
                    f"Portada - {item['nombre']}",
                    width=140,
                    max_height=90,
                )

            st.subheader(item.get("nombre") or "Sin Nombre")

            st.caption(
                (
                    item.get("tipo_codigo")
                    or "Sin Tipo"
                )
                + " · "
                + (
                    item.get("direccion")
                    or "Sin Dirección"
                )
            )

            charges = float(item.get("cargos") or 0)
            paid = float(item.get("pagos") or 0)

            rate = (
                round(100 * paid / charges, 1)
                if charges
                else 0
            )

            st.write(
                f"{item.get('espacios') or 0} Espacios · "
                f"{item.get('administradores') or 0} "
                "Administradores"
            )

            st.progress(
                min(rate / 100, 1),
                text=f"Cobranza {rate}%",
            )


def _render_financial_summary(rows, user):
    charges = sum(
        float(item.get("cargos") or 0)
        for item in rows
    )
    paid = sum(
        float(item.get("pagos") or 0)
        for item in rows
    )

    metrics(
        [
            (
                "Inmuebles Activos",
                sum(
                    bool(item.get("activo"))
                    for item in rows
                ),
            ),
            (
                "Espacios",
                sum(
                    int(item.get("espacios") or 0)
                    for item in rows
                ),
            ),
            (
                "Cargos",
                money(charges),
            ),
            (
                "Cobrado",
                money(paid),
            ),
            (
                "Pendiente",
                money(max(charges - paid, 0)),
            ),
        ]
    )

    frame = pd.DataFrame(rows)

    if frame.empty:
        return

    left, right = st.columns(2)

    with left:
        st.subheader("Distribución Por Tipo De Inmueble")

        figure = px.pie(
            frame,
            names="tipo_codigo",
            values="espacios",
            hole=0.5,
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
            key="mi_gestion_legacy_type_distribution",
        )

    with right:
        st.subheader("Cobranza Por Inmueble")

        frame["cobranza_pct"] = [
            (
                round(
                    100
                    * float(row.pagos)
                    / float(row.cargos),
                    1,
                )
                if float(row.cargos)
                else 0
            )
            for _, row in frame.iterrows()
        ]

        figure = px.bar(
            frame,
            x="cobranza_pct",
            y="nombre",
            orientation="h",
            range_x=[0, 100],
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
            key="mi_gestion_collection_by_property",
        )

    history = pd.DataFrame(
        management_periods(user)
    )

    st.subheader("Evolución De Cobranza")

    if not history.empty:
        st.plotly_chart(
            px.bar(
                history,
                x="periodo",
                y=[
                    "cargos",
                    "pagos",
                ],
                barmode="group",
            ),
            use_container_width=True,
            key="mi_gestion_collection_history",
        )
    else:
        st.info(
            "Aún No Hay Información Suficiente "
            "Para Esta Visualización"
        )


def _render_management_snapshot(rows):
    totals = portfolio_totals(rows)

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.metric(
            "Inmuebles",
            totals["inmuebles"],
        )

    with k2:
        st.metric(
            "Activos",
            totals["inmuebles_activos"],
        )

    with k3:
        st.metric(
            "Espacios",
            totals["espacios"],
        )

    with k4:
        st.metric(
            "Ocupados",
            totals["ocupados"],
        )

    with k5:
        st.metric(
            "Ocupación",
            f"{totals['ocupacion_pct']:.1f}%",
        )

    st.divider()

    left, right = st.columns(
        [
            1,
            1.25,
        ],
        gap="large",
    )

    with left:
        st.markdown("#### Distribución Administrativa Por Tipo")

        type_frame = pd.DataFrame(
            property_type_distribution(rows)
        )

        if not type_frame.empty:
            figure = px.pie(
                type_frame,
                names="tipo",
                values="inmuebles",
                hole=0.55,
                color_discrete_sequence=[
                    "#D9342B",
                    "#153B5B",
                    "#2C7596",
                    "#18A76F",
                    "#F2B134",
                    "#7C5DAA",
                ],
            )

            figure.update_layout(
                margin=dict(
                    l=10,
                    r=10,
                    t=10,
                    b=10,
                )
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
                key="mi_gestion_management_type",
            )

    with right:
        st.markdown("#### Ocupación Por Inmueble")

        occupation_frame = pd.DataFrame(
            [
                {
                    "Inmueble": row.get("nombre"),
                    "Ocupación": row.get(
                        "ocupacion_pct",
                        0,
                    ),
                    "Estado": row.get(
                        "estado_snapshot",
                    ),
                }
                for row in rows
            ]
        )

        if not occupation_frame.empty:
            occupation_frame = occupation_frame.sort_values(
                [
                    "Ocupación",
                    "Inmueble",
                ],
                ascending=[
                    True,
                    True,
                ],
            )

            figure = px.bar(
                occupation_frame,
                x="Ocupación",
                y="Inmueble",
                orientation="h",
                color="Estado",
                color_discrete_map=STATUS_COLORS,
                range_x=[
                    0,
                    100,
                ],
                text="Ocupación",
            )

            figure.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
                cliponaxis=False,
            )

            figure.update_layout(
                margin=dict(
                    l=10,
                    r=40,
                    t=10,
                    b=10,
                ),
                xaxis_title="Ocupación (%)",
                yaxis_title="",
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
                key="mi_gestion_occupancy",
            )

    st.divider()
    st.markdown("#### Snapshot De Inmuebles Administrados")

    st.caption(
        "Vista informativa. El contenido se limita "
        "automáticamente al alcance autorizado."
    )

    st.dataframe(
        _portfolio_grid(rows),
        use_container_width=True,
        hide_index=True,
    )

    if totals["inmuebles_inactivos"]:
        st.warning(
            "El portafolio contiene "
            f"{totals['inmuebles_inactivos']} "
            "inmueble(s) inactivo(s)."
        )


def render():
    user = st.session_state.get("user") or {}

    try:
        scope = dashboard_scope(user)
        snapshot_rows = property_snapshot(user)
    except PermissionError:
        st.error(
            "Tu perfil no dispone de un ámbito "
            "administrativo para consultar Mi Gestión."
        )
        return

    title(
        "Mi Gestión",
        (
            f"{scope['title']} · "
            f"{scope['role_label']}"
        ),
    )

    st.caption(scope["description"])

    legacy_rows = prop_rows(user)

    if not snapshot_rows and not legacy_rows:
        st.info(
            "No hay inmuebles disponibles dentro "
            "del alcance administrativo actual."
        )
        return

    if legacy_rows:
        _render_financial_summary(
            legacy_rows,
            user,
        )

        st.divider()

        _render_property_cards(
            legacy_rows,
        )

    if snapshot_rows:
        st.divider()
        st.markdown("### Snapshot Administrativo")
        _render_management_snapshot(
            snapshot_rows,
        )
