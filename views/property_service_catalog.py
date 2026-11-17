from datetime import date

import pandas as pd
import streamlit as st

from core.authorization import authorize
from views.property_service_categories import (
    render_service_categories,
)
from services.property_structure import (
    list_nodes,
    node_path,
)
from services.property_service_categories import (
    list_service_categories,
    suggest_service_code,
)
from services.property_service_catalog import (
    get_property_service,
    list_property_services,
    list_service_availability,
)
from services.property_service_commands import (
    create_property_service,
    create_service_availability,
    set_property_service_active,
    update_property_service,
)


MANAGE_PERMISSION = "FINANZAS_REGLA_GESTIONAR"


def _can_manage(
    *,
    property_id,
    user,
):
    return authorize(
        user,
        MANAGE_PERMISSION,
        property_id,
    ).allowed


def _service_state_label(active):
    return (
        "Activo"
        if active
        else "Inactivo"
    )


def _scope_label(value):
    labels = {
        "INMUEBLE": "Todo el inmueble",
        "ESTRUCTURA": "Estructura",
        "ESPACIO": "Espacio",
    }

    return labels.get(
        value,
        value,
    )


def _availability_label(value):
    return (
        "Disponible"
        if value
        else "No disponible"
    )


def _date_label(value):
    if value is None:
        return "Sin fecha de término"

    return value.strftime("%d/%m/%Y")


def _service_selection_key(property_id):
    return (
        f"property_service_selected_"
        f"{property_id}"
    )


def _action_key(property_id):
    return (
        f"property_service_action_"
        f"{property_id}"
    )


def _set_action(
    property_id,
    action,
):
    st.session_state[
        _action_key(property_id)
    ] = action


def _clear_action(property_id):
    st.session_state.pop(
        _action_key(property_id),
        None,
    )


def _selected_service_id(property_id):
    return st.session_state.get(
        _service_selection_key(property_id)
    )


def _space_options(spaces):
    result = {}

    for label, value in (spaces or {}).items():
        if isinstance(value, dict):
            identifier = value.get("id")
            name = (
                value.get("clave")
                or value.get("nombre")
                or label
            )
        else:
            identifier = value
            name = label

        if identifier is not None:
            result[str(name)] = identifier

    return result


def _structure_options(property_id):
    nodes = list_nodes(
        property_id,
        active_only=True,
    )

    result = {}

    for node in nodes:
        item = dict(node)
        label = (
            node_path(
                nodes,
                item["id"],
            )
            or item.get("nombre")
            or str(item["id"])
        )

        result[label] = item["id"]

    return result


def _render_catalog_grid(
    *,
    property_id,
    include_inactive=False,
):
    services = list_property_services(
        property_id=property_id,
        active_only=not include_inactive,
    )

    if not services:
        st.info(
            "El inmueble todavía no tiene servicios activos "
            "para mostrar."
        )
        return []

    display = pd.DataFrame(
        [
            {
                "ID": item["id"],
                "Servicio": item["nombre"],
                "Código": item["codigo"],
                "Categoría": (
                    (
                        f"{item['category_name']} "
                        f"({item['category_code']})"
                    )
                    if item.get("category_name")
                    else "Sin categoría"
                ),
                "Estado": (
                    _service_state_label(
                        item["activo"]
                    )
                ),
                "Descripción": (
                    item["descripcion"]
                    or "Sin descripción"
                ),
            }
            for item in services
        ]
    )

    event = st.dataframe(
        display,
        hide_index=True,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "ID": None,
        },
        key=(
            f"property_service_grid_"
            f"{property_id}"
        ),
    )

    selected_rows = (
        event.selection.rows
        if event is not None
        else []
    )

    if selected_rows:
        selected_index = selected_rows[0]
        selected = services[selected_index]

        st.session_state[
            _service_selection_key(
                property_id
            )
        ] = selected["id"]

    return services


