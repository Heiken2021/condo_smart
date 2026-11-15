BEGIN;

-- ============================================================
-- CONDO_SMART · BUILD 02
-- FINANCE FOUNDATION 02D
-- OBLIGATIONS & PAYMENT ALLOCATIONS
--
-- OBLIGACION != PAGO
--
-- Obligación:
--   importe que debe liquidarse.
--
-- Pago:
--   dinero efectivamente recibido.
--
-- Aplicación:
--   importe de un pago asignado a una obligación.
--
-- Saldo:
--   importe obligación - aplicaciones ACTIVAS.
--
-- Migración aditiva.
-- cargos y pagos existentes permanecen intactos.
-- ============================================================


-- ------------------------------------------------------------
-- 01. OBLIGACIONES FINANCIERAS
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS financial_obligations(
    id BIGSERIAL PRIMARY KEY,

    condominio_id BIGINT NOT NULL
        REFERENCES condominios(id),

    estructura_id BIGINT
        REFERENCES estructura_inmueble(id),

    espacio_id BIGINT NOT NULL
        REFERENCES espacios(id),

    periodo VARCHAR(7) NOT NULL,

    fecha_generacion DATE NOT NULL
        DEFAULT CURRENT_DATE,

    fecha_vencimiento DATE,

    tipo_codigo VARCHAR(80) NOT NULL,

    concepto VARCHAR(240) NOT NULL,

    monto_original_mxn NUMERIC(14,2)
        NOT NULL,

    estado_codigo VARCHAR(30)
        NOT NULL
        DEFAULT 'REGISTRADA',

    -- Procedencia gobernada.
    rule_version_id BIGINT
        REFERENCES financial_rule_versions(id),

    space_fee_history_id BIGINT
        REFERENCES space_fee_history(id),

    referencia VARCHAR(120),

    observaciones TEXT,

    creado_por BIGINT
        REFERENCES usuarios(id),

    creado_en TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    cancelado_por BIGINT
        REFERENCES usuarios(id),

    cancelado_en TIMESTAMPTZ,

    motivo_cancelacion TEXT,

    CHECK (
        periodo ~
        '^[0-9]{4}-(0[1-9]|1[0-2])$'
    ),

    CHECK (
        monto_original_mxn > 0
    ),

    CHECK (
        estado_codigo IN (
            'REGISTRADA',
            'CANCELADA'
        )
    ),

    CHECK (
        fecha_vencimiento IS NULL
        OR fecha_vencimiento >= fecha_generacion
    ),

    CHECK (
        (
            estado_codigo='REGISTRADA'
            AND cancelado_en IS NULL
            AND cancelado_por IS NULL
            AND motivo_cancelacion IS NULL
        )
        OR
        (
            estado_codigo='CANCELADA'
            AND cancelado_en IS NOT NULL
            AND cancelado_por IS NOT NULL
            AND NULLIF(
                BTRIM(motivo_cancelacion),
                ''
            ) IS NOT NULL
        )
    )
);


CREATE INDEX IF NOT EXISTS
idx_financial_obligations_scope
ON financial_obligations(
    condominio_id,
    estructura_id,
    espacio_id,
    periodo,
    estado_codigo
);


CREATE INDEX IF NOT EXISTS
idx_financial_obligations_rule
ON financial_obligations(
    rule_version_id
);


CREATE INDEX IF NOT EXISTS
idx_financial_obligations_fee
ON financial_obligations(
    space_fee_history_id
);


-- ------------------------------------------------------------
-- 02. APLICACIONES DE PAGO
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS payment_allocations(
    id BIGSERIAL PRIMARY KEY,

    condominio_id BIGINT NOT NULL
        REFERENCES condominios(id),

    pago_id BIGINT NOT NULL
        REFERENCES pagos(id),

    obligation_id BIGINT NOT NULL
        REFERENCES financial_obligations(id),

    monto_aplicado_mxn NUMERIC(14,2)
        NOT NULL,

    financial_rule_exception_id BIGINT
        REFERENCES financial_rule_exceptions(id),

    estado_codigo VARCHAR(30)
        NOT NULL
        DEFAULT 'ACTIVA',

    aplicado_por BIGINT
        REFERENCES usuarios(id),

    aplicado_en TIMESTAMPTZ NOT NULL
        DEFAULT NOW(),

    reversado_por BIGINT
        REFERENCES usuarios(id),

    reversado_en TIMESTAMPTZ,

    motivo_reversion TEXT,

    CHECK (
        monto_aplicado_mxn > 0
    ),

    CHECK (
        estado_codigo IN (
            'ACTIVA',
            'REVERSADA'
        )
    ),

    CHECK (
        (
            estado_codigo='ACTIVA'
            AND reversado_por IS NULL
            AND reversado_en IS NULL
            AND motivo_reversion IS NULL
        )
        OR
        (
            estado_codigo='REVERSADA'
            AND reversado_por IS NOT NULL
            AND reversado_en IS NOT NULL
            AND NULLIF(
                BTRIM(motivo_reversion),
                ''
            ) IS NOT NULL
        )
    )
);


