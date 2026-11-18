BEGIN;

-- CONDO_SMART BUILD 030A - GLOBAL RULE TEMPLATE FOUNDATION
-- Foundation only. This migration does NOT seed starter templates,
-- create financial_rules, create versions, assign properties,
-- approve rules, create obligations, or modify historical fees.

CREATE TABLE IF NOT EXISTS financial_rule_jurisdiction_profiles (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(120) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    country_code VARCHAR(8),
    state_code VARCHAR(32),
    municipality_code VARCHAR(80),
    parent_profile_id BIGINT REFERENCES financial_rule_jurisdiction_profiles(id),
    status_code VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
    effective_from DATE,
    effective_to DATE,
    source_title TEXT,
    source_url TEXT,
    source_published_on DATE,
    reviewed_on DATE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (status_code IN ('DRAFT','APPROVED','RETIRED')),
    CHECK (effective_to IS NULL OR effective_from IS NULL OR effective_to >= effective_from)
);

CREATE TABLE IF NOT EXISTS financial_rule_definition_profiles (
    id BIGSERIAL PRIMARY KEY,
    rule_definition_id BIGINT NOT NULL REFERENCES financial_rule_definitions(id),
    jurisdiction_profile_id BIGINT NOT NULL REFERENCES financial_rule_jurisdiction_profiles(id),
    profile_version INTEGER NOT NULL DEFAULT 1,
    status_code VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
    suggested_values JSONB NOT NULL DEFAULT '{}'::jsonb,
    parameter_constraints JSONB NOT NULL DEFAULT '{}'::jsonb,
    locked_parameters JSONB NOT NULL DEFAULT '[]'::jsonb,
    legal_basis JSONB NOT NULL DEFAULT '[]'::jsonb,
    notes TEXT,
    effective_from DATE,
    effective_to DATE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(rule_definition_id, jurisdiction_profile_id, profile_version),
    CHECK (profile_version > 0),
    CHECK (status_code IN ('DRAFT','APPROVED','RETIRED')),
    CHECK (jsonb_typeof(suggested_values)='object'),
    CHECK (jsonb_typeof(parameter_constraints)='object'),
    CHECK (jsonb_typeof(locked_parameters)='array'),
    CHECK (jsonb_typeof(legal_basis)='array'),
    CHECK (effective_to IS NULL OR effective_from IS NULL OR effective_to >= effective_from)
);

CREATE INDEX IF NOT EXISTS idx_fin_rule_jurisdiction_profile_scope
ON financial_rule_jurisdiction_profiles(country_code, state_code, municipality_code)
WHERE active=TRUE;

CREATE INDEX IF NOT EXISTS idx_fin_rule_definition_profile_lookup
ON financial_rule_definition_profiles(rule_definition_id, jurisdiction_profile_id, status_code, active);

COMMIT;