def _render_create_form(
    *,
    property_id,
    user,
):
    st.markdown("### Nuevo servicio")

    st.caption(
        "El servicio pertenecerá únicamente "
        "al inmueble activo. No se aplicará "
        "ninguna restricción automáticamente."
    )

    categories = list_service_categories(
        property_id=property_id,
        active_only=True,
    )

    if not categories:
        st.warning(
            "Antes de crear un servicio debes "
            "registrar al menos una categoría "
            "activa en la pestaña Categorías."
        )
        if st.button(
            "Cancelar",
            key=f"property_service_create_cancel_{property_id}",
        ):
            _clear_action(property_id)
            st.rerun()
        return

    suggested_code = suggest_service_code(
        property_id=property_id,
    )

    category_options = {
        f"{item['nombre']} ({item['codigo']})": item['id']
        for item in categories
    }

    with st.form(f"property_service_create_{property_id}"):
        st.text_input(
            "Código",
            value=suggested_code,
            disabled=True,
            help=(
                "Código sugerido automáticamente a partir de la clave "
                "del inmueble y del siguiente consecutivo disponible. "
                "El código permanecerá estable después de crear el servicio."
            ),
        )
        name = st.text_input("Nombre del servicio")
        category_label = st.selectbox(
            "Categoría",
            list(category_options),
            help="Categoría gobernada desde el subcatálogo del inmueble.",
        )
        category_id = category_options[category_label]
        description = st.text_area("Descripción")

        save, cancel = st.columns(2)
        with save:
            submitted = st.form_submit_button(
                "Crear servicio",
                type="primary",
            )
        with cancel:
            cancelled = st.form_submit_button("Cancelar")

    if cancelled:
        _clear_action(property_id)
        st.rerun()
    if not submitted:
        return

    try:
        create_property_service(
            property_id=property_id,
            code=suggested_code,
            name=name,
            description=description,
            category_id=category_id,
            actor_id=user['id'],
        )
    except Exception as exc:
        st.error(f"No fue posible crear el servicio: {exc}")
        return

    _clear_action(property_id)
    st.success("Servicio creado correctamente.")
    st.rerun()

def _render_edit_form(
    *,
    property_id,
    user,
    service,
):
    st.markdown("### Editar servicio")

    st.caption(
        "El código permanece estable para "
        "conservar la trazabilidad."
    )

    st.write(
        "**Código:** "
        + service["codigo"]
    )

    categories = list_service_categories(
        property_id=property_id,
        active_only=True,
    )

    if not categories:
        st.warning(
            "No existen categorías activas. "
            "Activa o crea una categoría antes "
            "de modificar este servicio."
        )
        return

    category_options = {
        f"{item['nombre']} ({item['codigo']})": item['id']
        for item in categories
    }

    labels = list(category_options)
    current_category_id = service.get("categoria_id")
    current_index = next(
        (
            i
            for i, label in enumerate(labels)
            if category_options[label] == current_category_id
        ),
        0,
    )

    with st.form(
        f"property_service_edit_{property_id}_{service['id']}"
    ):
        name = st.text_input(
            "Nombre del servicio",
            value=service["nombre"],
        )

        category_label = st.selectbox(
            "Categoría",
            labels,
            index=current_index,
            help="Categoría gobernada desde el subcatálogo del inmueble.",
        )
        category_id = category_options[category_label]

        description = st.text_area(
            "Descripción",
            value=service["descripcion"] or "",
        )

        save, cancel = st.columns(2)
        with save:
            submitted = st.form_submit_button(
                "Guardar cambios",
                type="primary",
            )
        with cancel:
            cancelled = st.form_submit_button("Cancelar")

    if cancelled:
        _clear_action(property_id)
        st.rerun()
    if not submitted:
        return

    try:
        update_property_service(
            property_id=property_id,
            service_id=service["id"],
            name=name,
            description=description,
            category_id=category_id,
            actor_id=user["id"],
        )
    except Exception as exc:
        st.error(f"No fue posible actualizar el servicio: {exc}")
        return

    _clear_action(property_id)
    st.success("Servicio actualizado correctamente.")
    st.rerun()

def _render_active_form(
    *,
    property_id,
    user,
    service,
):
    target_active = not service["activo"]

    action_label = (
        "Activar"
        if target_active
        else "Desactivar"
    )

    st.markdown(
        f"### {action_label} servicio"
    )

    st.warning(
        "Esta operación cambia la disponibilidad "
        "administrativa del servicio, pero no "
        "aplica restricciones operativas sobre "
        "ningún espacio."
    )

    reason = st.text_input(
        "Motivo",
        key=(
            f"property_service_active_reason_"
            f"{property_id}_{service['id']}"
        ),
    )

    confirm, cancel = st.columns(2)

    with confirm:
        clicked = st.button(
            f"Confirmar {action_label.lower()}",
            type="primary",
        )

    with cancel:
        cancelled = st.button(
            "Cancelar",
            key=(
                f"property_service_active_cancel_"
                f"{property_id}_{service['id']}"
            ),
        )

    if cancelled:
        _clear_action(property_id)
        st.rerun()

    if not clicked:
        return

    try:
        set_property_service_active(
            property_id=property_id,
            service_id=service["id"],
            active=target_active,
            actor_id=user["id"],
            reason=reason,
        )

    except Exception as exc:
        st.error(
            "No fue posible cambiar el "
            f"estado del servicio: {exc}"
        )
        return

    _clear_action(property_id)

    st.success(
        f"Servicio {action_label.lower()}do "
        "correctamente."
    )
    st.rerun()