CREATE INDEX IF NOT EXISTS
idx_payment_allocations_payment
ON payment_allocations(
    pago_id,
    estado_codigo
);


CREATE INDEX IF NOT EXISTS
idx_payment_allocations_obligation
ON payment_allocations(
    obligation_id,
    estado_codigo
);


-- ------------------------------------------------------------
-- 03. VISTA DE SALDO DERIVADO
--
-- El saldo NO se almacena como dato editable.
-- ------------------------------------------------------------

CREATE OR REPLACE VIEW financial_obligation_balances
AS
SELECT
    obligation.id AS obligation_id,
    obligation.condominio_id,
    obligation.estructura_id,
    obligation.espacio_id,
    obligation.periodo,
    obligation.tipo_codigo,
    obligation.concepto,
    obligation.monto_original_mxn,

    COALESCE(
        SUM(
            allocation.monto_aplicado_mxn
        ) FILTER (
            WHERE allocation.estado_codigo='ACTIVA'
        ),
        0
    )::NUMERIC(14,2)
        AS monto_aplicado_mxn,

    (
        obligation.monto_original_mxn
        -
        COALESCE(
            SUM(
                allocation.monto_aplicado_mxn
            ) FILTER (
                WHERE allocation.estado_codigo='ACTIVA'
            ),
            0
        )
    )::NUMERIC(14,2)
        AS saldo_mxn,

    CASE
        WHEN obligation.estado_codigo='CANCELADA'
            THEN 'CANCELADA'

        WHEN COALESCE(
            SUM(
                allocation.monto_aplicado_mxn
            ) FILTER (
                WHERE allocation.estado_codigo='ACTIVA'
            ),
            0
        ) = 0
            THEN 'PENDIENTE'

        WHEN COALESCE(
            SUM(
                allocation.monto_aplicado_mxn
            ) FILTER (
                WHERE allocation.estado_codigo='ACTIVA'
            ),
            0
        ) < obligation.monto_original_mxn
            THEN 'PARCIAL'

        ELSE 'LIQUIDADA'
    END AS situacion_codigo

FROM financial_obligations obligation

LEFT JOIN payment_allocations allocation
  ON allocation.obligation_id=obligation.id

GROUP BY
    obligation.id;


-- ------------------------------------------------------------
-- 04. VALIDAR SCOPE DE OBLIGACIÓN
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION
validate_financial_obligation_scope()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    space_row RECORD;
    structure_property_id BIGINT;
    fee_row RECORD;
    version_property_id BIGINT;
