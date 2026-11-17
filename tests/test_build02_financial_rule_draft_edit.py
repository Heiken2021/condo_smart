from pathlib import Path


SOURCE = Path(
    "services/financial_governance_commands.py"
).read_text(encoding="utf-8")


def test_update_draft_command_exists():
    assert (
        "def update_rule_version_draft("
        in SOURCE
    )


def test_update_requires_manage_permission():
    block = SOURCE[
        SOURCE.index(
            "def update_rule_version_draft("
        ):
        SOURCE.index(
            "def approve_rule_version("
        )
    ]

    assert (
        '"FINANZAS_REGLA_GESTIONAR"'
        in block
    )


def test_only_draft_is_editable():
    block = SOURCE[
        SOURCE.index(
            "def update_rule_version_draft("
        ):
        SOURCE.index(
            "def approve_rule_version("
        )
    ]

    assert (
        '"BORRADOR"'
        in block
    )

    assert (
        "FINANCIAL_RULE_VERSION_NOT_EDITABLE"
        in block
    )


def test_draft_update_uses_row_lock():
    block = SOURCE[
        SOURCE.index(
            "def update_rule_version_draft("
        ):
        SOURCE.index(
            "def approve_rule_version("
        )
    ]

    assert "FOR UPDATE" in block


def test_draft_update_is_audited():
    block = SOURCE[
        SOURCE.index(
            "def update_rule_version_draft("
        ):
        SOURCE.index(
            "def approve_rule_version("
        )
    ]

    assert (
        '"FINANCIAL_RULE_VERSION_"'
        in block
    )

    assert (
        '"DRAFT_UPDATED"'
        in block
    )

    assert '"before": before' in block
    assert '"after": after' in block


def test_draft_update_is_transactional():
    block = SOURCE[
        SOURCE.index(
            "def update_rule_version_draft("
        ):
        SOURCE.index(
            "def approve_rule_version("
        )
    ]

    assert "connection.commit()" in block
    assert "connection.rollback()" in block