def _render_availability_form(
    *,
    property_id,
    user,
    service,
    spaces,
):
    st.markdown(
        "### Nueva disponibilidad"
    )

    st.caption(
        "Define dónde está disponible este "
        "servicio. La configuración puede "
        "heredarse o especializarse mediante "
        "un override."
    )

    scope_labels = {
        "Todo el inmueble": "INMUEBLE",
        "Estructura": "ESTRUCTURA",
        "Espacio": "ESPACIO",
    }

    level_label = st.selectbox(
        "Nivel de disponibilidad",
        list(scope_labels),
        key=(
            f"property_service_scope_"
            f"{property_id}_{service['id']}"
        ),
    )

    scope_level = scope_labels[
        level_label
    ]

    structure_id = None
    space_id = None

    if scope_level == "ESTRUCTURA":
        structures = _structure_options(
            property_id
        )

        if not structures:
            st.warning(
                "No existen estructuras activas."
            )
            return

        structure_label = st.selectbox(
            "Estructura",
            list(structures),
            key=(
                f"property_service_structure_"
                f"{property_id}_{service['id']}"
            ),
        )

        structure_id = structures[
            structure_label
        ]

    elif scope_level == "ESPACIO":
        space_choices = _space_options(spaces)

        if not space_choices:
            st.warning(
                "No existen espacios disponibles."
            )
            return

        space_label = st.selectbox(
            "Espacio",
            list(space_choices),
            key=(
                f"property_service_space_"
                f"{property_id}_{service['id']}"
            ),
        )

        space_id = space_choices[
            space_label
        ]

    with st.form(
        f"property_service_availability_"
        f"{property_id}_{service['id']}_"
        f"{scope_level}"
    ):
        available = st.checkbox(
            "Servicio disponible",
            value=True,
        )

        inherits = st.checkbox(
            "Heredar a niveles inferiores",
            value=True,
        )

        is_override = st.checkbox(
            "Es una configuración específica",
            value=(
                scope_level != "INMUEBLE"
            ),
        )

        priority = st.number_input(
            "Prioridad",
            min_value=0,
            value=100,
            step=1,
        )

        effective_from = st.date_input(
            "Vigente desde",
            value=date.today(),
        )

        use_end = st.checkbox(
            "Definir fecha de término",
            value=False,
        )

        effective_to = None

        if use_end:
            effective_to = st.date_input(
                "Vigente hasta",
                value=effective_from,
            )

        reason = st.text_input(
            "Motivo de configuración",
            value=(
                "Configuración inicial "
                "de disponibilidad"
            ),
        )

        save, cancel = st.columns(2)

        with save:
            submitted = (
                st.form_submit_button(
                    "Guardar disponibilidad",
                    type="primary",
                )
            )

        with cancel:
            cancelled = (
                st.form_submit_button(
                    "Cancelar"
                )
            )

    if cancelled:
        _clear_action(property_id)
        st.rerun()

    if not submitted:
        return

    try:
        create_service_availability(
            property_id=property_id,
            service_id=service["id"],
            scope_level=scope_level,
            structure_id=structure_id,
            space_id=space_id,
            available=available,
            inherits=inherits,
            is_override=is_override,
            priority=priority,
            effective_from=effective_from,
            effective_to=effective_to,
            change_reason=reason,
            actor_id=user["id"],
        )

    except Exception as exc:
        st.error(
            "No fue posible guardar la "
            f"disponibilidad: {exc}"
        )
        return

    _clear_action(property_id)

    st.success(
        "Disponibilidad guardada "
        "correctamente."
    )
    st.rerun()