BEGIN

    SELECT
        condominio_id,
        estructura_id
    INTO space_row
    FROM espacios
    WHERE id=NEW.espacio_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'FINANCIAL_OBLIGATION_SPACE_NOT_FOUND';
    END IF;

    IF space_row.condominio_id
       IS DISTINCT FROM NEW.condominio_id
    THEN
        RAISE EXCEPTION
            'FINANCIAL_OBLIGATION_SPACE_SCOPE_MISMATCH';
    END IF;

    IF NEW.estructura_id
       IS DISTINCT FROM space_row.estructura_id
    THEN
        RAISE EXCEPTION
            'FINANCIAL_OBLIGATION_STRUCTURE_CONTEXT_MISMATCH';
    END IF;

    -- La ubicación se congela al generar la obligación.
    -- Si se declara, debe pertenecer al inmueble.
    IF NEW.estructura_id IS NOT NULL THEN

        SELECT condominio_id
        INTO structure_property_id
        FROM estructura_inmueble
        WHERE id=NEW.estructura_id;

        IF structure_property_id IS NULL
           OR structure_property_id
              <> NEW.condominio_id
        THEN
            RAISE EXCEPTION
                'FINANCIAL_OBLIGATION_STRUCTURE_SCOPE_MISMATCH';
        END IF;

    END IF;

    IF NEW.space_fee_history_id IS NOT NULL THEN

        SELECT
            condominio_id,
            espacio_id,
            tipo_cuota_codigo,
            vigente_desde,
            vigente_hasta,
            estado_codigo
        INTO fee_row
        FROM space_fee_history
        WHERE id=NEW.space_fee_history_id;

        IF NOT FOUND
           OR fee_row.condominio_id
              <> NEW.condominio_id
           OR fee_row.espacio_id
              <> NEW.espacio_id
        THEN
            RAISE EXCEPTION
                'FINANCIAL_OBLIGATION_FEE_SCOPE_MISMATCH';
        END IF;

        IF fee_row.estado_codigo
           <> 'APROBADO'
        THEN
            RAISE EXCEPTION
                'FINANCIAL_OBLIGATION_REQUIRES_APPROVED_FEE';
        END IF;

        IF fee_row.vigente_desde
           > TO_DATE(NEW.periodo || '-01', 'YYYY-MM-DD')
           OR (
               fee_row.vigente_hasta IS NOT NULL
               AND fee_row.vigente_hasta
                   < TO_DATE(
                       NEW.periodo || '-01',
                       'YYYY-MM-DD'
                   )
           )
        THEN
            RAISE EXCEPTION
                'FINANCIAL_OBLIGATION_FEE_NOT_EFFECTIVE';
        END IF;

    END IF;

    IF NEW.rule_version_id IS NOT NULL THEN

        SELECT rule.condominio_id
        INTO version_property_id
        FROM financial_rule_versions version
        JOIN financial_rules rule
          ON rule.id=version.rule_id
        WHERE version.id=NEW.rule_version_id
          AND version.estado_codigo='APROBADO'
          AND version.vigente_desde
              <= TO_DATE(
                  NEW.periodo || '-01',
                  'YYYY-MM-DD'
              )
          AND (
              version.vigente_hasta IS NULL
              OR version.vigente_hasta
                 >= TO_DATE(
                     NEW.periodo || '-01',
                     'YYYY-MM-DD'
                 )
          );

        IF NOT FOUND THEN
            RAISE EXCEPTION
                'FINANCIAL_OBLIGATION_REQUIRES_EFFECTIVE_APPROVED_RULE';
        END IF;

        IF version_property_id IS NOT NULL
           AND version_property_id
               <> NEW.condominio_id
        THEN
            RAISE EXCEPTION
                'FINANCIAL_OBLIGATION_RULE_SCOPE_MISMATCH';
        END IF;

    END IF;

    RETURN NEW;
END;
$$;


CREATE TRIGGER
trg_financial_obligation_scope
BEFORE INSERT OR UPDATE OF
    condominio_id,
    estructura_id,
    espacio_id,
    rule_version_id,
    space_fee_history_id
ON financial_obligations
FOR EACH ROW
EXECUTE FUNCTION
validate_financial_obligation_scope();


-- ------------------------------------------------------------
-- 05. VALIDAR APLICACIÓN DE PAGO
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION
validate_payment_allocation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    payment_row RECORD;
    obligation_row RECORD;
    payment_allocated NUMERIC(14,2);
    obligation_allocated NUMERIC(14,2);
    exception_row RECORD;
