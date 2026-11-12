from datetime import date
import streamlit as st
import pandas as pd
from core.db import execute
from core.auth import audit
from core.access import refresh_current_property
from core.authorization import authorize
from components.ui import title, table, property_header, clickable_image
from services.catalogs import options
from services.media import validate
from services.properties import list_properties, create_property, update_property, dependencies, deletable, delete_property, update_logo, delete_logo, update_cover, delete_cover, set_property_active, get_property
from services.property_admins import list_admins, create_admin, revoke, reactivate, reset_password, get_admin, update_admin_profile, list_assignable_admins, assign_existing_admin, admin_delete_dependencies, delete_inactive_admin
from services.property_structure import NODE_TYPES, list_nodes, create_node, update_node, set_node_active, node_path, node_dependencies, delete_node


def decision(user, permission, property_id=None):
    return authorize(user, permission, property_id)


def denied_message(permission):
    st.info(f"Tu perfil no cuenta con el permiso {permission} para esta operación.")


def form(row=None, key="p"):
    row = row or {}
    types = options("TIPO_INMUEBLE")
    conditions = options("CONDICION_FISICA")
    reverse = {value: name for name, value in types.items()}
    if not types or not conditions:
        st.error("Deben existir conceptos activos en Tipo De Inmueble y Condicion Fisica.")
        st.stop()

    col1, col2 = st.columns(2)
    clave = col1.text_input("Clave", row.get("clave", ""), key=key + "c")
    nombre = col2.text_input("Nombre", row.get("nombre", ""), key=key + "n")

    col1, col2 = st.columns(2)
    display = reverse.get(row.get("tipo_codigo"), list(types)[0])
    tipo = col1.selectbox(
        "Tipo De Inmueble",
        list(types),
        index=list(types).index(display),
        key=key + "t",
    )
    currencies = ["MXN", "USD", "EUR", "CAD"]
    current_currency = row.get("moneda_base") or "MXN"
    moneda = col2.selectbox(
        "Moneda Base",
        currencies,
        index=currencies.index(current_currency),
        key=key + "m",
    )

    construction_col, condition_col = st.columns(2)
    construction_value = row.get("fecha_construccion") or date.today()
    fecha_construccion = construction_col.date_input(
        "Fecha De Construcción",
        value=construction_value,
        max_value=date.today(),
        format="DD/MM/YYYY",
        key=key + "fc",
    )
    condition_reverse = {value: name for name, value in conditions.items()}
    condition_display = condition_reverse.get(row.get("condicion_codigo"), list(conditions)[0])
    condition_name = condition_col.selectbox(
        "Estado O Condición",
        list(conditions),
        index=list(conditions).index(condition_display),
        key=key + "cf",
    )
    years = date.today().year - fecha_construccion.year - (
        (date.today().month, date.today().day)
        < (fecha_construccion.month, fecha_construccion.day)
    )
    st.caption(f"Antigüedad calculada: {years} año(s)")

    direccion = st.text_area("Dirección", row.get("direccion") or "", key=key + "d")
    col1, col2 = st.columns(2)
    rfc = col1.text_input("RFC", row.get("rfc") or "", key=key + "r")
    zona = col2.text_input(
        "Zona Horaria",
        row.get("zona_horaria") or "America/Mexico_City",
        key=key + "z",
    )
    return {
        "clave": clave.upper().strip(),
        "nombre": nombre.strip(),
        "tipo_codigo": types[tipo],
        "moneda_base": moneda,
        "direccion": direccion,
        "rfc": rfc,
        "zona_horaria": zona,
        "fecha_construccion": fecha_construccion,
        "condicion_codigo": conditions[condition_name],
    }


