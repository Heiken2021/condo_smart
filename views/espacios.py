from datetime import date
import pandas as pd
import streamlit as st
from core.access import cid
from core.authorization import authorize
from core.formatting import money
from components.ui import title
from services.catalogs import options
from services.property_structure import list_space_locations, node_path
from services.spaces import (list_spaces,get_space,list_people,list_occupancy_history,create_space,
    update_space,sync_responsible_history,set_active,dependencies,deletable,delete_space)


def _decision(user,permission,pid): return authorize(user,permission,pid)
def _denied(permission): st.warning(f"Sin permiso para esta operacion: {permission}")


def _form(prefix,row=None,forced_structure_id=None,lock_structure=False):
    row=row or {}; types=options("TIPO_ESPACIO"); states=options("ESTADO_ESPACIO"); uses=options("USO_ESPACIO"); conditions=options("CONDICION_FISICA")
    if not types or not states or not uses or not conditions:
        st.error("Configura los catalogos TIPO_ESPACIO, ESTADO_ESPACIO, USO_ESPACIO y CONDICION_FISICA."); return None
    def selected(mapping,value):
        return next((n for n,c in mapping.items() if c==value),list(mapping)[0])
    c1,c2=st.columns(2)
    clave=c1.text_input("Clave / Codigo",value=row.get("clave") or "",key=f"{prefix}_clave")
    nombre=c2.text_input("Nombre",value=row.get("nombre") or "",key=f"{prefix}_nombre")
    c3,c4,c5=st.columns(3)
    tn=c3.selectbox("Tipo",list(types),index=list(types).index(selected(types,row.get("tipo_codigo"))),key=f"{prefix}_tipo")
    en=c4.selectbox("Estado de ocupacion",list(states),index=list(states).index(selected(states,row.get("estado_codigo"))),key=f"{prefix}_estado")
    un=c5.selectbox("Uso",list(uses),index=list(uses).index(selected(uses,row.get("uso_codigo"))),key=f"{prefix}_uso")
    c6,c7,c8=st.columns(3)
    superficie=c6.number_input("Superficie m2",min_value=0.0,value=float(row.get("superficie_m2") or 0),step=1.0,key=f"{prefix}_m2")
    edificio_zona=c7.text_input("Edificio / Zona",value=row.get("edificio_zona") or "",key=f"{prefix}_edificio_zona")
    nivel=c8.text_input("Nivel / Piso",value=row.get("nivel") or "",key=f"{prefix}_nivel")
    if lock_structure:
        estructura_id=forced_structure_id
        if estructura_id is None:
            st.caption("Ubicación seleccionada: Espacios Directos")
        else:
            nodes=list_space_locations(cid(),active_only=False)
            st.caption(f"Ubicación seleccionada: {node_path(nodes,estructura_id) or estructura_id}")
    else:
        nodes=list_space_locations(cid(),active_only=True)
        structure_map={"Espacios Directos":None}|{node_path(nodes,n["id"]):n["id"] for n in nodes}
        current_structure=next((name for name,node_id in structure_map.items() if node_id==row.get("estructura_id")),"Espacios Directos")
        estructura_label=st.selectbox("Ubicación",list(structure_map),index=list(structure_map).index(current_structure),key=f"{prefix}_estructura")
        estructura_id=structure_map[estructura_label]
    people=list_people(cid()); person_map={"Sin asignar":None}|{p["nombre"]:p["id"] for p in people}
    current=next((n for n,v in person_map.items() if v==row.get("responsable_persona_id")),"Sin asignar")
    c9,c10=st.columns(2)
    responsible=c9.selectbox("Responsable",list(person_map),index=list(person_map).index(current),key=f"{prefix}_responsable")
    relation=c10.selectbox("Relacion",["PROPIETARIO","INQUILINO"],index=0 if row.get("responsable_relacion")!="INQUILINO" else 1,key=f"{prefix}_relacion",disabled=responsible=="Sin asignar")
    cy,cc=st.columns(2)
    current_year=date.today().year
    fecha_value=row.get("fecha_construccion") or date(current_year,1,1)
    fecha_construccion=cy.date_input("Fecha de construccion",value=fecha_value,max_value=date.today(),format="DD/MM/YYYY",key=f"{prefix}_fecha_construccion")
    cn=cc.selectbox("Condicion fisica",list(conditions),index=list(conditions).index(selected(conditions,row.get("condicion_codigo"))),key=f"{prefix}_condicion")
    descripcion=st.text_area("Descripcion",value=row.get("descripcion") or "",key=f"{prefix}_descripcion")
    fecha_ocupacion=st.date_input("Fecha de ocupacion / inicio de relacion",value=date.today(),max_value=date.today(),format="DD/MM/YYYY",key=f"{prefix}_fecha_ocupacion")
    c11,c12=st.columns(2)
    cuota=c11.number_input("Cuota Base",min_value=0.0,value=float(row.get("cuota_base") or 0),step=100.0,key=f"{prefix}_cuota")
    indiviso=c12.number_input("Indiviso %",min_value=0.0,max_value=100.0,value=float(row.get("indiviso_pct") or 0),step=0.01,key=f"{prefix}_indiviso")
    return dict(clave=clave.strip() or None,nombre=nombre.strip(),tipo_codigo=types[tn],estado_codigo=states[en],uso_codigo=uses[un],superficie_m2=superficie,edificio_zona=edificio_zona.strip() or None,nivel=nivel.strip() or None,fecha_construccion=fecha_construccion,condicion_codigo=conditions[cn],descripcion=descripcion.strip() or None,responsable_persona_id=person_map[responsible],responsable_relacion=relation if person_map[responsible] else None,fecha_ocupacion=fecha_ocupacion,estructura_id=estructura_id,cuota_base=cuota,indiviso_pct=indiviso)