BEGIN

    SELECT
        condominio_id,
        espacio_id,
        fecha,
        monto_mxn,
        estado_codigo,
        activo
    INTO payment_row
    FROM pagos
    WHERE id=NEW.pago_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'FINANCIAL_ALLOCATION_PAYMENT_NOT_FOUND';
    END IF;

    IF payment_row.estado_codigo
       <> 'REGISTRADO'
       OR NOT payment_row.activo
    THEN
        RAISE EXCEPTION
            'FINANCIAL_ALLOCATION_PAYMENT_NOT_ACTIVE';
    END IF;


    SELECT
        condominio_id,
        espacio_id,
        monto_original_mxn,
        estado_codigo
    INTO obligation_row
    FROM financial_obligations
    WHERE id=NEW.obligation_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'FINANCIAL_ALLOCATION_OBLIGATION_NOT_FOUND';
    END IF;

    IF obligation_row.estado_codigo
       <> 'REGISTRADA'
    THEN
        RAISE EXCEPTION
            'FINANCIAL_ALLOCATION_OBLIGATION_NOT_ACTIVE';
    END IF;


    IF payment_row.condominio_id
       <> obligation_row.condominio_id
       OR NEW.condominio_id
          <> obligation_row.condominio_id
    THEN
        RAISE EXCEPTION
            'FINANCIAL_ALLOCATION_PROPERTY_SCOPE_MISMATCH';
    END IF;


    IF payment_row.espacio_id
       <> obligation_row.espacio_id
    THEN
        RAISE EXCEPTION
            'FINANCIAL_ALLOCATION_SPACE_SCOPE_MISMATCH';
    END IF;


    SELECT
        COALESCE(
            SUM(monto_aplicado_mxn),
            0
        )
    INTO payment_allocated
    FROM payment_allocations
    WHERE pago_id=NEW.pago_id
      AND estado_codigo='ACTIVA'
      AND id <> COALESCE(NEW.id,0);


    IF payment_allocated
       + NEW.monto_aplicado_mxn
       > payment_row.monto_mxn
    THEN
        RAISE EXCEPTION
            'FINANCIAL_PAYMENT_OVERALLOCATION';
    END IF;


    SELECT
        COALESCE(
            SUM(monto_aplicado_mxn),
            0
        )
    INTO obligation_allocated
    FROM payment_allocations
    WHERE obligation_id=NEW.obligation_id
      AND estado_codigo='ACTIVA'
      AND id <> COALESCE(NEW.id,0);


    IF obligation_allocated
       + NEW.monto_aplicado_mxn
       > obligation_row.monto_original_mxn
    THEN
        RAISE EXCEPTION
            'FINANCIAL_OBLIGATION_OVERALLOCATION';
    END IF;


    IF NEW.financial_rule_exception_id
       IS NOT NULL
    THEN

        SELECT
            condominio_id,
            estructura_id,
            espacio_id,
            estado_codigo,
            vigente_desde,
            vigente_hasta
        INTO exception_row
        FROM financial_rule_exceptions
        WHERE id=
            NEW.financial_rule_exception_id;

        IF NOT FOUND
           OR exception_row.estado_codigo
              <> 'APROBADA'
        THEN
            RAISE EXCEPTION
                'FINANCIAL_ALLOCATION_REQUIRES_APPROVED_EXCEPTION';
        END IF;

        IF exception_row.condominio_id
           <> NEW.condominio_id
        THEN
            RAISE EXCEPTION
                'FINANCIAL_ALLOCATION_EXCEPTION_SCOPE_MISMATCH';
        END IF;

        IF (
            exception_row.vigente_desde IS NOT NULL
            AND exception_row.vigente_desde
                > payment_row.fecha
        )
        OR (
            exception_row.vigente_hasta IS NOT NULL
            AND exception_row.vigente_hasta
                < payment_row.fecha
        )
        THEN
            RAISE EXCEPTION
                'FINANCIAL_ALLOCATION_EXCEPTION_NOT_EFFECTIVE';
        END IF;

        IF exception_row.espacio_id
           IS NOT NULL
           AND exception_row.espacio_id
               <> obligation_row.espacio_id
        THEN
            RAISE EXCEPTION
                'FINANCIAL_ALLOCATION_EXCEPTION_SPACE_MISMATCH';
        END IF;

    END IF;


    RETURN NEW;
END;
$$;


CREATE TRIGGER
trg_payment_allocation_integrity
BEFORE INSERT OR UPDATE OF
    condominio_id,
    pago_id,
    obligation_id,
    monto_aplicado_mxn,
    financial_rule_exception_id,
    estado_codigo
ON payment_allocations
FOR EACH ROW
WHEN (NEW.estado_codigo='ACTIVA')
EXECUTE FUNCTION
validate_payment_allocation();


-- ------------------------------------------------------------
-- 06. PROTEGER HISTÓRICO DE APLICACIONES
--
-- Una aplicación activa no se edita.
-- Puede transicionar únicamente a REVERSADA.
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION
protect_payment_allocation_history()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF TG_OP='DELETE' THEN
        RAISE EXCEPTION
            'FINANCIAL_PAYMENT_ALLOCATION_DELETE_NOT_ALLOWED';
    END IF;

    IF OLD.estado_codigo='REVERSADA' THEN
        RAISE EXCEPTION
            'REVERSED_PAYMENT_ALLOCATION_IS_IMMUTABLE';
    END IF;


    IF NEW.estado_codigo='REVERSADA' THEN

        IF NEW.reversado_por IS NULL
           OR NEW.reversado_en IS NULL
           OR NULLIF(
               BTRIM(NEW.motivo_reversion),
               ''
           ) IS NULL
        THEN
            RAISE EXCEPTION
                'FINANCIAL_ALLOCATION_REVERSAL_METADATA_REQUIRED';
        END IF;


        IF (
            to_jsonb(NEW)
            - ARRAY[
                'estado_codigo',
                'reversado_por',
                'reversado_en',
                'motivo_reversion'
            ]
        )
        IS DISTINCT FROM
        (
            to_jsonb(OLD)
            - ARRAY[
                'estado_codigo',
                'reversado_por',
                'reversado_en',
                'motivo_reversion'
            ]
        )
        THEN
            RAISE EXCEPTION
                'ACTIVE_PAYMENT_ALLOCATION_IS_IMMUTABLE';
        END IF;

        RETURN NEW;

    END IF;


    RAISE EXCEPTION
        'ACTIVE_PAYMENT_ALLOCATION_IS_IMMUTABLE';

