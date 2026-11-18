from datetime import date

import streamlit as st

from core.authorization import authorize
from services.financial_dynamic_parameter_editor import (
    friendly_value,
    missing_required_parameters,
    parameter_label,
    render_parameter_inputs,
)
from services.financial_rules_grid import (
    list_global_financial_rule_catalog,
    suggest_financial_rule_code,
)


WORKFLOW_STEPS = (
    {
        "key": "definition",
        "number": 1,
        "title": "Definición",
        "question": "¿Qué quieres gobernar?",
        "description": "Indica el propósito de la regla en lenguaje de negocio.",
        "icon": "📄",
        "colour": "#1677ff",
    },
    {
        "key": "availability",
        "number": 2,
        "title": "Disponibilidad",
        "question": "¿Dónde podrá utilizarse?",
        "description": "Decide si será global, por tipología o exclusiva del inmueble.",
        "icon": "🌐",
        "colour": "#12a594",
    },
    {
        "key": "scope",
        "number": 3,
        "title": "Alcance",
        "question": "¿A quién debe aplicarse?",
        "description": "Selecciona el nivel de la jerarquía sin utilizar códigos técnicos.",
        "icon": "🏢",
        "colour": "#7457d9",
    },
    {
        "key": "parameters",
        "number": 4,
        "title": "Parámetros",
        "question": "¿Cómo debe funcionar?",
        "description": "Configura únicamente los valores permitidos por el catálogo.",
        "icon": "🎛️",
        "colour": "#e79a18",
    },
    {
        "key": "version",
        "number": 5,
        "title": "Versión",
        "question": "¿Desde cuándo tendrá vigencia?",
        "description": "Define vigencia y motivo del cambio; el estado inicial será Borrador.",
        "icon": "📑",
        "colour": "#df3d72",
    },
    {
        "key": "review",
        "number": 6,
        "title": "Revisión",
        "question": "¿La regla está lista para enviarse?",
        "description": "Revisa el resumen y todos los puntos de control.",
        "icon": "🛡️",
        "colour": "#169ca7",
    },
)


def _key(property_id, name):
    return f"guided_rule_workflow_{property_id}_{name}"


def _init(property_id):
    defaults = {
        "step": 0,
        "name": "",
        "code": "",
        "description": "",
        "domain": "Obligaciones",
        "definition_id": None,
        "definition_code": "",
        "parameter_schema": {},
        "parameters": {},
        "availability": "Sólo el inmueble activo",
        "scope": "Todo el inmueble",
        "inheritance": True,
        "override": False,
        "effective_from": date.today(),
        "change_reason": "Configuración inicial de la regla",
        "version_confirmed": False,
    }
    for name, value in defaults.items():
        st.session_state.setdefault(_key(property_id, name), value)


def _get(property_id, name):
    return st.session_state.get(_key(property_id, name))


def _set(property_id, name, value):
    st.session_state[_key(property_id, name)] = value