def render():
    st.markdown('''<style>
    .cs-selected-space{
        background:#D9F5E5;
        color:#087D45;
        border-radius:11px;
        padding:12px 16px;
        font-size:1.45rem;
        line-height:1.25;
        font-weight:800;
        margin:8px 0 14px 0;
        border:1px solid rgba(32,170,88,.12);
    }
    </style>''',unsafe_allow_html=True)
    title("Espacios","Grid seleccionable y detalle funcional por inmueble")
    pid=cid()
    if not pid: st.info("Selecciona un inmueble desde Inmuebles."); return
    user=st.session_state.get("user",{})
    if not _decision(user,"ESPACIO_CONSULTAR",pid).allowed: _denied("ESPACIO_CONSULTAR"); return
    rows=list_spaces(pid)
    nodes=list_space_locations(pid,active_only=True)
    locations=[{"id":None,"Clave":"DIRECTOS","Ubicación":"Espacios Directos","Tipo":"DIRECTO","Espacios":sum(1 for r in rows if r.get("estructura_id") is None)}]
    locations += [{"id":n["id"],"Clave":n.get("clave") or "","Ubicación":node_path(nodes,n["id"]),"Tipo":n.get("tipo_codigo"),"Espacios":sum(1 for r in rows if r.get("estructura_id")==n["id"])} for n in nodes]
    st.markdown("### 1. Selecciona Una Ubicación")
    location_event=st.dataframe(pd.DataFrame([{k:v for k,v in x.items() if k!="id"} for x in locations]),hide_index=True,use_container_width=True,on_select="rerun",selection_mode="single-row",key=f"spaces_location_grid_{pid}")
    location_indexes=list(location_event.selection.rows or [])
    location_selected=locations[location_indexes[0]] if location_indexes and 0<=location_indexes[0]<len(locations) else None
    selected_structure_id=location_selected["id"] if location_selected else None
    selected=None
    if location_selected is None:
        st.info("Selecciona Espacios Directos o una Privada para consultar sus registros.")
    else:
        st.markdown(f"### 2. Espacios De: {location_selected['Ubicación']}")
        location_rows=[r for r in rows if r.get("estructura_id")==selected_structure_id]
        f1,f2,f3,f4=st.columns([2,1,1,1])
        search=f1.text_input("Buscar por clave, nombre o responsable",key="spaces_search").strip().lower()
        tf=f2.selectbox("Tipo",["Todos"]+sorted({r["tipo_codigo"] for r in location_rows if r.get("tipo_codigo")}),key="spaces_type_filter")
        sf=f3.selectbox("Ocupación",["Todos"]+sorted({r["estado_codigo"] for r in location_rows if r.get("estado_codigo")}),key="spaces_occupancy_filter")
        af=f4.selectbox("Activo",["Todos","Activos","Inactivos"],key="spaces_status_filter")
        filtered=[]
        for r in location_rows:
            hay=" ".join(str(r.get(k) or "") for k in ("clave","nombre","responsable_nombre")).lower()
            if search and search not in hay: continue
            if tf!="Todos" and r.get("tipo_codigo")!=tf: continue
            if sf!="Todos" and r.get("estado_codigo")!=sf: continue
            if af=="Activos" and not r.get("activo"): continue
            if af=="Inactivos" and r.get("activo"): continue
            filtered.append(r)
        display=pd.DataFrame([{"Clave":r.get("clave") or "","Espacio / Casa":r.get("nombre"),"Tipo":r.get("tipo_codigo"),"Estado de ocupación":r.get("estado_codigo"),"Superficie m2":float(r.get("superficie_m2") or 0),"Responsable":r.get("responsable_nombre") or "Sin asignar","Relación":r.get("responsable_relacion") or "","Cuota Base":money(r.get("cuota_base")),"Activo":"Sí" if r.get("activo") else "No"} for r in filtered])
        if display.empty:
            st.info("La ubicación seleccionada no tiene espacios para los filtros aplicados.")
        else:
            event=st.dataframe(display,hide_index=True,use_container_width=True,on_select="rerun",selection_mode="single-row",key=f"spaces_master_grid_{pid}")
            indexes=list(event.selection.rows or [])
            selected_index=indexes[0] if indexes else None
            selected=filtered[selected_index] if selected_index is not None and 0 <= selected_index < len(filtered) else None
        st.caption("Selecciona una fila del grid de espacios para mostrar el detalle y habilitar acciones.")

    if selected:
        row=get_space(pid,selected["id"]); st.markdown("---"); st.markdown(
            f'''<div class="cs-selected-space">{row.get('clave') or ''} · {row.get('nombre') or ''}</div>''',
            unsafe_allow_html=True,
        )
        c1,c2,c3=st.columns(3)
        with c1:
            st.markdown("**Caracteristicas**"); st.write("Tipo:",row.get("tipo_codigo") or "-"); st.write("Ocupacion:",row.get("estado_codigo") or "-"); st.write("Superficie:",f"{float(row.get('superficie_m2') or 0):,.2f} m2"); st.write("Uso:",row.get("uso_codigo") or "-")
        with c2:
            st.markdown("**Ubicacion**"); st.write("Edificio / Zona:",row.get("edificio_zona") or "-"); st.write("Nivel / Piso:",row.get("nivel") or "-"); fc=row.get("fecha_construccion"); edad=(date.today().year-fc.year-((date.today().month,date.today().day)<(fc.month,fc.day))) if fc else None; st.write("Fecha de construccion:",fc or "-"); st.write("Edad:",f"{edad} años" if edad is not None else "-"); st.write("Condicion fisica:",row.get("condicion_codigo") or "-"); st.write("Descripcion:",row.get("descripcion") or "-")
        with c3:
            st.markdown("**Responsable y finanzas**"); st.write("Responsable:",row.get("responsable_nombre") or "Sin asignar"); st.write("Relacion:",row.get("responsable_relacion") or "-"); st.write("Correo:",row.get("responsable_email") or "-"); st.write("Telefono:",row.get("responsable_telefono") or "-"); st.write("Cuota Base:",money(row.get("cuota_base"))); st.write("Indiviso %:",row.get("indiviso_pct") or 0); st.write("Activo:","Si" if row.get("activo") else "No")
        st.markdown("**Historial cronologico de ocupacion**")
        history=list_occupancy_history(pid,row["id"])
        if history:
            st.dataframe(pd.DataFrame([{"Persona":h.get("nombre"),"Relacion":h.get("tipo_relacion"),"Desde":h.get("fecha_inicio"),"Hasta":h.get("fecha_fin") or "Actual","Antiguedad (dias)":h.get("antiguedad_dias"),"Activo":"Si" if h.get("activo") else "No"} for h in history]),hide_index=True,use_container_width=True)
        else: st.info("Sin historial de ocupacion.")
        management_section=st.radio(
            "Gestion Del Espacio",
            ["Editar","Cambiar Estado","Eliminar"],
            horizontal=True,
            key=f"space_management_section_{pid}_{row['id']}",
            label_visibility="collapsed",
        )
        if management_section=="Editar":
            if not _decision(user,"ESPACIO_MODIFICAR",pid).allowed: _denied("ESPACIO_MODIFICAR")
            else:
                with st.form("space_edit_selected"):
                    data=_form("selected_edit",row,forced_structure_id=row.get("estructura_id"),lock_structure=True); ok=st.form_submit_button("Guardar Cambios",type="primary")
                if ok and data:
                    if not data["nombre"]: st.error("El nombre es obligatorio.")
                    else:
                        fecha_ocupacion=data.pop("fecha_ocupacion", None)
                        update_space(pid,row["id"],**data)
                        sync_responsible_history(pid,row["id"],data.get("responsable_persona_id"),data.get("responsable_relacion"),fecha_ocupacion)
                        st.success("Espacio actualizado."); st.rerun()
        if management_section=="Cambiar Estado":
            target=not row["activo"]; permission="ESPACIO_REACTIVAR" if target else "ESPACIO_DESACTIVAR"
            if not _decision(user,permission,pid).allowed: _denied(permission)
            elif st.button("Reactivar Espacio" if target else "Desactivar Espacio",key="selected_state"):
                set_active(pid,row["id"],target); st.rerun()
        if management_section=="Eliminar":
            if not _decision(user,"ESPACIO_ELIMINAR",pid).allowed: _denied("ESPACIO_ELIMINAR")
            else:
                deps=dependencies(pid,row["id"]) or {}
                st.markdown("**Dependencias asociadas**")
                dep_cols=st.columns(4)
                dep_items=[("Personas",deps.get("personas",0)),("Usuarios",deps.get("usuarios",0)),("Cargos",deps.get("cargos",0)),("Pagos",deps.get("pagos",0))]
                for col,(label,total) in zip(dep_cols,dep_items):
                    col.metric(label,int(total))
                dep_total=sum(int(total) for _,total in dep_items)
                if dep_total:
                    st.warning(f"Este espacio tiene {dep_total} dependencia(s) asociada(s) y no puede eliminarse permanentemente.")
                else:
                    st.success("Este espacio no tiene dependencias asociadas y puede eliminarse.")
                can=deletable(pid,row["id"])
                confirm=st.checkbox("Confirmo la eliminacion permanente",disabled=not can,key="selected_delete_confirm")
                if not can: st.warning("El espacio tiene dependencias. Desactivalo si corresponde.")
                if st.button("Eliminar Espacio",disabled=not(can and confirm),key="selected_delete"):
                    if delete_space(pid,row["id"]): st.rerun()

    if location_selected is not None:
        create_col,_=st.columns([1.6,8.4])
        if create_col.button(
            "+ Alta De Espacio",
            type="primary",
            use_container_width=True,
            key=f"space_create_open_{pid}_{selected_structure_id}",
        ):
            st.session_state.space_create_mode=True

        if st.session_state.get("space_create_mode"):
            st.subheader(f"Alta De Espacio En: {location_selected['Ubicación']}")
            if st.button("Cancelar Alta",key=f"space_create_cancel_{pid}_{selected_structure_id}"):
                st.session_state.space_create_mode=False
                st.rerun()
            if not _decision(user,"ESPACIO_CREAR",pid).allowed: _denied("ESPACIO_CREAR")
            else:
                with st.form("space_create_master_detail"):
                    data=_form("space_new",forced_structure_id=selected_structure_id,lock_structure=True); ok=st.form_submit_button("Crear Espacio",type="primary")
                if ok and data:
                    if not data["nombre"]: st.error("El nombre es obligatorio.")
                    else:
                        fecha_ocupacion=data.pop("fecha_ocupacion", None)
                        record=create_space(pid,**data)
                        sync_responsible_history(pid,record["id"],data.get("responsable_persona_id"),data.get("responsable_relacion"),fecha_ocupacion)
                        st.session_state.space_create_mode=False
                        st.success("Espacio creado."); st.rerun()
