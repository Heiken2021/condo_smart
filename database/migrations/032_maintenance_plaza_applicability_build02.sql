-- Build 02 · 032
-- Amplía la aplicabilidad gobernada de MANTENIMIENTO_ORDINARIO.
-- No duplica la definición global ni crea reglas/versiones por inmueble.

INSERT INTO financial_rule_applicability (
    rule_definition_id,
    dimension_codigo,
    valor_codigo,
    incluido
)
SELECT
    definition.id,
    'TIPO_INMUEBLE',
    'PLAZA_COMERCIAL',
    TRUE
FROM financial_rule_definitions definition
WHERE definition.codigo='MANTENIMIENTO_ORDINARIO'
  AND definition.activo=TRUE
ON CONFLICT (
    rule_definition_id,
    dimension_codigo,
    valor_codigo
)
DO UPDATE SET incluido=EXCLUDED.incluido;
