import pandas as pd
import streamlit as st

from core.authorization import authorize
from services.property_service_categories import (
    get_service_category,
    list_service_categories,
)
from services.property_service_category_commands import (
    create_service_category,
    set_service_category_active,
    update_service_category,
)


MANAGE_PERMISSION = "FINANZAS_REGLA_GESTIONAR"


def _selected_key(property_id):
    return f"service_category_selected_{property_id}"


def _action_key(property_id):
    return f"service_category_action_{property_id}"


def _can_manage(user, property_id):
    return authorize(
        user,
        MANAGE_PERMISSION,
        property_id,
    ).allowed


def _next_category_code(categories):
    maximum = 0

    for category in categories:
        code = str(
            category.get("codigo") or ""
        ).upper()

        if (
            code.startswith("CAT")
            and code[3:].isdigit()
        ):
            maximum = max(
                maximum,
                int(code[3:]),
            )

    return f"CAT{maximum + 1:03d}"


def _set_action(property_id, action):
    st.session_state[
        _action_key(property_id)
    ] = action


def _clear_action(property_id):
    st.session_state.pop(
        _action_key(property_id),
        None,
    )


def _render_create(
    *,
    property_id,
    user,
    categories,
):
    st.markdown("#### Nueva categoría")

    suggested = _next_category_code(
        categories
    )

    with st.form(
        f"service_category_create_{property_id}"
    ):
        code = st.text_input(
            "Código",
            value=suggested,
            disabled=True,
            help=(
                "Código sugerido automáticamente. "
                "Quedará estable después de crear "
                "la categoría."
            ),
        )

        name = st.text_input(
            "Nombre de la categoría"
        )

        description = st.text_area(
            "Descripción / enfoque"
        )

        order = st.number_input(
            "Orden de presentación",
            min_value=0,
            value=100,
            step=10,
        )

        save, cancel = st.columns(2)

        with save:
            submitted = (
                st.form_submit_button(
                    "Crear categoría",
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
        create_service_category(
            property_id=property_id,
            code=suggested,
            name=name,
            description=description,
            order=order,
            actor_id=user["id"],
        )
    except Exception as exc:
        st.error(
            "No fue posible crear la "
            f"categoría: {exc}"
        )
        return

    _clear_action(property_id)
    st.success(
        "Categoría creada correctamente."
    )
    st.rerun()


def _render_edit(
    *,
    property_id,
    user,
    category,
):
    st.markdown("#### Editar categoría")

    st.write(
        "**Código:** "
        + category["codigo"]
    )

    with st.form(
        f"service_category_edit_"
        f"{property_id}_{category['id']}"
    ):
        name = st.text_input(
            "Nombre de la categoría",
            value=category["nombre"],
        )

        description = st.text_area(
            "Descripción / enfoque",
            value=(
                category["descripcion"]
                or ""
            ),
        )

        order = st.number_input(
            "Orden de presentación",
            min_value=0,
            value=int(category["orden"]),
            step=10,
        )

        save, cancel = st.columns(2)

        with save:
            submitted = (
                st.form_submit_button(
                    "Guardar cambios",
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
        update_service_category(
            property_id=property_id,
            category_id=category["id"],
            name=name,
            description=description,
            order=order,
            actor_id=user["id"],
        )
    except Exception as exc:
        st.error(
            "No fue posible actualizar la "
            f"categoría: {exc}"
        )
        return

    _clear_action(property_id)
    st.success(
        "Categoría actualizada correctamente."
    )
    st.rerun()


def _render_active(
    *,
    property_id,
    user,
    category,
):
    target = not category["activo"]

    verb = (
        "activar"
        if target
        else "desactivar"
    )

    st.markdown(
        f"#### {verb.capitalize()} categoría"
    )

    reason = st.text_input(
        "Motivo",
        key=(
            f"service_category_reason_"
            f"{property_id}_{category['id']}"
        ),
    )

    confirm, cancel = st.columns(2)

    with confirm:
        clicked = st.button(
            f"Confirmar {verb}",
            type="primary",
        )

    with cancel:
        cancelled = st.button(
            "Cancelar",
            key=(
                f"service_category_cancel_"
                f"{property_id}_{category['id']}"
            ),
        )

    if cancelled:
        _clear_action(property_id)
        st.rerun()

    if not clicked:
        return

    try:
        set_service_category_active(
            property_id=property_id,
            category_id=category["id"],
            active=target,
            actor_id=user["id"],
            reason=reason,
        )
    except Exception as exc:
        st.error(
            "No fue posible cambiar el estado "
            f"de la categoría: {exc}"
        )
        return

    _clear_action(property_id)
    st.success(
        "Estado de la categoría actualizado."
    )
    st.rerun()


def render_service_categories(
    *,
    property_id,
    user,
):
    st.markdown("### Categorías de Servicios")

    st.caption(
        "Clasificación configurable para los "
        "servicios del inmueble. Las categorías "
        "no determinan por sí mismas ninguna "
        "restricción financiera."
    )

    categories = list_service_categories(
        property_id=property_id,
        active_only=False,
    )

    selected_id = st.session_state.get(
        _selected_key(property_id)
    )

    if categories:
        display = pd.DataFrame(
            [
                {
                    "ID": item["id"],
                    "Categoría": item["nombre"],
                    "Código": item["codigo"],
                    "Descripción / enfoque": (
                        item["descripcion"]
                        or "Sin descripción"
                    ),
                    "Orden": item["orden"],
                    "Estado": (
                        "Activa"
                        if item["activo"]
                        else "Inactiva"
                    ),
                }
                for item in categories
            ]
        )

        event = st.dataframe(
            display,
            hide_index=True,
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config={"ID": None},
            key=(
                f"service_category_grid_"
                f"{property_id}"
            ),
        )

        if event.selection.rows:
            selected_id = categories[
                event.selection.rows[0]
            ]["id"]

            st.session_state[
                _selected_key(property_id)
            ] = selected_id

    else:
        st.info(
            "El inmueble todavía no tiene "
            "categorías de servicios."
        )

    selected = None

    if selected_id is not None:
        selected = get_service_category(
            property_id=property_id,
            category_id=selected_id,
        )

    can_manage = _can_manage(
        user,
        property_id,
    )

    buttons = st.columns(3)

    with buttons[0]:
        if st.button(
            "Nueva categoría",
            key=f"service_category_new_{property_id}",
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
            key=f"service_category_edit_{property_id}",
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
            key=f"service_category_active_{property_id}",
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

    if selected:
        st.info(
            "Categoría seleccionada: "
            + selected["nombre"]
        )

    action = st.session_state.get(
        _action_key(property_id)
    )

    if action == "CREATE":
        _render_create(
            property_id=property_id,
            user=user,
            categories=categories,
        )

    elif (
        action == "EDIT"
        and selected is not None
    ):
        _render_edit(
            property_id=property_id,
            user=user,
            category=selected,
        )

    elif (
        action == "ACTIVE"
        and selected is not None
    ):
        _render_active(
            property_id=property_id,
            user=user,
            category=selected,
        )

    if not can_manage:
        st.info(
            "El usuario puede consultar las "
            "categorías, pero no modificarlas."
        )
