BEGIN;

-- CONDO_SMART BUILD 033 - FLEXIBLE FREQUENCY CATALOG
-- Standard governed frequencies remain suggested, while an administrator may enter
-- an additional frequency when the property requires it. Values remain version data.

UPDATE financial_rule_definitions
SET esquema_parametros = jsonb_set(
    esquema_parametros,
    '{frequency}',
    COALESCE(esquema_parametros->'frequency','{}'::jsonb) ||
    '{"type":"string","allowed":["MENSUAL","BIMESTRAL","TRIMESTRAL","SEMESTRAL","ANUAL"],"accept_new_options":true}'::jsonb
)
WHERE codigo='MANTENIMIENTO_ORDINARIO'
  AND activo=TRUE;

COMMIT;
