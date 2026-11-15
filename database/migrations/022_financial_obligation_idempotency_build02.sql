BEGIN;

-- ============================================================
-- CONDO_SMART · BUILD 02
-- FINANCE FOUNDATION 02D.3
-- FINANCIAL OBLIGATION IDEMPOTENCY
--
-- Impide que dos procesos concurrentes generen la misma
-- obligación activa para un espacio, periodo y tipo.
--
-- 021 permanece inmutable.
-- ============================================================


-- ------------------------------------------------------------
-- 01. UNICIDAD DE OBLIGACIÓN ACTIVA
--
-- Una obligación CANCELADA deja de participar en esta
-- restricción y no bloquea una sustitución posterior.
-- ------------------------------------------------------------

CREATE UNIQUE INDEX IF NOT EXISTS
uq_financial_obligation_active_period_type
ON financial_obligations(
    condominio_id,
    espacio_id,
    periodo,
    tipo_codigo
)
WHERE estado_codigo='REGISTRADA';


-- ------------------------------------------------------------
-- 02. FUNCIÓN DE CONSULTA DE IDEMPOTENCIA
--
-- Contrato reutilizable por servicios y diagnósticos.
-- La restricción definitiva sigue siendo el índice único.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION
financial_active_obligation_exists(
    property_id BIGINT,
    space_id BIGINT,
    obligation_period VARCHAR,
    obligation_type VARCHAR
)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT EXISTS(
        SELECT 1
        FROM financial_obligations obligation
        WHERE obligation.condominio_id=
              property_id
          AND obligation.espacio_id=
              space_id
          AND obligation.periodo=
              obligation_period
          AND obligation.tipo_codigo=
              obligation_type
          AND obligation.estado_codigo=
              'REGISTRADA'
    );
$$;


COMMIT;
