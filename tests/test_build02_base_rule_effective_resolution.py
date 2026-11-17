from pathlib import Path


SERVICE = Path(
    "services/financial_governance.py"
).read_text(encoding="utf-8")


def test_property_base_rule_does_not_require_override():
    assert (
        "SPECIFIC_RULE_REQUIRES_OVERRIDE"
        not in SERVICE
    )


def test_base_configuration_is_eligible():
    assert (
        "ELIGIBLE_BASE_CONFIGURATION"
        in SERVICE
    )


def test_override_remains_explicit():
    assert (
        "ELIGIBLE_OVERRIDE"
        in SERVICE
    )

    assert (
        'candidate.get(\n'
        '                "es_override"'
        in SERVICE
    )


def test_scope_resolution_is_preserved():
    for scope in (
        '"CORE"',
        '"TIPOLOGIA"',
        '"INMUEBLE"',
        '"ESTRUCTURA"',
        '"ESPACIO"',
    ):
        assert scope in SERVICE

    assert (
        "scope_rank"
        in SERVICE
    )


def test_candidate_order_remains_governed():
    for token in (
        'row["scope_rank"]',
        'row["prioridad"]',
        'row["version_num"]',
        'row["version_id"]',
    ):
        assert token in SERVICE


def test_only_approved_versions_are_effective():
    assert (
        "version.estado_codigo='APROBADO'"
        in SERVICE
    )


def test_effective_date_constraints_remain():
    assert (
        "version.vigente_desde <= %s"
        in SERVICE
    )

    assert (
        "version.vigente_hasta >= %s"
        in SERVICE
    )
