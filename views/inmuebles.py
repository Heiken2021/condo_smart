import streamlit as st
from core.db import execute
from core.auth import audit
from core.access import refresh_current_property
from core.authorization import authorize
from components.ui import title, table, property_header, clickable_image
from services.catalogs import options
from services.media import validate
from services.properties import list_properties, dependencies, deletable, update_logo, delete_logo, update_cover, delete_cover, get_property
from services.property_admins import list_admins, create_admin, revoke, reactivate, reset_password


def decision(user, permission, property_id=None):
    return authorize(user, permission, property_id)


def denied_message(permission):
    st.info(f"Tu perfil no cuenta con el permiso {permission} para esta operación.")


def form(row=None, key="p"):
    row = row or {}
    types = options("TIPO_INMUEBLE")
    reverse = {value: name for name, value in types.items()}
    if not types:
        st.error("No existen conceptos activos en el catálogo Tipo De Inmueble.")
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
    }


def render():
    user = st.session_state.user
    title("Inmuebles", "Datos Generales, Administradores, Identidad Y Estado")
    rows = list_properties()
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
    table(
        friendly,
        "condominios",
        ["clave", "nombre", "tipo_codigo", "moneda_base", "direccion", "rfc", "zona_horaria", "activo"],
    )

    labels = {f"{item['clave']} - {item['nombre']}": item for item in rows}
    tabs = st.tabs(["Alta", "Datos Generales", "Administradores", "Identidad", "Estado", "Eliminar"])

    with tabs[0]:
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
                        record = execute(
                            "INSERT INTO condominios(clave,nombre,tipo_codigo,direccion,rfc,moneda_base,zona_horaria) VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                            (
                                values["clave"], values["nombre"], values["tipo_codigo"],
                                values["direccion"], values["rfc"], values["moneda_base"], values["zona_horaria"],
                            ),
                            True,
                        )
                        audit("INMUEBLE_CREAR", "condominios", record["id"], after=values)
                        st.success("Inmueble creado correctamente.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"No fue posible crear el inmueble. Verifica que la clave no esté duplicada. Detalle: {exc}")

    if not labels:
        return

    with tabs[1]:
        selected = st.selectbox("Inmueble", list(labels), key="gen")
        row = labels[selected]
        property_header(row)
        access = decision(user, "INMUEBLE_MODIFICAR", row["id"])
        if not access.allowed:
            denied_message("INMUEBLE_MODIFICAR")
        else:
            with st.form("edit"):
                values = form(row, "e")
                submitted = st.form_submit_button("Guardar Cambios", type="primary")
            if submitted:
                try:
                    execute(
                        "UPDATE condominios SET clave=%s,nombre=%s,tipo_codigo=%s,moneda_base=%s,direccion=%s,rfc=%s,zona_horaria=%s,actualizado_en=NOW() WHERE id=%s",
                        (
                            values["clave"], values["nombre"], values["tipo_codigo"], values["moneda_base"],
                            values["direccion"], values["rfc"], values["zona_horaria"], row["id"],
                        ),
                    )
                    audit("INMUEBLE_MODIFICAR", "condominios", row["id"], before=row, after=values)
                    st.success("Cambios guardados correctamente.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"No fue posible guardar los cambios. Detalle: {exc}")

    with tabs[2]:
        selected = st.selectbox("Inmueble", list(labels), key="admins")
        row = labels[selected]
        access = decision(user, "ADMINISTRADOR_ASIGNAR", row["id"])
        if not access.allowed:
            denied_message("ADMINISTRADOR_ASIGNAR")
        else:
            admins = list_admins(row["id"])
            table(admins, "usuarios", ["username", "nombre", "email", "rol_codigo", "activo", "asignacion_activa"])

            with st.expander("Nuevo Administrador"):
                st.caption("La contraseña debe tener al menos 10 caracteres, una mayúscula y un número.")
                with st.form("newadmin"):
                    nombre = st.text_input("Nombre")
                    email = st.text_input("Correo Electrónico")
                    username = st.text_input("Usuario")
                    password = st.text_input("Contraseña Inicial", type="password")
                    submitted = st.form_submit_button("Crear Y Asignar")
                if submitted:
                    if not nombre or not email or not username or not password:
                        st.error("Nombre, Correo Electrónico, Usuario Y Contraseña Son Obligatorios.")
                    else:
                        try:
                            created = create_admin(row["id"], nombre, email, username, password, user["id"])
                            audit("ADMINISTRADOR_CREAR", "usuarios", created["id"], after={"condominio_id": row["id"]})
                            st.success("Administrador creado y asignado correctamente.")
                            st.rerun()
                        except ValueError:
                            st.error("La contraseña no cumple la política de seguridad. Usa al menos 10 caracteres, una letra mayúscula y un número.")
                        except Exception as exc:
                            st.error(f"No fue posible crear el administrador. Verifica que el usuario y el correo no estén duplicados. Detalle: {exc}")

            if admins:
                admin_map = {f"{item['username']} - {item['nombre']}": item for item in admins}
                selected_admin = st.selectbox("Administrar Acceso", list(admin_map))
                admin = admin_map[selected_admin]
                col1, col2, col3 = st.columns(3)
                if col1.button("Revocar Del Inmueble"):
                    revoke(row["id"], admin["id"], user["id"])
                    audit("ADMINISTRADOR_REVOCAR", "usuarios", admin["id"])
                    st.rerun()
                if col2.button("Reactivar Asignación"):
                    reactivate(row["id"], admin["id"], user["id"])
                    audit("ADMINISTRADOR_REACTIVAR", "usuarios", admin["id"])
                    st.rerun()
                new_password = col3.text_input("Nueva Contraseña", type="password", key="rpw")
                if col3.button("Restablecer") and new_password:
                    try:
                        reset_password(admin["id"], new_password)
                        audit("ADMINISTRADOR_PASSWORD_RESET", "usuarios", admin["id"])
                        st.success("Contraseña restablecida correctamente.")
                        st.rerun()
                    except ValueError:
                        st.error("La contraseña no cumple la política de seguridad. Usa al menos 10 caracteres, una letra mayúscula y un número.")

    with tabs[3]:
        selected = st.selectbox("Inmueble", list(labels), key="brand")
        row = labels[selected]
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
                    update_logo(row["id"], media["data"], media["mime"])
                    audit(action, "condominios", row["id"], after={"mime": media["mime"], "name": media["name"]})
                    refresh_current_property(row["id"])
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
            delete_logo_confirm = c2.checkbox("Confirmo eliminar logotipo", key="delete_logo_confirm")
            if c2.button("Eliminar Logotipo", disabled=not (delete_logo_confirm and row.get("logo_data"))):
                delete_logo(row["id"]);audit("INMUEBLE_LOGO_BAJA", "condominios", row["id"]);refresh_current_property(row["id"]);st.rerun()
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
                    update_cover(row["id"], media["data"], media["mime"])
                    audit(action, "condominios", row["id"], after={"mime": media["mime"], "name": media["name"]})
                    refresh_current_property(row["id"])
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
            delete_cover_confirm = c2.checkbox("Confirmo eliminar portada", key="delete_cover_confirm")
            if c2.button("Eliminar Portada", disabled=not (delete_cover_confirm and row.get("portada_data"))):
                delete_cover(row["id"]);audit("INMUEBLE_PORTADA_BAJA", "condominios", row["id"]);refresh_current_property(row["id"]);st.rerun()

    with tabs[4]:
        selected = st.selectbox("Inmueble", list(labels), key="state")
        row = labels[selected]
        permission = "INMUEBLE_DESACTIVAR" if row["activo"] else "INMUEBLE_REACTIVAR"
        access = decision(user, permission, row["id"])
        if not access.allowed:
            denied_message(permission)
        else:
            action = "Desactivar" if row["activo"] else "Reactivar"
            confirm = st.checkbox("Confirmo " + action)
            if st.button(action, disabled=not confirm):
                execute("UPDATE condominios SET activo=NOT activo WHERE id=%s", (row["id"],))
                audit(permission, "condominios", row["id"])
                st.rerun()

    with tabs[5]:
        selected = st.selectbox("Inmueble", list(labels), key="delete")
        row = labels[selected]
        access = decision(user, "INMUEBLE_ELIMINAR", row["id"])
        if not access.allowed:
            denied_message("INMUEBLE_ELIMINAR")
        else:
            deps = dependencies(row["id"])
            st.write("Dependencias", deps)
            if deletable(row["id"]):
                confirm = st.checkbox("Confirmo La Eliminación Permanente")
                if st.button("Eliminar Inmueble", disabled=not confirm):
                    audit("INMUEBLE_ELIMINAR", "condominios", row["id"], before=row)
                    execute("DELETE FROM condominios WHERE id=%s", (row["id"],))
                    st.rerun()
            else:
                st.warning("Este Inmueble Tiene Registros Relacionados. Utiliza Desactivar.")
