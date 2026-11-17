-- ============================================================
-- Condo_Smart · Build 02
-- Migration 026
-- Governed dependencies between financial rule definitions
-- ============================================================

CREATE TABLE IF NOT EXISTS financial_rule_dependencies(
    id BIGSERIAL PRIMARY KEY,

    consumer_definition_id BIGINT NOT NULL
        REFERENCES financial_rule_definitions(id),

    source_definition_id BIGINT NOT NULL
        REFERENCES financial_rule_definitions(id),

    criterion_code VARCHAR(100) NOT NULL,
    criterion_label VARCHAR(180) NOT NULL,

    source_parameter_code VARCHAR(100) NOT NULL,

    required BOOLEAN NOT NULL DEFAULT TRUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    UNIQUE(
        consumer_definition_id,
        criterion_code
    ),

    CHECK (
        consumer_definition_id
        <> source_definition_id
    )
);


CREATE INDEX IF NOT EXISTS
idx_financial_rule_dependencies_consumer
ON financial_rule_dependencies(
    consumer_definition_id,
    active
);


CREATE INDEX IF NOT EXISTS
idx_financial_rule_dependencies_source
ON financial_rule_dependencies(
    source_definition_id,
    active
);


INSERT INTO financial_rule_dependencies(
    consumer_definition_id,
    source_definition_id,
    criterion_code,
    criterion_label,
    source_parameter_code,
    required,
    active
)
SELECT
    consumer.id,
    source.id,
    'coverage_threshold',
    'Cobertura mínima requerida',
    'minimum_payment_percentage',
    TRUE,
    TRUE
FROM financial_rule_definitions consumer
JOIN financial_rule_definitions source
  ON source.codigo='PAGO_MINIMO_PARCIAL'
WHERE consumer.codigo='CONTINUIDAD_SERVICIOS'
ON CONFLICT(
    consumer_definition_id,
    criterion_code
)
DO UPDATE SET
    source_definition_id=
        EXCLUDED.source_definition_id,
    criterion_label=
        EXCLUDED.criterion_label,
    source_parameter_code=
        EXCLUDED.source_parameter_code,
    required=TRUE,
    active=TRUE;


INSERT INTO financial_rule_dependencies(
    consumer_definition_id,
    source_definition_id,
    criterion_code,
    criterion_label,
    source_parameter_code,
    required,
    active
)
SELECT
    consumer.id,
    source.id,
    'tolerance_days',
    'Días de tolerancia',
    'grace_days',
    TRUE,
    TRUE
FROM financial_rule_definitions consumer
JOIN financial_rule_definitions source
  ON source.codigo='RECARGO_MOROSIDAD'
WHERE consumer.codigo='CONTINUIDAD_SERVICIOS'
ON CONFLICT(
    consumer_definition_id,
    criterion_code
)
DO UPDATE SET
    source_definition_id=
        EXCLUDED.source_definition_id,
    criterion_label=
        EXCLUDED.criterion_label,
    source_parameter_code=
        EXCLUDED.source_parameter_code,
    required=TRUE,
    active=TRUE;
