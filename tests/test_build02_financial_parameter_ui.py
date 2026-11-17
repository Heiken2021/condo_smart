from pathlib import Path


VIEW = Path(
    "views/financial_governance.py"
).read_text(encoding="utf-8")

EDITOR = Path(
    "services/"
    "financial_dynamic_parameter_editor.py"
).read_text(encoding="utf-8")


def test_parameter_experience_is_business_friendly():
    assert (
        "Parámetros configurables"
        in VIEW
    )

    assert (
        "render_parameter_definition_cards("
        in VIEW
    )

    assert "PARAMETER_LABELS" in EDITOR
    assert "PARAMETER_HELP" in EDITOR


def test_parameter_cards_have_dynamic_help():
    assert "st.popover(" in EDITOR
    assert '"ⓘ"' in EDITOR

    assert (
        "parameter_help(code)"
        in EDITOR
    )


def test_parameter_cards_explain_meaning():
    assert (
        "**¿Qué configura?** "
        in EDITOR
    )

    assert (
        "**Tipo de valor:** "
        in EDITOR
    )

    assert (
        "**Límites permitidos:** "
        in EDITOR
    )


def test_maintenance_parameters_remain_supported():
    for label in (
        "Importe",
        "Frecuencia",
        "Día de vencimiento",
    ):
        assert f'"{label}"' in EDITOR


def test_late_fee_parameters_are_supported():
    for label in (
        "Porcentaje de recargo",
        "Base de cálculo",
        "Días de gracia",
        "Frecuencia del recargo",
        "Recargo máximo",
    ):
        assert f'"{label}"' in EDITOR


def test_continuity_parameters_are_supported():
    for label in (
        "Cobertura mínima requerida",
        "Días de tolerancia",
        "Requiere aviso previo",
        "Requiere autorización",
        "Acción operativa",
    ):
        assert f'"{label}"' in EDITOR


def test_technical_definition_is_removed():
    forbidden = (
        "st.json(schema)",
        "Ver definición técnica",
        "Administración avanzada",
        "st.data_editor(schema",
    )

    for token in forbidden:
        assert token not in VIEW


def test_configuration_tab_exists():
    assert '"Configuración"' in VIEW

    assert (
        "#### Configuración de la regla"
        in VIEW
    )


def test_version_values_are_supported():
    assert (
        "configured_parameter_rows("
        in VIEW
    )

    assert (
        "Valores de la versión"
        in VIEW
    )


def test_business_labels_are_used():
    for function in (
        "business_status(",
        "business_scope(",
        "business_priority(",
        "business_applicability(",
    ):
        assert function in VIEW


def test_parameter_ui_remains_governed():
    forbidden = (
        "st.json(schema)",
        "st.data_editor(schema",
        'st.text_area("JSON',
        'st.text_area("Esquema',
    )

    for token in forbidden:
        assert token not in VIEW