def _render_availability_history(
    *,
    property_id,
    service_id,
):
    rows = list_service_availability(
        property_id=property_id,
        service_id=service_id,
    )

    st.markdown(
        "### Disponibilidad configurada"
    )

    if not rows:
        st.info(
            "El servicio todavía no tiene "
            "disponibilidad configurada."
        )
        return

    display = pd.DataFrame(
        [
            {
                "Nivel": _scope_label(
                    row["scope_level"]
                ),
                "Estructura": (
                    row["estructura_id"]
                    or "—"
                ),
                "Espacio": (
                    row["espacio_id"]
                    or "—"
                ),
                "Disponibilidad": (
                    _availability_label(
                        row["disponible"]
                    )
                ),
                "Hereda": (
                    "Sí"
                    if row["hereda"]
                    else "No"
                ),
                "Configuración específica": (
                    "Sí"
                    if row["es_override"]
                    else "No"
                ),
                "Prioridad": row["prioridad"],
                "Desde": _date_label(
                    row["vigente_desde"]
                ),
                "Hasta": _date_label(
                    row["vigente_hasta"]
                ),
                "Motivo": (
                    row["motivo_cambio"]
                    or "Sin motivo"
                ),
            }
            for row in rows
        ]
    )

    st.dataframe(
        display,
        hide_index=True,
        use_container_width=True,
    )


def _render_service_catalog_content(
    *,
    property_id,
    user,
    spaces,
):
    st.markdown(
        "### Catálogo de Servicios"
    )

    st.caption(
        "Servicios configurables del inmueble. "
        "La existencia y disponibilidad de un "
        "servicio no implica que pueda ser "
        "restringido automáticamente."
    )

    can_manage = _can_manage(
        property_id=property_id,
        user=user,
    )

    include_inactive = st.checkbox(
        "Mostrar servicios inactivos",
        value=False,
        key=f"property_service_show_inactive_{property_id}",
    )

    services = _render_catalog_grid(
        property_id=property_id,
        include_inactive=include_inactive,
    )

    selected_id = _selected_service_id(
        property_id
    )

    selected = None

    if selected_id is not None:
        selected = get_property_service(
            property_id=property_id,
            service_id=selected_id,
        )

    buttons = st.columns(4)

    with buttons[0]:
        if st.button(
            "Nuevo servicio",
            key=f"property_service_new_{property_id}",
            disabled=not can_manage,
            use_container_width=True,
        ):
            _set_action(
                property_id,
                "CREATE",
            )

    with buttons[1]:
        if st.button(
            "Editar",
            key=f"property_service_edit_button_{property_id}",
            disabled=(
                not can_manage
                or selected is None
            ),
            use_container_width=True,
        ):
            _set_action(
                property_id,
                "EDIT",
            )

    with buttons[2]:
        if st.button(
            (
                "Desactivar"
                if selected
                and selected["activo"]
                else "Activar"
            ),
            key=f"property_service_active_button_{property_id}",
            disabled=(
                not can_manage
                or selected is None
            ),
            use_container_width=True,
        ):
            _set_action(
                property_id,
                "ACTIVE",
            )

    with buttons[3]:
        if st.button(
            "Disponibilidad",
            key=f"property_service_availability_button_{property_id}",
            disabled=(
                not can_manage
                or selected is None
                or not selected["activo"]
            ),
            use_container_width=True,
        ):
            _set_action(
                property_id,
                "AVAILABILITY",
            )

    if selected is not None:
        st.info(
            "Servicio seleccionado: "
            f"{selected['nombre']} "
            f"({selected['codigo']})"
        )

        _render_availability_history(
            property_id=property_id,
            service_id=selected["id"],
        )

    action = st.session_state.get(
        _action_key(property_id)
    )

    if action == "CREATE":
        _render_create_form(
            property_id=property_id,
            user=user,
        )

    elif (
        action == "EDIT"
        and selected is not None
    ):
        _render_edit_form(
            property_id=property_id,
            user=user,
            service=selected,
        )

    elif (
        action == "ACTIVE"
        and selected is not None
    ):
        _render_active_form(
            property_id=property_id,
            user=user,
            service=selected,
        )

    elif (
        action == "AVAILABILITY"
        and selected is not None
    ):
        _render_availability_form(
            property_id=property_id,
            user=user,
            service=selected,
            spaces=spaces,
        )

    if not can_manage:
        st.info(
            "El usuario puede consultar el "
            "catálogo, pero no modificarlo."
        )

def render_property_service_catalog(
    *,
    property_id,
    user,
    spaces,
):
    catalog_tab, category_tab = st.tabs(
        [
            "Catálogo Servicios",
            "Categorías",
        ]
    )

    with catalog_tab:
        _render_service_catalog_content(
            property_id=property_id,
            user=user,
            spaces=spaces,
        )

    with category_tab:
        render_service_categories(
            property_id=property_id,
            user=user,
        )
