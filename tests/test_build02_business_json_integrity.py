import json
from pathlib import Path

from services.financial_governance_commands import (
    _audit_json,
    _json,
)


SERVICE = Path(
    "services/financial_governance_commands.py"
).read_text(encoding="utf-8")


def test_business_json_preserves_authorization_boolean():
    value = json.loads(
        _json(
            {
                "authorization_required": True,
            }
        )
    )

    assert (
        value["authorization_required"]
        is True
    )


def test_business_json_preserves_prior_notice_boolean():
    value = json.loads(
        _json(
            {
                "prior_notice_required": True,
            }
        )
    )

    assert (
        value["prior_notice_required"]
        is True
    )


def test_audit_json_still_redacts_sensitive_authorization():
    value = json.loads(
        _audit_json(
            {
                "authorization": "Bearer secret",
            }
        )
    )

    assert value["authorization"] == "[REDACTED]"


def test_business_json_does_not_call_sanitize():
    start = SERVICE.index(
        "def _json("
    )

    end = SERVICE.index(
        "def _audit_json(",
        start,
    )

    block = SERVICE[start:end]

    assert "sanitize(" not in block


def test_audit_json_does_call_sanitize():
    start = SERVICE.index(
        "def _audit_json("
    )

    end = SERVICE.index(
        "def _insert_audit(",
        start,
    )

    block = SERVICE[start:end]

    assert "sanitize(value)" in block


def test_insert_audit_uses_audit_serializer():
    assert "_audit_json(metadata)" in SERVICE