def _css():
    st.markdown(
        """
        <style>
        .rvb-hero {
            border: 1px solid #dbe9fb;
            background: linear-gradient(110deg, #edf6ff 0%, #f4f0ff 100%);
            border-radius: 18px;
            padding: 18px 22px;
            margin: 4px 0 18px 0;
        }
        .rvb-hero h3 { margin: 0 0 4px 0; color: #17315f; }
        .rvb-hero p { margin: 0; color: #52647f; }
        .rvb-map {
            border: 1px solid #e0e7f2;
            background: #ffffff;
            border-radius: 18px;
            padding: 18px;
            min-height: 560px;
        }
        .rvb-node {
            border-radius: 16px;
            padding: 14px 16px;
            margin: 0 0 8px 0;
            border: 1px solid #dfe7f2;
            background: #f7f9fc;
        }
        .rvb-node-current {
            box-shadow: 0 0 0 3px rgba(22,119,255,.13);
            background: #edf5ff;
            border-color: #76aef7;
        }
        .rvb-node-complete {
            background: #edf9f3;
            border-color: #7bcda5;
        }
        .rvb-node-locked { opacity: .62; }
        .rvb-arrow { text-align:center; color:#7386a3; font-size:22px; line-height:20px; }
        .rvb-card {
            border: 1px solid #dfe7f2;
            background: white;
            border-radius: 18px;
            padding: 18px 20px;
            margin-bottom: 12px;
        }
        .rvb-gate-ok {
            border-left: 5px solid #18a66a;
            background: #edf9f3;
            border-radius: 12px;
            padding: 12px 14px;
            margin: 12px 0;
        }
        .rvb-gate-wait {
            border-left: 5px solid #e7a11b;
            background: #fff8e8;
            border-radius: 12px;
            padding: 12px 14px;
            margin: 12px 0;
        }
        .rvb-branch {
            border: 1px dashed #9eb3d3;
            background: #f8fbff;
            border-radius: 14px;
            padding: 12px 14px;
            margin-top: 10px;
        }
        div[data-testid="stHorizontalBlock"] { align-items: stretch; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _step_complete(property_id, index):
    checks = (
        bool(
            str(_get(property_id, "name") or "").strip()
            and str(_get(property_id, "code") or "").strip()
            and str(_get(property_id, "description") or "").strip()
        ),
        bool(_get(property_id, "availability")),
        bool(_get(property_id, "scope")),
        bool(
            _get(property_id, "definition_id")
            and not missing_required_parameters(
                schema=_get(property_id, "parameter_schema") or {},
                values=_get(property_id, "parameters") or {},
            )
        ),
        bool(
            _get(property_id, "effective_from")
            and str(_get(property_id, "change_reason") or "").strip()
            and _get(property_id, "version_confirmed")
        ),
        False,
    )
    return checks[index]


def _first_incomplete(property_id):
    for index in range(5):
        if not _step_complete(property_id, index):
            return index
    return 5


def _render_progress(property_id):
    current = int(_get(property_id, "step") or 0)
    columns = st.columns(6)
    for index, step in enumerate(WORKFLOW_STEPS):
        complete = _step_complete(property_id, index)
        if complete:
            badge = "✓"
            state = "Completo"
        elif index == current:
            badge = str(step["number"])
            state = "Estás aquí"
        elif index > _first_incomplete(property_id):
            badge = "🔒"
            state = "Bloqueado"
        else:
            badge = str(step["number"])
            state = "Pendiente"
        with columns[index]:
            if st.button(
                f"{badge}  {step['title']}\n\n{state}",
                key=_key(property_id, f"progress_{index}"),
                use_container_width=True,
                disabled=(index > _first_incomplete(property_id)),
            ):
                _set(property_id, "step", index)
                st.rerun()


def _render_map(property_id):
    current = int(_get(property_id, "step") or 0)
    parts = ['<div class="rvb-map"><h3>Mapa de la regla</h3>']
    for index, step in enumerate(WORKFLOW_STEPS):
        complete = _step_complete(property_id, index)
        locked = index > _first_incomplete(property_id)
        classes = ["rvb-node"]
        if complete:
            classes.append("rvb-node-complete")
        elif index == current:
            classes.append("rvb-node-current")
        elif locked:
            classes.append("rvb-node-locked")
        marker = "✅" if complete else "🔵" if index == current else "🔒" if locked else "⚪"
        parts.append(
            f'<div class="{" ".join(classes)}">'
            f'<b>{marker} {step["number"]}. {step["title"]}</b><br>'
            f'<span style="color:#5e6e86">{step["question"]}</span>'
            '</div>'
        )
        if index < len(WORKFLOW_STEPS) - 1:
            parts.append('<div class="rvb-arrow">↓</div>')
    parts.extend([
        '<div class="rvb-branch"><b>🔗 Dependencias</b><br><span style="color:#5e6e86">Se muestran sólo cuando otra regla aporta valores gobernados.</span></div>',
        '<div class="rvb-branch"><b>⚗️ Excepciones</b><br><span style="color:#5e6e86">Se habilitan únicamente para casos especiales autorizados.</span></div>',
        '</div>',
    ])
    st.markdown("".join(parts), unsafe_allow_html=True)


def _gate(message, ready):
    css_class = "rvb-gate-ok" if ready else "rvb-gate-wait"
    icon = "✅" if ready else "🟠"
    title = "Punto de control superado" if ready else "Completa este paso para continuar"
    st.markdown(
        f'<div class="{css_class}"><b>{icon} {title}</b><br>{message}</div>',
        unsafe_allow_html=True,
    )


def _definition(property_id, catalog):
    st.markdown("### ¿Qué quieres gobernar?")
    st.caption(
        "Selecciona una plantilla del catálogo. Condo_Smart cargará sus "
        "parámetros y conservará el nombre y código editables antes de confirmar."
    )

    available = [row for row in catalog if row.get("compatible")]
    if not available:
        st.warning("No hay plantillas compatibles disponibles para este inmueble.")
        _gate("Selecciona una plantilla compatible para continuar.", False)
        return False

    current_id = _get(property_id, "definition_id")
    options = [row["definition_id"] for row in available]
    index = options.index(current_id) if current_id in options else None
    labels = {
        row["definition_id"]: (
            f'{row["definition_name"]} · {row["dominio_codigo"]}'
        )
        for row in available
    }
    selected_id = st.selectbox(
        "Plantilla de regla",
        options,
        index=index,
        format_func=lambda value: labels[value],
        placeholder="Selecciona qué proceso quieres gobernar",
        key=_key(property_id, "definition_input"),
    )

    selected = next(
        (row for row in available if row["definition_id"] == selected_id),
        None,
    )
    if selected and selected_id != current_id:
        _set(property_id, "definition_id", selected_id)
        _set(property_id, "definition_code", selected["definition_code"])
        _set(property_id, "name", selected["definition_name"])
        _set(property_id, "description", selected.get("definition_description") or "")
        _set(property_id, "domain", selected["dominio_codigo"])
        _set(property_id, "parameter_schema", selected.get("esquema_parametros") or {})
        _set(property_id, "parameters", {})
        try:
            suggested_code = suggest_financial_rule_code(
                name=selected["definition_name"],
            )
        except TypeError:
            suggested_code = selected["definition_code"]
        _set(property_id, "code", suggested_code)
        st.rerun()

    if not selected:
        _gate("Selecciona una plantilla para continuar.", False)
        return False

    st.info(selected.get("definition_description") or "Plantilla global gobernada.")
    name = st.text_input(
        "Nombre visible de la regla",
        value=_get(property_id, "name"),
        key=_key(property_id, "name_input"),
    )
    _set(property_id, "name", name)
    code = st.text_input(
        "Código sugerido y editable",
        value=_get(property_id, "code"),
        help="La propuesta sigue la lógica gobernada. Puedes editarla antes de confirmar.",
        key=_key(property_id, "code_input"),
    )
    _set(property_id, "code", code)
    description = st.text_area(
        "¿Para qué servirá?",
        value=_get(property_id, "description"),
        key=_key(property_id, "description_input"),
    )
    _set(property_id, "description", description)
    ready = _step_complete(property_id, 0)
    _gate(
        "Plantilla, nombre, código y propósito están completos."
        if ready else "Selecciona la plantilla y completa nombre, código y propósito.",
        ready,
    )
    return ready


def _availability(property_id, catalog):
    st.markdown("### ¿Dónde podrá utilizarse?")
    st.caption("Esta decisión controla la disponibilidad de la definición, no su asignación concreta.")
    options = (
        "Sólo el inmueble activo",
        "Todos los inmuebles del portafolio",
        "Inmuebles de una tipología compatible",
    )
    selection = st.radio(
        "Disponibilidad",
        options,
        index=options.index(_get(property_id, "availability")),
        key=_key(property_id, "availability_input"),
    )
    _set(property_id, "availability", selection)
    st.info(f"Catálogo gobernado consultado: {len(catalog)} definiciones visibles para validar compatibilidad.")
    ready = _step_complete(property_id, 1)
    _gate("Disponibilidad definida; la verificación persistente seguirá usando el engine actual.", ready)
    return ready


def _scope(property_id):
    st.markdown("### ¿A quién debe aplicarse?")
    st.caption("Selecciona una opción de negocio. Condo_Smart traducirá la selección a la jerarquía técnica.")
    options = (
        "Todo el inmueble",
        "Una estructura o privada",
        "Determinados espacios",
    )
    selection = st.radio(
        "Alcance",
        options,
        index=options.index(_get(property_id, "scope")),
        key=_key(property_id, "scope_input"),
    )
    _set(property_id, "scope", selection)
    inheritance = st.toggle(
        "Permitir que niveles inferiores hereden esta configuración",
        value=bool(_get(property_id, "inheritance")),
        key=_key(property_id, "inheritance_input"),
    )
    _set(property_id, "inheritance", inheritance)
    override = st.toggle(
        "Esta asignación sustituirá una configuración heredada",
        value=bool(_get(property_id, "override")),
        key=_key(property_id, "override_input"),
        help="Actívalo únicamente cuando exista una configuración superior que deba sustituirse.",
    )
    _set(property_id, "override", override)
    ready = _step_complete(property_id, 2)
    _gate("Alcance y comportamiento de herencia definidos.", ready)
    return ready


def _parameters(property_id):
    st.markdown("### ¿Cómo debe funcionar?")
    schema = _get(property_id, "parameter_schema") or {}
    if not _get(property_id, "definition_id"):
        st.warning("Primero selecciona una plantilla en Definición.")
        _gate("No hay una plantilla seleccionada.", False)
        return False

    st.caption(
        "Configura únicamente los valores permitidos por el catálogo. "
        "Los límites, tipos y opciones proceden del Gobierno Financiero."
    )
    if not schema:
        st.info("Esta plantilla no requiere parámetros configurables.")
        values = {}
    else:
        values = render_parameter_inputs(
            schema=schema,
            current_values=_get(property_id, "parameters") or {},
            key_prefix=_key(property_id, "parameter"),
        )
    _set(property_id, "parameters", values)

    missing = missing_required_parameters(schema=schema, values=values)
    ready = not missing
    if ready:
        _gate("Todos los parámetros obligatorios son válidos.", True)
    else:
        readable = ", ".join(parameter_label(code) for code in missing)
        _gate("Falta completar: " + readable + ".", False)
    return ready


def _version(property_id):
    st.markdown("### ¿Desde cuándo tendrá vigencia?")
    effective_from = st.date_input(
        "Vigente desde",
        value=_get(property_id, "effective_from"),
        key=_key(property_id, "effective_input"),
    )
    _set(property_id, "effective_from", effective_from)
    reason = st.text_area(
        "Motivo del cambio",
        value=_get(property_id, "change_reason"),
        key=_key(property_id, "reason_input"),
    )
    _set(property_id, "change_reason", reason)
    st.info("La primera versión se creará en estado Borrador. Nadie podrá modificar una versión aprobada de forma destructiva.")
    confirmed = st.checkbox(
        "He revisado la vigencia y el motivo",
        value=bool(_get(property_id, "version_confirmed")),
        key=_key(property_id, "version_input"),
    )
    _set(property_id, "version_confirmed", confirmed)
    ready = _step_complete(property_id, 4)
    _gate("Versión preparada para revisión final." if ready else "Revisa vigencia y motivo.", ready)
    return ready


def _review(property_id):
    st.markdown("### Tu regla está lista para revisión")
    rows = (
        ("Qué gobierna", _get(property_id, "name") or "Pendiente"),
        ("Código", _get(property_id, "code") or "Pendiente"),
        ("Disponibilidad", _get(property_id, "availability") or "Pendiente"),
        ("Alcance", _get(property_id, "scope") or "Pendiente"),
        ("Herencia", "Permitida" if _get(property_id, "inheritance") else "No permitida"),
        ("Override", "Sí" if _get(property_id, "override") else "No"),
        ("Vigencia", str(_get(property_id, "effective_from"))),
        ("Estado inicial", "Borrador"),
    )
    for label, value in rows:
        st.markdown(f"**{label}:** {value}")

    st.markdown("#### Parámetros configurados")
    parameters = _get(property_id, "parameters") or {}
    if parameters:
        for code, value in parameters.items():
            display_value = "Sí" if value is True else "No" if value is False else friendly_value(value)
            st.markdown(f"- **{parameter_label(code)}:** {display_value}")
    else:
        st.caption("La plantilla seleccionada no requiere parámetros configurables.")

    all_ready = all(_step_complete(property_id, index) for index in range(5))
    _gate("Todas las validaciones previas están completas." if all_ready else "Hay pasos pendientes; vuelve al primero incompleto.", all_ready)
    st.warning("Piloto UX v2: Crear borrador y Enviar a aprobación permanecen deshabilitados hasta aprobar el QA visual y funcional.")
    left, right = st.columns(2)
    with left:
        st.button("Guardar borrador", disabled=True, use_container_width=True, key=_key(property_id, "save_disabled"))
    with right:
        st.button("Enviar a aprobación", disabled=True, use_container_width=True, key=_key(property_id, "approve_disabled"))
    return all_ready


def _render_step(property_id, catalog):
    index = int(_get(property_id, "step") or 0)
    step = WORKFLOW_STEPS[index]
    st.markdown(
        f'<div class="rvb-card"><span style="color:{step["colour"]}; font-weight:700">'
        f'Paso {step["number"]} de 6 · {step["title"]}</span>'
        f'<h2 style="margin:8px 0">{step["icon"]} {step["question"]}</h2>'
        f'<p style="color:#5e6e86">{step["description"]}</p></div>',
        unsafe_allow_html=True,
    )
    renderers = (
        lambda: _definition(property_id, catalog),
        lambda: _availability(property_id, catalog),
        lambda: _scope(property_id),
        lambda: _parameters(property_id),
        lambda: _version(property_id),
        lambda: _review(property_id),
    )
    ready = renderers[index]()
    st.divider()
    previous, next_column = st.columns(2)
    with previous:
        if st.button(
            "← Anterior",
            disabled=index == 0,
            use_container_width=True,
            key=_key(property_id, "previous"),
        ):
            _set(property_id, "step", max(0, index - 1))
            st.rerun()
    with next_column:
        if st.button(
            "Continuar →" if index < 5 else "Workflow revisado",
            disabled=(index == 5 or not ready),
            type="primary",
            use_container_width=True,
            key=_key(property_id, "next"),
        ):
            _set(property_id, "step", min(5, index + 1))
            st.rerun()


def render_rule_visual_builder(*, property_id, user):
    decision = authorize(user, "FINANZAS_GOBIERNO_CONSULTAR", property_id)
    if not decision.allowed:
        st.warning("Sin permiso para consultar el Gobierno Financiero.")
        return
    _init(property_id)
    _css()
    catalog = list_global_financial_rule_catalog(
        property_id=property_id,
        user=user,
    )
    st.markdown("## Rule Visual Builder")
    st.caption("Crear regla de negocio · Condo_Smart te guiará paso a paso")
    st.markdown(
        '<div class="rvb-hero"><h3>✨ Workflow guiado</h3>'
        '<p>Una decisión por pantalla, puntos de control y un mapa visual permanente. '
        'Mismo Gobierno Financiero, sin exponer complejidad técnica.</p></div>',
        unsafe_allow_html=True,
    )
    st.info("Piloto UX v2 · Draft-only · sin aprobación automática · sin escrituras directas en base de datos.")
    _render_progress(property_id)
    st.divider()
    map_column, workflow_column = st.columns([0.9, 1.8], gap="large")
    with map_column:
        _render_map(property_id)
    with workflow_column:
        _render_step(property_id, catalog)
