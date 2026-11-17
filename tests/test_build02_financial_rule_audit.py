from pathlib import Path


SERVICE = Path(
    "services/financial_rule_audit.py"
).read_text(encoding="utf-8")

LIFECYCLE = Path(
    "views/financial_rule_lifecycle.py"
).read_text(encoding="utf-8")


def test_audit_reads_rule_and_version_events():
    for token in (
        "FROM auditoria_financiera audit",
        "audit.entidad='FINANCIAL_RULE'",
        "'FINANCIAL_RULE_VERSION'",
        "audit.metadata->>'rule_id'",
        "ORDER BY audit.fecha DESC",
    ):
        assert token in SERVICE


def test_audit_has_business_operation_labels():
    for label in (
        "Configuración de regla creada",
        "Versión creada",
        "Borrador actualizado",
        "Versión aprobada",
        "Vigencia finalizada",
    ):
        assert label in SERVICE


def test_audit_presents_business_fields():
    for token in (
        '"evento"',
        '"version"',
        '"actor"',
        '"transicion"',
        '"motivo"',
        '"dependencias"',
        '"trace_id"',
    ):
        assert token in SERVICE


def test_approval_dependencies_are_presented():
    assert (
        'metadata.get("resolved_dependencies")'
        in SERVICE
    )

    assert (
        "Dependencias utilizadas "
        in LIFECYCLE
    )


def test_lifecycle_replaces_audit_placeholder():
    assert (
        "def _render_rule_audit("
        in LIFECYCLE
    )

    assert (
        "financial_rule_audit_rows("
        in LIFECYCLE
    )

    assert (
        'elif action == "AUDIT":'
        in LIFECYCLE
    )

    assert (
        "se incorporará en el siguiente "
        not in LIFECYCLE
    )


def test_audit_does_not_show_raw_metadata():
    assert "st.json(" not in LIFECYCLE
    assert "json.dumps(" not in LIFECYCLE