def render():
    user = st.session_state.user
    title("Inmuebles", "Datos Generales, Administradores, Identidad Y Estado")
    rows = list_properties(user)
    type_options = options("TIPO_INMUEBLE")
    friendly = []
    for item in rows:
        friendly.append(
            {
                **item,
                "tipo_codigo": next(
                    (name for name, code in type_options.items() if code == item["tipo_codigo"]),
                    item["tipo_codigo"],
                ),
            }
        )
    st.subheader("Consulta Y Selección De Inmuebles")
    search_col, type_col, status_col, currency_col = st.columns([2.2, 1.3, 1.1, 1.0])
    search_text = search_col.text_input(
        "Buscar",
        key="property_grid_search",
        placeholder="Clave, nombre, dirección, RFC o tipo...",
    ).strip().casefold()
    type_values = sorted({str(item.get("tipo_codigo") or "") for item in friendly if item.get("tipo_codigo")})
    type_filter = type_col.selectbox("Tipo", ["Todos"] + type_values, key="property_grid_type")
    status_filter = status_col.selectbox("Estado", ["Todos", "Activos", "Inactivos"], key="property_grid_status")
    currency_values = sorted({str(item.get("moneda_base") or "") for item in rows if item.get("moneda_base")})
    currency_filter = currency_col.selectbox("Moneda", ["Todas"] + currency_values, key="property_grid_currency")

    filtered = []
    for raw, shown in zip(rows, friendly):
        searchable = " ".join(
            str(raw.get(field) or "")
            for field in ("clave", "nombre", "direccion", "rfc", "tipo_codigo")
        ).casefold()
        if search_text and search_text not in searchable:
            continue
        if type_filter != "Todos" and str(shown.get("tipo_codigo") or "") != type_filter:
            continue
        if status_filter == "Activos" and not raw.get("activo"):
            continue
        if status_filter == "Inactivos" and raw.get("activo"):
            continue
        if currency_filter != "Todas" and str(raw.get("moneda_base") or "") != currency_filter:
            continue
        filtered.append(raw)

    grid_rows = [
        {
            "ID": item["id"],
            "Clave": item.get("clave"),
            "Nombre": item.get("nombre"),
            "Tipo": next(
                (name for name, code in type_options.items() if code == item.get("tipo_codigo")),
                item.get("tipo_codigo"),
            ),
            "Moneda": item.get("moneda_base"),
            "Dirección": item.get("direccion"),
            "RFC": item.get("rfc"),
            "Fecha De Construcción": item.get("fecha_construccion"),
            "Antigüedad": (
                date.today().year - item["fecha_construccion"].year -
                ((date.today().month, date.today().day) <
                 (item["fecha_construccion"].month, item["fecha_construccion"].day))
            ) if item.get("fecha_construccion") else None,
            "Condición": item.get("condicion_codigo"),
            "Estado": "Activo" if item.get("activo") else "Inactivo",
        }
        for item in filtered
    ]
    st.caption(f"{len(grid_rows)} inmueble(s) encontrado(s). Selecciona una fila para gestionarla.")
    grid_event = st.dataframe(
        pd.DataFrame(grid_rows),
        hide_index=True,
        use_container_width=True,
        column_config={"ID": None},
        on_select="rerun",
        selection_mode="single-row",
        key="property_management_grid",
    )

    selected_rows = list(getattr(getattr(grid_event, "selection", None), "rows", []) or [])
    if selected_rows:
        selected_index = selected_rows[0]
        if 0 <= selected_index < len(filtered):
            selected_property = filtered[selected_index]
            newly_selected_id = selected_property["id"]
            st.session_state.inmueble_gestion_id = newly_selected_id
            # Only an online property may become the global active context.
            # An offline property remains selected for management/reactivation.
            if selected_property.get("activo"):
                if st.session_state.get("condominio_id") != newly_selected_id:
                    st.session_state.condominio_id = newly_selected_id
                    st.session_state.inmueble_gestion_id = newly_selected_id
                    refresh_current_property(newly_selected_id)
                    st.rerun()
            else:
                if st.session_state.get("condominio_id") == newly_selected_id:
                    st.session_state.pop("condominio_id", None)
                    st.session_state.pop("condominio", None)

    all_by_id = {item["id"]: item for item in rows}
    selected_id = st.session_state.get("inmueble_gestion_id")
    if selected_id not in all_by_id:
        selected_id = None
        st.session_state.pop("inmueble_gestion_id", None)
        st.session_state.pop("condominio_id", None)
        st.session_state.pop("condominio", None)
    selected_row = all_by_id.get(selected_id)

    if selected_row:
        visible_in_filter = any(item["id"] == selected_id for item in filtered)
        st.success(f"Gestionando: {selected_row['clave']} · {selected_row['nombre']}")
        if not visible_in_filter:
            st.warning("El inmueble seleccionado no se encuentra dentro de los resultados del filtro. La selección se conserva para evitar cambiar de registro silenciosamente.")

    labels = {f"{item['clave']} - {item['nombre']}": item for item in rows}

    if user.get("rol_global") == "SUPERADMIN":
        action_col, spacer_col = st.columns([1.35, 8.65])
        if action_col.button(
            "+ Alta De Inmueble",
            type="primary",
            use_container_width=True,
            key="property_create_open",
        ):
            st.session_state.property_create_mode = True
    else:
        st.session_state.property_create_mode = False

    if st.session_state.get("property_create_mode"):
        st.subheader("Alta De Inmueble")
        if st.button("Cancelar Alta", key="property_create_cancel"):
            st.session_state.property_create_mode = False
            st.rerun()
        access = decision(user, "INMUEBLE_CREAR")
        if not access.allowed:
            denied_message("INMUEBLE_CREAR")
        else:
            with st.form("new"):
                values = form(key="n")
                submitted = st.form_submit_button("Crear Inmueble", type="primary")
            if submitted:
                if not values["clave"] or not values["nombre"]:
                    st.error("Clave Y Nombre Son Obligatorios.")
                else:
                    try:
                        record = create_property(
                            user["id"],
                            values,
                        )
                        audit("INMUEBLE_CREAR", "condominios", record["id"], after=values)
                        st.session_state.property_create_mode = False
                        st.success("Inmueble creado correctamente.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"No fue posible crear el inmueble. Verifica que la clave no esté duplicada. Detalle: {exc}")

    if not labels:
        return

    if not selected_row:
        if not st.session_state.get("property_create_mode"):
            st.caption("Selecciona una fila del grid para mostrar las opciones de gestión del inmueble.")
        return

    if not st.session_state.get("property_create_mode"):
        section_names = ["Datos Generales", "Estructura", "Administradores", "Identidad", "Áreas Comunes", "Planos", "Estado", "Eliminar"]
        section = st.radio(
            "Gestion Del Inmueble",
            section_names,
            horizontal=True,
            key="property_management_section",
            label_visibility="collapsed",
        )
    else:
        return

    if section == "Datos Generales":
        row = selected_row
        if row is None:
            st.info("Selecciona primero un inmueble en el grid superior.")
            st.stop()
        property_header(row)
        access = decision(user, "INMUEBLE_MODIFICAR", row["id"])
        if not access.allowed:
            denied_message("INMUEBLE_MODIFICAR")
        else:
            with st.form(f"edit_{row['id']}"):
                values = form(row, f"e_{row['id']}")
                submitted = st.form_submit_button("Guardar Cambios", type="primary")
            if submitted:
                try:
                    update_property(
                        row["id"],
                        values,
                        user["id"],
                    )
                    audit("INMUEBLE_MODIFICAR", "condominios", row["id"], before=row, after=values)
                    st.success("Cambios guardados correctamente.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"No fue posible guardar los cambios. Detalle: {exc}")

    if section == "Estructura":
        row = selected_row
        if row is None:
            st.info("Selecciona primero un inmueble en el grid superior.")
        else:
            st.subheader("Estructura Del Inmueble")
            nodes=list_nodes(row["id"])
            grid_rows=[{"ID":n["id"],"Clave":n.get("clave") or "","Nombre":n.get("nombre"),"Tipo":n.get("tipo_codigo"),"Ubicación":node_path(nodes,n["id"]),"Descripción":n.get("descripcion") or "","Estado":"Activo" if n.get("activo") else "Inactivo"} for n in nodes]
            if grid_rows:
                event=st.dataframe(pd.DataFrame(grid_rows),hide_index=True,use_container_width=True,column_config={"ID":None},on_select="rerun",selection_mode="single-row",key=f"structure_management_grid_{row['id']}")
                indexes=list(getattr(getattr(event,"selection",None),"rows",[]) or [])
                selected_node=nodes[indexes[0]] if indexes and 0<=indexes[0]<len(nodes) else None
            else:
                selected_node=None; st.info("Este inmueble todavía no tiene estructuras registradas.")

            type_labels={"Conjunto Urbano":"CONJUNTO_URBANO","Fraccionamiento":"FRACCIONAMIENTO","Privada":"PRIVADA","Edificio":"EDIFICIO","Torre":"TORRE","Sección":"SECCION","Zona":"ZONA"}
            reverse_types={v:k for k,v in type_labels.items()}
            if selected_node:
                st.markdown("### Gestionar Estructura")
                st.success(f"Gestionando: {node_path(nodes,selected_node['id'])}")
                management=st.radio("Gestión",["Editar","Cambiar Estado","Eliminar"],horizontal=True,key=f"structure_action_{row['id']}_{selected_node['id']}",label_visibility="collapsed")
                parent_candidates=[n for n in nodes if n["id"]!=selected_node["id"] and n.get("activo")]
                parent_map={"Nivel raíz del inmueble":None}|{f"{node_path(nodes,n['id'])} · {n['tipo_codigo']}":n["id"] for n in parent_candidates}
                if management=="Editar":
                    access=decision(user,"ESTRUCTURA_MODIFICAR",row["id"])
                    if not access.allowed: denied_message("ESTRUCTURA_MODIFICAR")
                    else:
                        current_type=reverse_types.get(selected_node["tipo_codigo"],list(type_labels)[0])
                        current_parent=next((k for k,val in parent_map.items() if val==selected_node.get("parent_id")),"Nivel raíz del inmueble")
                        with st.form(f"structure_edit_{selected_node['id']}"):
                            c1,c2=st.columns(2)
                            t=c1.selectbox("Tipo De Estructura",list(type_labels),index=list(type_labels).index(current_type))
                            p=c2.selectbox("Estructura Padre",list(parent_map),index=list(parent_map).index(current_parent))
                            clave=st.text_input("Clave",selected_node.get("clave") or "")
                            nombre=st.text_input("Nombre",selected_node.get("nombre") or "")
                            desc=st.text_area("Descripción",selected_node.get("descripcion") or "")
                            save=st.form_submit_button("Guardar Cambios",type="primary")
                        if save:
                            if not nombre.strip(): st.error("El nombre es obligatorio.")
                            else:
                                update_node(row["id"],selected_node["id"],nombre.strip(),clave.strip() or None,desc.strip() or None,type_labels[t],parent_map[p],user["id"]); audit("ESTRUCTURA_MODIFICAR","estructura_inmueble",selected_node["id"]); st.rerun()
                elif management=="Cambiar Estado":
                    target=not selected_node.get("activo"); permission="ESTRUCTURA_REACTIVAR" if target else "ESTRUCTURA_DESACTIVAR"
                    if not decision(user,permission,row["id"]).allowed: denied_message(permission)
                    elif st.button("Reactivar Estructura" if target else "Desactivar Estructura",type="primary"):
                        set_node_active(row["id"],selected_node["id"],target,user["id"]); audit(permission,"estructura_inmueble",selected_node["id"]); st.rerun()
                else:
                    deps=node_dependencies(row["id"],selected_node["id"],user["id"]) or {}
                    st.write(f"Estructuras hijas: {deps.get('hijos',0)} · Espacios vinculados: {deps.get('espacios',0)}")
                    can_delete=sum(deps.values())==0
                    if not can_delete: st.warning("No se puede eliminar mientras existan estructuras hijas o espacios vinculados.")
                    confirm=st.checkbox("Confirmo la eliminación permanente",disabled=not can_delete,key=f"structure_delete_confirm_{selected_node['id']}")
                    if not decision(user,"ESTRUCTURA_ELIMINAR",row["id"]).allowed: denied_message("ESTRUCTURA_ELIMINAR")
                    elif st.button("Eliminar Estructura",disabled=not(can_delete and confirm),type="primary"):
                        if delete_node(row["id"],selected_node["id"],user["id"]): audit("ESTRUCTURA_ELIMINAR","estructura_inmueble",selected_node["id"]); st.rerun()
            else:
                st.caption("Selecciona una fila del grid para editar, cambiar su estado o eliminarla.")

            with st.expander("Agregar Estructura",expanded=not bool(nodes)):
                if not decision(user,"ESTRUCTURA_CREAR",row["id"]).allowed: denied_message("ESTRUCTURA_CREAR")
                else:
                    parent_map={"Nivel raíz del inmueble":None}|{f"{node_path(nodes,n['id'])} · {n['tipo_codigo']}":n["id"] for n in nodes if n.get("activo")}
                    with st.form(f"structure_add_{row['id']}"):
                        c1,c2=st.columns(2); t=c1.selectbox("Tipo De Estructura",list(type_labels)); p=c2.selectbox("Estructura Padre",list(parent_map)); clave=st.text_input("Clave"); nombre=st.text_input("Nombre"); desc=st.text_area("Descripción"); add=st.form_submit_button("Agregar Estructura",type="primary")
                    if add:
                        if not nombre.strip(): st.error("El nombre es obligatorio.")
                        else: create_node(row["id"],type_labels[t],nombre.strip(),clave.strip() or None,parent_map[p],desc.strip() or None,user["id"]); audit("ESTRUCTURA_CREAR","estructura_inmueble",detail=f"Inmueble {row['id']}"); st.rerun()

    if section == "Administradores":
        row = selected_row

        if row is None:
            st.info("Selecciona primero un inmueble en el grid superior.")
            st.stop()

        access = decision(user, "ADMINISTRADOR_ASIGNAR", row["id"])

        if not access.allowed:
            denied_message("ADMINISTRADOR_ASIGNAR")

        else:
            admins = list_admins(row["id"])

            admin_grid_rows = [
                {
                    "ID": a["id"],
                    "Usuario": a.get("username"),
                    "Nombre": a.get("nombre"),
                    "Correo Electrónico": a.get("email"),
                    "Tel. Of / Casa": a.get("telefono_of_casa"),
                    "Tel. Celular": a.get("telefono_celular"),
                    "Origen": a.get("origen_codigo"),
                    "Rol": a.get("rol_codigo"),
                    "Estado": "Activo" if a.get("activo") else "Inactivo",
                    "Asignación Activa": bool(a.get("asignacion_activa")),
                }
                for a in admins
            ]

            st.caption(
                f"{len(admin_grid_rows)} administrador(es). "
                "Selecciona una fila para gestionarla."
            )

            admin_event = st.dataframe(
                pd.DataFrame(admin_grid_rows),
                hide_index=True,
                use_container_width=True,
                column_config={"ID": None},
                on_select="rerun",
                selection_mode="single-row",
                key=f"admin_management_grid_{row['id']}",
            )

            admin_selected_rows = list(
                getattr(getattr(admin_event, "selection", None), "rows", []) or []
            )

            if admin_selected_rows:
                admin_index = admin_selected_rows[0]
                if 0 <= admin_index < len(admins):
                    st.session_state.admin_gestion_id = admins[admin_index]["id"]

            admin_by_id = {a["id"]: a for a in admins}
            admin_id = st.session_state.get("admin_gestion_id")

            if admin_id not in admin_by_id:
                admin_id = None
                st.session_state.pop("admin_gestion_id", None)

            if admins and admin_id is not None:

                st.subheader("Gestionar Administrador")

                admin = get_admin(row["id"], admin_id, user["id"])

                st.success(
                    f"Gestionando Administrador: "
                    f"{admin['username']} · {admin['nombre']}"
                )

                # ==============================================
                # DATOS DEL ADMINISTRADOR
                # ==============================================

                st.markdown("#### Datos Del Administrador")

                origin_options = options("ORIGEN_ADMIN")

                origin_reverse = {
                    value: name
                    for name, value in origin_options.items()
                }

                with st.form(
                    f"admin_profile_{row['id']}_{admin['id']}"
                ):

                    c1, c2 = st.columns(2)

                    admin_username = c1.text_input(
                        "Usuario",
                        admin.get("username") or "",
                    )

                    admin_nombre = c2.text_input(
                        "Nombre",
                        admin.get("nombre") or "",
                    )

                    admin_email = st.text_input(
                        "Correo Electrónico",
                        admin.get("email") or "",
                    )

                    c1, c2 = st.columns(2)

                    tel_of = c1.text_input(
                        "Tel. Of / Casa",
                        admin.get("telefono_of_casa") or "",
                    )

                    tel_cel = c2.text_input(
                        "Tel. Celular",
                        admin.get("telefono_celular") or "",
                    )

                    admin_direccion = st.text_area(
                        "Dirección",
                        admin.get("direccion") or "",
                    )

                    origin_names = (
                        list(origin_options)
                        or ["Empresa", "Inquilino", "Privado"]
                    )

                    current_origin = origin_reverse.get(
                        admin.get("origen_codigo"),
                        origin_names[0],
                    )

                    origin_name = st.selectbox(
                        "Origen",
                        origin_names,
                        index=origin_names.index(current_origin),
                    )

                    save_admin = st.form_submit_button(
                        "Guardar Datos Del Administrador",
                        type="primary",
                    )

                if save_admin:

                    if not admin_username.strip():
                        st.error("Usuario es obligatorio.")

                    elif not admin_nombre.strip():
                        st.error("Nombre es obligatorio.")

                    else:

                        try:

                            origin_code = origin_options.get(
                                origin_name,
                                origin_name.upper(),
                            )

                            before = {
                                k: admin.get(k)
                                for k in (
                                    "username",
                                    "nombre",
                                    "email",
                                    "telefono_of_casa",
                                    "telefono_celular",
                                    "direccion",
                                    "origen_codigo",
                                )
                            }

                            update_admin_profile(
                                row["id"],
                                admin["id"],
                                admin_username.strip(),
                                admin_nombre.strip(),
                                admin_email.strip(),
                                tel_of.strip(),
                                tel_cel.strip(),
                                admin_direccion.strip(),
                                origin_code,
                                user["id"],
                            )

                            audit(
                                "ADMINISTRADOR_MODIFICAR",
                                "usuarios",
                                admin["id"],
                                before=before,
                                after={
                                    "username": admin_username.strip(),
                                    "nombre": admin_nombre.strip(),
                                    "email": admin_email.strip(),
                                    "telefono_of_casa": tel_of.strip(),
                                    "telefono_celular": tel_cel.strip(),
                                    "direccion": admin_direccion.strip(),
                                    "origen_codigo": origin_code,
                                },
                            )

                            st.success(
                                "Datos del administrador actualizados correctamente."
                            )

                            st.rerun()

                        except Exception as exc:

                            st.error(
                                "No fue posible actualizar el administrador. "
                                "Verifica que el Usuario no esté duplicado. "
                                f"Detalle: {exc}"
                            )

                # ==============================================
                # ACCESO DEL MISMO ADMINISTRADOR
                # ==============================================

                st.markdown("#### Acceso Del Administrador")

                st.caption(
                    f"Las siguientes acciones aplican a "
                    f"{admin['nombre']} · {admin['username']}"
                )

                c1, c2, c3 = st.columns(
                    [1, 1, 1.5]
                )

                revoke_access = decision(user, "ADMINISTRADOR_REVOCAR", row["id"])
                if c1.button(
                    "Eliminar / Revocar Del Inmueble",
                    disabled=not revoke_access.allowed,
                    key=f"revoke_{row['id']}_{admin['id']}",
                ):

                    revoke(
                        row["id"],
                        admin["id"],
                        user["id"],
                    )

                    audit(
                        "ADMINISTRADOR_REVOCAR",
                        "usuarios",
                        admin["id"],
                        detail=f"Inmueble {row['id']}",
                    )

                    st.rerun()

                if c2.button(
                    "Reactivar Asignación",
                    key=f"reactivate_{row['id']}_{admin['id']}",
                ):

                    reactivate(
                        row["id"],
                        admin["id"],
                        user["id"],
                    )

                    audit(
                        "ADMINISTRADOR_REACTIVAR",
                        "usuarios",
                        admin["id"],
                        detail=f"Inmueble {row['id']}",
                    )

                    st.rerun()

                with c3:

                    new_password = st.text_input(
                        "Nueva Contraseña",
                        type="password",
                        key=f"pwd_{row['id']}_{admin['id']}",
                    )

                    if st.button(
                        "Restablecer",
                        key=f"resetpwd_{row['id']}_{admin['id']}",
                    ):

                        try:

                            reset_password(
                                row["id"],
                                admin["id"],
                                new_password,
                                user["id"],
                            )

                            audit(
                                "ADMINISTRADOR_PASSWORD_RESET",
                                "usuarios",
                                admin["id"],
                            )

                            st.success(
                                "Contraseña restablecida correctamente."
                            )

                            st.rerun()

                        except ValueError:

                            st.error(
                                "La contraseña no cumple la política de seguridad. "
                                "Usa al menos 10 caracteres, una letra mayúscula y un número."
                            )

                # ==============================================
                # ELIMINACION DEFINITIVA DE LA IDENTIDAD
                # ==============================================
                st.markdown("#### Eliminar Administrador De La Base De Datos")
                delete_access = decision(user, "ADMINISTRADOR_ELIMINAR", row["id"])
                delete_deps = admin_delete_dependencies(admin["id"]) or {}
                active_assignments = int(delete_deps.get("asignaciones_activas", 0))
                space_assignments = int(delete_deps.get("espacios", 0))
                can_delete_identity = (
                    delete_access.allowed
                    and admin["id"] != user["id"]
                    and admin.get("rol_global") != "SUPERADMIN"
                    and active_assignments == 0
                    and space_assignments == 0
                )
                st.caption(
                    "Esta acción elimina definitivamente la cuenta, sus asignaciones históricas "
                    "y sus códigos de recuperación. No puede deshacerse."
                )
                st.write(
                    f"Asignaciones activas: {active_assignments} · "
                    f"Asignaciones totales: {int(delete_deps.get('asignaciones_totales', 0))} · "
                    f"Espacios asignados: {space_assignments}"
                )
                if not delete_access.allowed:
                    denied_message("ADMINISTRADOR_ELIMINAR")
                elif admin["id"] == user["id"]:
                    st.warning("No puedes eliminar la cuenta con la que has iniciado sesión.")
                elif admin.get("rol_global") == "SUPERADMIN":
                    st.warning("No se puede eliminar una cuenta SuperAdmin desde este módulo.")
                elif active_assignments:
                    st.warning("Primero revoca al administrador de todos los inmuebles activos.")
                elif space_assignments:
                    st.warning("El administrador tiene espacios asignados y no puede eliminarse.")
                confirmation = st.text_input(
                    f"Escribe {admin['username']} para confirmar la eliminación definitiva",
                    key=f"delete_admin_confirmation_{admin['id']}",
                    disabled=not can_delete_identity,
                )
                if st.button(
                    "Eliminar Administrador Definitivamente",
                    type="primary",
                    disabled=not (can_delete_identity and confirmation == admin["username"]),
                    key=f"delete_admin_permanent_{admin['id']}",
                ):
                    before={"id":admin["id"],"username":admin["username"],"nombre":admin["nombre"],"email":admin.get("email")}
                    delete_inactive_admin(admin["id"],user["id"])
                    audit("ADMINISTRADOR_ELIMINAR","usuarios",admin["id"],before=before)
                    st.session_state.pop("admin_gestion_id",None)
                    st.success("Administrador eliminado definitivamente.")
                    st.rerun()

            elif admins:

                st.info(
                    "Selecciona una fila del grid de Administradores "
                    "para gestionar sus datos y accesos."
                )

            else:

                st.info(
                    "Este inmueble no tiene administradores asignados."
                )

            # ==================================================
            # ASIGNAR ADMINISTRADOR EXISTENTE
            # ==================================================

            with st.expander("Asignar Administrador Existente"):
                assign_access = decision(
                    user,
                    "ADMINISTRADOR_ASIGNAR",
                    row["id"],
                )
                if not assign_access.allowed:
                    denied_message("ADMINISTRADOR_ASIGNAR")
                else:
                    candidates = list_assignable_admins(row["id"], user["id"])
                    if not candidates:
                        st.info(
                            "No hay administradores existentes disponibles "
                            "para asignar a este inmueble."
                        )
                    else:
                        candidate_map = {
                            f"{item['nombre']} · {item['username']} · "
                            f"{item.get('email') or 'Sin correo'}": item
                            for item in candidates
                        }
                        selected_candidate = st.selectbox(
                            "Administrador existente",
                            list(candidate_map),
                            key=f"existing_admin_{row['id']}",
                        )
                        candidate = candidate_map[selected_candidate]
                        if candidate.get("asignacion_actual_activa") is False:
                            st.caption(
                                "La asignación anterior está revocada y será reactivada."
                            )
                        else:
                            st.caption(
                                "Se conservarán el mismo usuario, contraseña y perfil."
                            )
                        if st.button(
                            "Asignar Al Inmueble",
                            type="primary",
                            key=f"assign_existing_admin_{row['id']}",
                        ):
                            try:
                                result = assign_existing_admin(
                                    row["id"],
                                    candidate["id"],
                                    user["id"],
                                )
                                action = (
                                    "ADMINISTRADOR_REACTIVAR"
                                    if result["status"] == "REACTIVATED"
                                    else "ADMINISTRADOR_ASIGNAR"
                                )
                                audit(
                                    action,
                                    "usuario_inmuebles",
                                    candidate["id"],
                                    detail=f"Inmueble {row['id']}",
                                    after={
                                        "usuario_id": candidate["id"],
                                        "condominio_id": row["id"],
                                        "rol_codigo": "ADMINISTRADOR",
                                        "status": result["status"],
                                    },
                                )
                                if result["status"] == "ALREADY_ACTIVE":
                                    st.info(
                                        "El administrador ya tiene una asignación "
                                        "activa en este inmueble."
                                    )
                                elif result["status"] == "REACTIVATED":
                                    st.success(
                                        "Asignación reactivada correctamente, sin "
                                        "crear otra identidad."
                                    )
                                else:
                                    st.success(
                                        "Administrador existente asignado correctamente."
                                    )
                                st.rerun()
                            except ValueError:
                                st.error(
                                    "La identidad seleccionada ya no está disponible."
                                )

            # ==================================================
            # NUEVO ADMINISTRADOR
            # ==================================================

            with st.expander("Nuevo Administrador"):

                st.caption(
                    "La contraseña debe tener al menos 10 caracteres, "
                    "una mayúscula y un número."
                )

                with st.form(
                    f"newadmin_{row['id']}"
                ):

                    nombre = st.text_input(
                        "Nombre",
                        key=f"newadmin_nombre_{row['id']}",
                    )

                    email = st.text_input(
                        "Correo Electrónico",
                        key=f"newadmin_email_{row['id']}",
                    )

                    username = st.text_input(
                        "Usuario",
                        key=f"newadmin_username_{row['id']}",
                    )

                    password = st.text_input(
                        "Contraseña Inicial",
                        type="password",
                        key=f"newadmin_password_{row['id']}",
                    )

                    submitted = st.form_submit_button(
                        "Crear Y Asignar"
                    )

                if submitted:

                    if (
                        not nombre
                        or not email
                        or not username
                        or not password
                    ):

                        st.error(
                            "Nombre, correo, usuario y contraseña "
                            "son obligatorios."
                        )

                    else:

                        try:

                            create_admin(
                                row["id"],
                                nombre,
                                email,
                                username,
                                password,
                                user["id"],
                            )

                            audit(
                                "ADMINISTRADOR_CREAR",
                                "usuarios",
                                detail=(
                                    f"Inmueble {row['id']} · {username}"
                                ),
                            )

                            st.success(
                                "Administrador creado y asignado correctamente."
                            )

                            st.rerun()

                        except ValueError:

                            st.error(
                                "La contraseña no cumple la política de seguridad. "
                                "Usa al menos 10 caracteres, una letra mayúscula y un número."
                            )

                        except Exception as exc:

                            st.error(
                                "No fue posible crear el administrador. "
                                f"Detalle: {exc}"
                            )

    if section == "Identidad":
        row = selected_row
        if row is None:
            st.info("Selecciona primero un inmueble en el grid superior.")
            st.stop()
        property_header(row)
        access = decision(user, "INMUEBLE_BRANDING", row["id"])
        if not access.allowed:
            denied_message("INMUEBLE_BRANDING")
        else:
            st.subheader("Logotipo")
            if row.get("logo_data"):
                clickable_image(row["logo_data"], row.get("logo_mime") or "image/png", f"Logotipo - {row['nombre']}", width=140, max_height=100)
            logo = st.file_uploader("Nuevo Logotipo", type=["jpg", "jpeg", "png", "bmp"], key="property_logo")
            c1, c2 = st.columns(2)
            if c1.button("Guardar / Cambiar Logotipo", disabled=logo is None):
                try:
                    media = validate(logo, 2)
                    action = "INMUEBLE_LOGO_CAMBIO" if row.get("logo_data") else "INMUEBLE_LOGO_ALTA"
                    update_logo(row["id"], media["data"], media["mime"], user["id"])
                    audit(action, "condominios", row["id"], after={"mime": media["mime"], "name": media["name"]})
                    refresh_current_property(row["id"])
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
            delete_logo_confirm = c2.checkbox("Confirmo eliminar logotipo", key="delete_logo_confirm")
            if c2.button("Eliminar Logotipo", disabled=not (delete_logo_confirm and row.get("logo_data"))):
                delete_logo(row["id"], user["id"]);audit("INMUEBLE_LOGO_BAJA", "condominios", row["id"]);refresh_current_property(row["id"]);st.rerun()
            st.divider()
            st.subheader("Portada / Imagen De Identidad")
            if row.get("portada_data"):
                clickable_image(row["portada_data"], row.get("portada_mime") or "image/jpeg", f"Portada - {row['nombre']}", width=220, max_height=125)
            cover = st.file_uploader("Nueva Portada", type=["jpg", "jpeg", "png", "bmp"], key="property_cover")
            c1, c2 = st.columns(2)
            if c1.button("Guardar / Cambiar Portada", disabled=cover is None):
                try:
                    media = validate(cover, 5)
                    action = "INMUEBLE_PORTADA_CAMBIO" if row.get("portada_data") else "INMUEBLE_PORTADA_ALTA"
                    update_cover(row["id"], media["data"], media["mime"], user["id"])
                    audit(action, "condominios", row["id"], after={"mime": media["mime"], "name": media["name"]})
                    refresh_current_property(row["id"])
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
            delete_cover_confirm = c2.checkbox("Confirmo eliminar portada", key="delete_cover_confirm")
            if c2.button("Eliminar Portada", disabled=not (delete_cover_confirm and row.get("portada_data"))):
                delete_cover(row["id"], user["id"]);audit("INMUEBLE_PORTADA_BAJA", "condominios", row["id"]);refresh_current_property(row["id"]);st.rerun()

    if section == "Áreas Comunes":
        st.subheader("Áreas Comunes")
        st.info("Apartado estructural del inmueble. Funcionalidad operativa pendiente de asignación a un Build futuro.")

    if section == "Planos":
        st.subheader("Planos")
        st.info("Apartado estructural del inmueble. Funcionalidad documental y gráfica pendiente de asignación a un Build futuro.")

    if section == "Estado":
        row = selected_row
        if row is None:
            st.info("Selecciona primero un inmueble en el grid superior.")
            st.stop()
        permission = "INMUEBLE_DESACTIVAR" if row["activo"] else "INMUEBLE_REACTIVAR"
        access = decision(user, permission, row["id"])
        if not access.allowed:
            denied_message(permission)
        else:
            is_active = bool(row["activo"])
            action = "Poner Offline" if is_active else "Reactivar Inmueble"
            target_state = not is_active
            if is_active:
                st.warning(
                    "Esta acción pondrá el inmueble temporalmente Offline. "
                    "No elimina información y podrá reactivarse posteriormente."
                )
                confirmation_text = "Confirmo que deseo poner este inmueble Offline temporalmente."
            else:
                st.info(
                    "La reactivación devolverá el inmueble al estado Activo y permitirá "
                    "usarlo nuevamente como contexto operativo."
                )
                confirmation_text = "Confirmo que deseo reactivar este inmueble."

            confirm = st.checkbox(
                confirmation_text,
                key=f"confirm_state_{row['id']}_{int(target_state)}",
            )
            if st.button(
                action,
                disabled=not confirm,
                key=f"change_state_{row['id']}_{int(target_state)}",
                type="primary" if target_state else "secondary",
            ):
                set_property_active(
                    row["id"],
                    target_state,
                    user["id"],
                )
                audit(
                    permission,
                    "condominios",
                    row["id"],
                    before={"activo": is_active},
                    after={"activo": target_state},
                    detail="Reactivación" if target_state else "Offline temporal",
                )
                st.session_state.inmueble_gestion_id = row["id"]
                if not target_state:
                    st.session_state.pop("condominio_id", None)
                    st.session_state.pop("condominio", None)
                st.success(
                    "Inmueble reactivado correctamente."
                    if target_state
                    else "Inmueble puesto Offline temporalmente."
                )
                st.rerun()

    if section == "Eliminar":
        row = selected_row
        if row is None:
            st.info("Selecciona primero un inmueble en el grid superior.")
            st.stop()
        access = decision(user, "INMUEBLE_ELIMINAR", row["id"])
        if not access.allowed:
            denied_message("INMUEBLE_ELIMINAR")
        else:
            deps = dependencies(row["id"], user["id"])
            st.write("Dependencias", deps)
            if deletable(row["id"], user["id"]):
                confirm = st.checkbox("Confirmo La Eliminación Permanente")
                if st.button("Eliminar Inmueble", disabled=not confirm):
                    audit("INMUEBLE_ELIMINAR", "condominios", row["id"], before=row)
                    delete_property(
                        row["id"],
                        user["id"],
                    )
                    st.rerun()
            else:
                st.warning("Este Inmueble Tiene Registros Relacionados. Utiliza Desactivar.")
