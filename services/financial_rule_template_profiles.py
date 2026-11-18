from core.db import fetch_all, fetch_one


def list_jurisdiction_profiles(*, country_code=None, state_code=None, municipality_code=None):
    rows = fetch_all(
        """
        SELECT *
        FROM financial_rule_jurisdiction_profiles
        WHERE active=TRUE
          AND (%s IS NULL OR country_code=%s)
          AND (%s IS NULL OR state_code=%s)
          AND (%s IS NULL OR municipality_code=%s)
        ORDER BY
            CASE WHEN municipality_code IS NOT NULL THEN 30
                 WHEN state_code IS NOT NULL THEN 20
                 WHEN country_code IS NOT NULL THEN 10
                 ELSE 0 END,
            code
        """,
        (
            country_code, country_code,
            state_code, state_code,
            municipality_code, municipality_code,
        ),
    )
    return [dict(row) for row in rows]


def list_definition_profiles(*, definition_id):
    rows = fetch_all(
        """
        SELECT
            profile.*,
            jurisdiction.code AS jurisdiction_code,
            jurisdiction.name AS jurisdiction_name,
            jurisdiction.country_code,
            jurisdiction.state_code,
            jurisdiction.municipality_code
        FROM financial_rule_definition_profiles profile
        JOIN financial_rule_jurisdiction_profiles jurisdiction
          ON jurisdiction.id=profile.jurisdiction_profile_id
        WHERE profile.rule_definition_id=%s
          AND profile.active=TRUE
          AND jurisdiction.active=TRUE
        ORDER BY
            CASE WHEN jurisdiction.municipality_code IS NOT NULL THEN 30
                 WHEN jurisdiction.state_code IS NOT NULL THEN 20
                 WHEN jurisdiction.country_code IS NOT NULL THEN 10
                 ELSE 0 END,
            profile.profile_version DESC
        """,
        (definition_id,),
    )
    return [dict(row) for row in rows]


def get_approved_definition_profile(*, definition_id, jurisdiction_code, effective_date):
    row = fetch_one(
        """
        SELECT profile.*, jurisdiction.code AS jurisdiction_code
        FROM financial_rule_definition_profiles profile
        JOIN financial_rule_jurisdiction_profiles jurisdiction
          ON jurisdiction.id=profile.jurisdiction_profile_id
        WHERE profile.rule_definition_id=%s
          AND jurisdiction.code=%s
          AND profile.status_code='APPROVED'
          AND profile.active=TRUE
          AND jurisdiction.active=TRUE
          AND (profile.effective_from IS NULL OR profile.effective_from<=%s)
          AND (profile.effective_to IS NULL OR profile.effective_to>=%s)
        ORDER BY profile.profile_version DESC, profile.id DESC
        LIMIT 1
        """,
        (definition_id, jurisdiction_code, effective_date, effective_date),
    )
    return dict(row) if row else None
