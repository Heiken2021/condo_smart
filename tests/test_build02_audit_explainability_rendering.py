from pathlib import Path


V = Path(
    "views/auditoria.py"
).read_text(encoding="utf-8")


def test_status_card_normalizes_html_indentation():
    assert "import textwrap" in V
    assert "textwrap.dedent(html).strip()" in V


def test_status_card_still_allows_html_rendering():
    assert "unsafe_allow_html=True" in V


def test_explanation_is_still_inside_status_card():
    for value in [
        'explanation["summary"]',
        'explanation["reason"]',
        'explanation["trigger"]',
        'explanation["criteria"]',
        'explanation["recommendation"]',
    ]:
        assert value in V


def test_explanation_labels_are_preserved():
    assert "¿Por qué?" in V
    assert "Evento detonante:" in V
    assert "Criterio utilizado:" in V
    assert "Recomendación:" in V


def test_rule_engine_notice_is_preserved():
    assert (
        "Evaluación automática basada en reglas"
        in V
    )


def test_status_card_keeps_dynamic_color():
    assert "SEVERITY_COLORS[severity]" in V


def test_status_card_keeps_dynamic_icon():
    assert "SEVERITY_ICONS[severity]" in V


def test_status_card_html_is_rendered_as_one_normalized_string():
    assert "html = f" in V
    assert "st.markdown(" in V
    assert "textwrap.dedent(html).strip()" in V