END;
$$;


CREATE TRIGGER
trg_payment_allocation_history
BEFORE UPDATE OR DELETE
ON payment_allocations
FOR EACH ROW
EXECUTE FUNCTION
protect_payment_allocation_history();


-- ------------------------------------------------------------
-- 07. PROTEGER CANCELACIÓN DE OBLIGACIONES
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION
validate_financial_obligation_cancellation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    active_allocations INTEGER;
BEGIN

    IF OLD.estado_codigo='CANCELADA' THEN
        RAISE EXCEPTION
            'CANCELLED_FINANCIAL_OBLIGATION_IS_IMMUTABLE';
    END IF;


    IF NEW.estado_codigo='CANCELADA' THEN

        SELECT COUNT(*)
        INTO active_allocations
        FROM payment_allocations
        WHERE obligation_id=OLD.id
          AND estado_codigo='ACTIVA';


        IF active_allocations > 0 THEN
            RAISE EXCEPTION
                'FINANCIAL_OBLIGATION_HAS_ACTIVE_ALLOCATIONS';
        END IF;


        IF NEW.cancelado_por IS NULL
           OR NEW.cancelado_en IS NULL
           OR NULLIF(
               BTRIM(NEW.motivo_cancelacion),
               ''
           ) IS NULL
        THEN
            RAISE EXCEPTION
                'FINANCIAL_OBLIGATION_CANCELLATION_METADATA_REQUIRED';
        END IF;


        IF (
            to_jsonb(NEW)
            - ARRAY[
                'estado_codigo',
                'cancelado_por',
                'cancelado_en',
                'motivo_cancelacion'
            ]
        )
        IS DISTINCT FROM
        (
            to_jsonb(OLD)
            - ARRAY[
                'estado_codigo',
                'cancelado_por',
                'cancelado_en',
                'motivo_cancelacion'
            ]
        )
        THEN
            RAISE EXCEPTION
                'FINANCIAL_OBLIGATION_HISTORY_IS_IMMUTABLE';
        END IF;


        RETURN NEW;

    END IF;


    IF NEW IS DISTINCT FROM OLD THEN
        RAISE EXCEPTION
            'FINANCIAL_OBLIGATION_HISTORY_IS_IMMUTABLE';
    END IF;

    RETURN NEW;

END;
$$;


CREATE TRIGGER
trg_financial_obligation_history
BEFORE UPDATE OR DELETE
ON financial_obligations
FOR EACH ROW
EXECUTE FUNCTION
validate_financial_obligation_cancellation();


-- ------------------------------------------------------------
-- 08. PERMISOS
-- ------------------------------------------------------------

INSERT INTO permisos(
    codigo,
    nombre,
    modulo,
    accion,
    activo
)
VALUES
    (
        'FINANZAS_OBLIGACION_CREAR',
        'Crear Obligación Financiera',
        'FINANZAS',
        'CREATE',
        TRUE
    ),
    (
        'FINANZAS_OBLIGACION_CANCELAR',
        'Cancelar Obligación Financiera',
        'FINANZAS',
        'UPDATE',
        TRUE
    ),
    (
        'FINANZAS_PAGO_APLICAR',
        'Aplicar Pago A Obligación',
        'FINANZAS',
        'CREATE',
        TRUE
    ),
    (
        'FINANZAS_PAGO_REVERTIR_APLICACION',
        'Revertir Aplicación De Pago',
        'FINANZAS',
        'UPDATE',
        TRUE
    )
ON CONFLICT (codigo) DO NOTHING;


-- Asignación inicial conservadora.
-- Puede evolucionar mediante gobierno posterior.

INSERT INTO rol_permisos(
    rol_codigo,
    permiso_codigo,
    permitido
)
SELECT
    rol.codigo,
    permiso.codigo,
    TRUE
FROM roles rol
JOIN permisos permiso
  ON permiso.codigo IN (
      'FINANZAS_OBLIGACION_CREAR',
      'FINANZAS_OBLIGACION_CANCELAR',
      'FINANZAS_PAGO_APLICAR',
      'FINANZAS_PAGO_REVERTIR_APLICACION'
  )
WHERE rol.codigo='ADMINISTRADOR'
ON CONFLICT DO NOTHING;


COMMIT;
