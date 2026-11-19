BEGIN;

-- CONDO_SMART BUILD 030C - MANTENIMIENTO ORDINARIO APPLICABILITY
-- Extends the governed starter definition to vertical properties.
-- Does not create rules, versions, obligations, approvals or fees.

INSERT INTO financial_rule_applicability(rule_definition_id,dimension_codigo,valor_codigo,incluido)
SELECT id,'TIPO_INMUEBLE','VERTICAL',TRUE
FROM financial_rule_definitions
WHERE codigo='MANTENIMIENTO_ORDINARIO'
  AND NOT EXISTS (
      SELECT 1 FROM financial_rule_applicability a
      WHERE a.rule_definition_id=financial_rule_definitions.id
        AND a.dimension_codigo='TIPO_INMUEBLE'
        AND a.valor_codigo='VERTICAL'
  );

COMMIT;
