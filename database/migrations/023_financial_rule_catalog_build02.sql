-- ============================================================
-- Condo_Smart · Build 02
-- Migration 023
-- Initial governed financial rule catalogue
--
-- Additive and idempotent.
-- Creates definitions/catalogue only.
-- Does not create configured rules, versions, fees,
-- obligations, payments, allocations or exceptions.
-- ============================================================


-- ------------------------------------------------------------
-- 1. Canonical definition:
--    Ordinary maintenance fee
-- ------------------------------------------------------------

INSERT INTO financial_rule_definitions (
    codigo,
    nombre,
    descripcion,
    dominio_codigo,
    nivel_base_codigo,
    tipo_resultado,
    esquema_parametros,
    obligatoria,
    admite_especializacion,
    admite_herencia,
    admite_override,
    admite_excepcion,
    requiere_aprobacion,
    permite_nivel_inmueble,
    permite_nivel_estructura,
    permite_nivel_espacio,
    contexto_kpi,
    contexto_ia,
    activo
)
SELECT
    'MANTENIMIENTO_ORDINARIO',
    'Mantenimiento ordinario',
    (
        'Gobierna la configuración de cuotas '
        'ordinarias de mantenimiento por inmueble, '
        'estructura o espacio.'
    ),
    'OBLIGACIONES',
    'CORE',
    'POLICY',
    jsonb_build_object(
        'amount', jsonb_build_object(
            'type', 'number',
            'minimum', 0.01,
            'currency', 'MXN'
        ),
        'frequency', jsonb_build_object(
            'type', 'string',
            'allowed', jsonb_build_array(
                'MENSUAL'
            )
        ),
        'due_day', jsonb_build_object(
            'type', 'integer',
            'minimum', 1,
            'maximum', 31,
            'optional', true
        )
    ),
    FALSE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE,
    TRUE
WHERE NOT EXISTS (
    SELECT 1
    FROM financial_rule_definitions
    WHERE codigo='MANTENIMIENTO_ORDINARIO'
);


-- ------------------------------------------------------------
-- 2. Applicability:
--    Compatible with FRACCIONAMIENTO properties
-- ------------------------------------------------------------

INSERT INTO financial_rule_applicability (
    rule_definition_id,
    dimension_codigo,
    valor_codigo,
    incluido
)
SELECT
    definition.id,
    'TIPO_INMUEBLE',
    'FRACCIONAMIENTO',
    TRUE
FROM financial_rule_definitions definition
WHERE definition.codigo=
      'MANTENIMIENTO_ORDINARIO'
  AND NOT EXISTS (
      SELECT 1
      FROM financial_rule_applicability
          applicability
      WHERE
          applicability.rule_definition_id=
          definition.id
        AND applicability.dimension_codigo=
            'TIPO_INMUEBLE'
        AND applicability.valor_codigo=
            'FRACCIONAMIENTO'
        AND applicability.incluido=TRUE
  );


-- ------------------------------------------------------------
-- Important
-- ------------------------------------------------------------
-- This migration intentionally does not create:
--
-- financial_rules
-- financial_rule_versions
-- financial_rule_exceptions
-- space_fee_history
-- financial_obligations
-- payment_allocations
--
-- The rule lifecycle will create those records through
-- governed application services and explicit approval.
