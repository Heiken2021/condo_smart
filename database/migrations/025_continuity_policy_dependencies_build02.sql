-- ============================================================
-- Condo_Smart · Build 02
-- Migration 025
-- Continuity policy without duplicated financial thresholds
--
-- CONTINUIDAD_SERVICIOS consumes governed results from:
--   PAGO_MINIMO_PARCIAL
--   RECARGO_MOROSIDAD
--
-- It configures only operational consequences.
-- ============================================================

UPDATE financial_rule_definitions
SET
    descripcion = (
        'Gobierna las consecuencias operativas asociadas '
        'al cumplimiento financiero. Utiliza el criterio '
        'de cobertura resuelto por Pago mínimo parcial y '
        'el criterio temporal resuelto por Recargo por '
        'morosidad, sin duplicar sus parámetros.'
    ),
    esquema_parametros = jsonb_build_object(
        'operational_action',
        jsonb_build_object(
            'type', 'string',
            'allowed', jsonb_build_array(
                'SIN_CAMBIO',
                'REVISAR',
                'RESTRINGIR_SEGUN_POLITICA'
            )
        ),
        'prior_notice_required',
        jsonb_build_object(
            'type', 'boolean'
        ),
        'authorization_required',
        jsonb_build_object(
            'type', 'boolean'
        )
    ),
    contexto_kpi = TRUE,
    contexto_ia = TRUE
WHERE codigo = 'CONTINUIDAD_SERVICIOS'
  AND activo = TRUE;
