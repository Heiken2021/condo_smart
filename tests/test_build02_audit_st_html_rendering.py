from pathlib import Path


V = Path(
    "views/auditoria.py"
).read_text(encoding="utf-8")


def status_card_block():
    return V.split(
        "def _status_card(",
        1,
    )[1].split(
        "def _severity_counts(",
        1,
    )[0]


def test_status_card_uses_streamlit_html():
    block = status_card_block()

    assert "st.html(" in block
    assert "status_html" in block


def test_status_card_no_longer_uses_markdown():
    block = status_card_block()

    assert "st.markdown(" not in block
    assert "unsafe_allow_html=True" not in block


def test_status_card_no_longer_depends_on_dedent():
    block = status_card_block()

    assert "textwrap.dedent" not in block
    assert "import textwrap" not in V


def test_dynamic_explanation_values_are_escaped():
    block = status_card_block()

    for value in [
        "safe_title",
        "safe_display",
        "safe_summary",
        "safe_reason",
        "safe_trigger",
        "safe_criteria",
        "safe_recommendation",
    ]:
        assert value in block

    assert "html.escape(" in block


def test_explanation_labels_are_preserved():
    block = status_card_block()

    assert "¿Por qué?" in block
    assert "Evento detonante:" in block
    assert "Criterio utilizado:" in block
    assert "Recomendación:" in block


def test_rule_engine_notice_is_preserved():
    block = status_card_block()

    assert (
        "Evaluación automática basada en reglas"
        in block
    )


def test_status_card_keeps_dynamic_colours():
    block = status_card_block()

    assert "SEVERITY_COLORS[severity]" in block


def test_status_card_keeps_dynamic_icons():
    block = status_card_block()

    assert "SEVERITY_ICONS[severity]" in block


def test_both_dashboards_continue_using_status_card():
    assert V.count("_status_card(") >= 3
