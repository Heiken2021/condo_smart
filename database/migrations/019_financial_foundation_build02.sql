BEGIN;

-- ============================================================
-- BUILD 02 · FINANCIAL FOUNDATION
-- Cargos · Pagos · Gastos
-- ============================================================

-- ------------------------------------------------------------
-- 1. CATÁLOGOS MÍNIMOS
-- ------------------------------------------------------------

INSERT INTO catalogos(
    codigo,
    nombre,
    activo
)
VALUES
    (
        'ESTADO_MOVIMIENTO_FINANCIERO',
        'Estado De Movimiento Financiero',
        TRUE
    ),
    (
        'TIPO_CARGO',
        'Tipo De Cargo',
        TRUE
    ),
    (
        'CATEGORIA_GASTO',
        'Categoría De Gasto',
        TRUE
    )
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO catalogo_valores(
    catalogo_id,
    codigo,
    nombre,
    activo
)
SELECT
    catalogo.id,
    valor.codigo,
    valor.nombre,
    TRUE
FROM catalogos catalogo
JOIN (
    VALUES
        (
            'ESTADO_MOVIMIENTO_FINANCIERO',
            'REGISTRADO',
            'Registrado'
        ),
        (
            'ESTADO_MOVIMIENTO_FINANCIERO',
            'CANCELADO',
            'Cancelado'
        ),
        (
            'TIPO_CARGO',
            'CUOTA_MANTENIMIENTO',
            'Cuota De Mantenimiento'
        ),
        (
            'TIPO_CARGO',
            'CUOTA_EXTRAORDINARIA',
            'Cuota Extraordinaria'
        ),
        (
            'TIPO_CARGO',
            'OTRO',
            'Otro Cargo'
        ),
        (
            'CATEGORIA_GASTO',
            'OPERACION',
            'Operación'
        ),
        (
            'CATEGORIA_GASTO',
            'MANTENIMIENTO',
            'Mantenimiento'
        ),
        (
            'CATEGORIA_GASTO',
            'SERVICIOS',
            'Servicios'
        ),
        (
            'CATEGORIA_GASTO',
            'OTRO',
            'Otro Gasto'
        )
) AS valor(
    catalogo_codigo,
    codigo,
    nombre
)
  ON catalogo.codigo=valor.catalogo_codigo
ON CONFLICT (catalogo_id, codigo) DO NOTHING;

-- ------------------------------------------------------------
-- 2. PERMISOS FINANCIEROS
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
        'FINANZAS_CONSULTAR',
        'Consultar Movimientos Financieros',
        'FINANZAS',
        'READ',
        TRUE
    ),
    (
        'FINANZAS_CARGO_CREAR',
        'Crear Cargos',
        'FINANZAS',
        'CREATE',
        TRUE
    ),
    (
        'FINANZAS_PAGO_REGISTRAR',
        'Registrar Pagos',
        'FINANZAS',
        'CREATE',
        TRUE
    ),
    (
        'FINANZAS_GASTO_REGISTRAR',
        'Registrar Gastos',
        'FINANZAS',
        'CREATE',
        TRUE
    ),
    (
        'FINANZAS_MOVIMIENTO_CANCELAR',
        'Cancelar Movimientos Financieros',
        'FINANZAS',
        'UPDATE',
        TRUE
    ),
    (
        'FINANZAS_ESTADO_CUENTA',
        'Consultar Estado De Cuenta',
        'FINANZAS',
        'READ',
        TRUE
    )
ON CONFLICT (codigo) DO NOTHING;

-- Administración y Contabilidad pueden operar.
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
      'FINANZAS_CONSULTAR',
      'FINANZAS_CARGO_CREAR',
      'FINANZAS_PAGO_REGISTRAR',
      'FINANZAS_GASTO_REGISTRAR',
      'FINANZAS_MOVIMIENTO_CANCELAR',
      'FINANZAS_ESTADO_CUENTA'
  )
WHERE rol.codigo IN (
    'ADMINISTRADOR',
    'CONTABILIDAD'
)
ON CONFLICT DO NOTHING;

-- Gerencia y Comité comienzan con lectura.
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
      'FINANZAS_CONSULTAR',
      'FINANZAS_ESTADO_CUENTA'
  )
WHERE rol.codigo IN (
    'GERENTE',
    'COMITE'
)
ON CONFLICT DO NOTHING;

-- ------------------------------------------------------------
-- 3. CARGOS
-- ------------------------------------------------------------

ALTER TABLE cargos
    ADD COLUMN IF NOT EXISTS estado_codigo VARCHAR(30),
    ADD COLUMN IF NOT EXISTS referencia VARCHAR(120),
    ADD COLUMN IF NOT EXISTS observaciones TEXT,
    ADD COLUMN IF NOT EXISTS creado_en TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS creado_por BIGINT REFERENCES usuarios(id),
    ADD COLUMN IF NOT EXISTS cancelado_en TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS cancelado_por BIGINT REFERENCES usuarios(id),
    ADD COLUMN IF NOT EXISTS motivo_cancelacion TEXT;

UPDATE cargos
SET
    estado_codigo=COALESCE(
        estado_codigo,
        CASE
            WHEN activo=FALSE THEN 'CANCELADO'
            ELSE 'REGISTRADO'
        END
    ),
    creado_en=COALESCE(creado_en, NOW()),
    activo=COALESCE(activo, TRUE),
    monto_mxn=COALESCE(monto_mxn, 0)
WHERE
    estado_codigo IS NULL
    OR creado_en IS NULL
    OR activo IS NULL
    OR monto_mxn IS NULL;

ALTER TABLE cargos
    ALTER COLUMN condominio_id SET NOT NULL,
    ALTER COLUMN espacio_id SET NOT NULL,
    ALTER COLUMN periodo SET NOT NULL,
    ALTER COLUMN tipo_codigo SET NOT NULL,
    ALTER COLUMN concepto SET NOT NULL,
    ALTER COLUMN monto_mxn SET NOT NULL,
    ALTER COLUMN activo SET NOT NULL,
    ALTER COLUMN estado_codigo SET DEFAULT 'REGISTRADO',
    ALTER COLUMN estado_codigo SET NOT NULL,
    ALTER COLUMN creado_en SET DEFAULT NOW(),
    ALTER COLUMN creado_en SET NOT NULL;

-- ------------------------------------------------------------
-- 4. PAGOS
-- ------------------------------------------------------------

ALTER TABLE pagos
    ADD COLUMN IF NOT EXISTS estado_codigo VARCHAR(30),
    ADD COLUMN IF NOT EXISTS referencia VARCHAR(120),
    ADD COLUMN IF NOT EXISTS observaciones TEXT,
    ADD COLUMN IF NOT EXISTS creado_en TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS creado_por BIGINT REFERENCES usuarios(id),
    ADD COLUMN IF NOT EXISTS cancelado_en TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS cancelado_por BIGINT REFERENCES usuarios(id),
    ADD COLUMN IF NOT EXISTS motivo_cancelacion TEXT;

UPDATE pagos
SET
    estado_codigo=COALESCE(
        estado_codigo,
        CASE
            WHEN activo=FALSE THEN 'CANCELADO'
            ELSE 'REGISTRADO'
        END
    ),
    creado_en=COALESCE(creado_en, NOW()),
    fecha=COALESCE(fecha, CURRENT_DATE),
    activo=COALESCE(activo, TRUE),
    monto_mxn=COALESCE(monto_mxn, 0)
WHERE
    estado_codigo IS NULL
    OR creado_en IS NULL
    OR fecha IS NULL
    OR activo IS NULL
    OR monto_mxn IS NULL;

ALTER TABLE pagos
    ALTER COLUMN condominio_id SET NOT NULL,
    ALTER COLUMN espacio_id SET NOT NULL,
    ALTER COLUMN periodo SET NOT NULL,
    ALTER COLUMN fecha SET DEFAULT CURRENT_DATE,
    ALTER COLUMN fecha SET NOT NULL,
    ALTER COLUMN monto_mxn SET NOT NULL,
    ALTER COLUMN activo SET NOT NULL,
    ALTER COLUMN estado_codigo SET DEFAULT 'REGISTRADO',
    ALTER COLUMN estado_codigo SET NOT NULL,
    ALTER COLUMN creado_en SET DEFAULT NOW(),
    ALTER COLUMN creado_en SET NOT NULL;

-- ------------------------------------------------------------
-- 5. GASTOS
-- ------------------------------------------------------------

ALTER TABLE gastos
    ADD COLUMN IF NOT EXISTS estado_codigo VARCHAR(30),
    ADD COLUMN IF NOT EXISTS referencia VARCHAR(120),
    ADD COLUMN IF NOT EXISTS observaciones TEXT,
    ADD COLUMN IF NOT EXISTS creado_en TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS creado_por BIGINT REFERENCES usuarios(id),
    ADD COLUMN IF NOT EXISTS cancelado_en TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS cancelado_por BIGINT REFERENCES usuarios(id),
    ADD COLUMN IF NOT EXISTS motivo_cancelacion TEXT;

UPDATE gastos
SET
    estado_codigo=COALESCE(
        estado_codigo,
        CASE
            WHEN activo=FALSE THEN 'CANCELADO'
            ELSE 'REGISTRADO'
        END
    ),
    creado_en=COALESCE(creado_en, NOW()),
    fecha=COALESCE(fecha, CURRENT_DATE),
    activo=COALESCE(activo, TRUE),
    monto_mxn=COALESCE(monto_mxn, 0)
WHERE
    estado_codigo IS NULL
    OR creado_en IS NULL
    OR fecha IS NULL
    OR activo IS NULL
    OR monto_mxn IS NULL;

ALTER TABLE gastos
    ALTER COLUMN condominio_id SET NOT NULL,
    ALTER COLUMN fecha SET DEFAULT CURRENT_DATE,
    ALTER COLUMN fecha SET NOT NULL,
    ALTER COLUMN categoria_codigo SET NOT NULL,
    ALTER COLUMN concepto SET NOT NULL,
    ALTER COLUMN monto_mxn SET NOT NULL,
    ALTER COLUMN activo SET NOT NULL,
    ALTER COLUMN estado_codigo SET DEFAULT 'REGISTRADO',
    ALTER COLUMN estado_codigo SET NOT NULL,
    ALTER COLUMN creado_en SET DEFAULT NOW(),
    ALTER COLUMN creado_en SET NOT NULL;

-- ------------------------------------------------------------
-- 6. RESTRICCIONES
-- ------------------------------------------------------------

ALTER TABLE cargos
    DROP CONSTRAINT IF EXISTS ck_cargos_monto_positivo,
    DROP CONSTRAINT IF EXISTS ck_cargos_periodo,
    DROP CONSTRAINT IF EXISTS ck_cargos_estado;

ALTER TABLE cargos
    ADD CONSTRAINT ck_cargos_monto_positivo
        CHECK (monto_mxn > 0),
    ADD CONSTRAINT ck_cargos_periodo
        CHECK (periodo ~ '^[0-9]{4}-(0[1-9]|1[0-2])$'),
    ADD CONSTRAINT ck_cargos_estado
        CHECK (estado_codigo IN ('REGISTRADO', 'CANCELADO'));

ALTER TABLE pagos
    DROP CONSTRAINT IF EXISTS ck_pagos_monto_positivo,
    DROP CONSTRAINT IF EXISTS ck_pagos_periodo,
    DROP CONSTRAINT IF EXISTS ck_pagos_estado;

ALTER TABLE pagos
    ADD CONSTRAINT ck_pagos_monto_positivo
        CHECK (monto_mxn > 0),
    ADD CONSTRAINT ck_pagos_periodo
        CHECK (periodo ~ '^[0-9]{4}-(0[1-9]|1[0-2])$'),
    ADD CONSTRAINT ck_pagos_estado
        CHECK (estado_codigo IN ('REGISTRADO', 'CANCELADO'));

ALTER TABLE gastos
    DROP CONSTRAINT IF EXISTS ck_gastos_monto_positivo,
    DROP CONSTRAINT IF EXISTS ck_gastos_estado;

ALTER TABLE gastos
    ADD CONSTRAINT ck_gastos_monto_positivo
        CHECK (monto_mxn > 0),
    ADD CONSTRAINT ck_gastos_estado
        CHECK (estado_codigo IN ('REGISTRADO', 'CANCELADO'));

-- ------------------------------------------------------------
-- 7. COHERENCIA INMUEBLE / ESPACIO
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_financial_space_scope()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    actual_property_id BIGINT;
BEGIN
    SELECT espacio.condominio_id
    INTO actual_property_id
    FROM espacios espacio
    WHERE espacio.id=NEW.espacio_id;

    IF actual_property_id IS NULL THEN
        RAISE EXCEPTION 'FINANCIAL_SPACE_NOT_FOUND';
    END IF;

    IF actual_property_id <> NEW.condominio_id THEN
        RAISE EXCEPTION 'FINANCIAL_SPACE_PROPERTY_MISMATCH';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS
    trg_cargos_validate_space_scope
ON cargos;

CREATE TRIGGER trg_cargos_validate_space_scope
BEFORE INSERT OR UPDATE OF condominio_id, espacio_id
ON cargos
FOR EACH ROW
EXECUTE FUNCTION validate_financial_space_scope();

DROP TRIGGER IF EXISTS
    trg_pagos_validate_space_scope
ON pagos;

CREATE TRIGGER trg_pagos_validate_space_scope
BEFORE INSERT OR UPDATE OF condominio_id, espacio_id
ON pagos
FOR EACH ROW
EXECUTE FUNCTION validate_financial_space_scope();

-- ------------------------------------------------------------
-- 8. CANCELACIÓN CONTROLADA
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION validate_cargo_cancellation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.estado_codigo='CANCELADO' THEN
        RAISE EXCEPTION
            'FINANCIAL_MOVEMENT_ALREADY_CANCELLED';
    END IF;

    IF NEW.estado_codigo <> 'CANCELADO' THEN
        RAISE EXCEPTION
            'FINANCIAL_MOVEMENT_IS_IMMUTABLE';
    END IF;

    IF NEW.condominio_id IS DISTINCT FROM OLD.condominio_id
       OR NEW.espacio_id IS DISTINCT FROM OLD.espacio_id
       OR NEW.periodo IS DISTINCT FROM OLD.periodo
       OR NEW.tipo_codigo IS DISTINCT FROM OLD.tipo_codigo
       OR NEW.concepto IS DISTINCT FROM OLD.concepto
       OR NEW.monto_mxn IS DISTINCT FROM OLD.monto_mxn
       OR NEW.referencia IS DISTINCT FROM OLD.referencia
       OR NEW.observaciones IS DISTINCT FROM OLD.observaciones
       OR NEW.creado_en IS DISTINCT FROM OLD.creado_en
       OR NEW.creado_por IS DISTINCT FROM OLD.creado_por
    THEN
        RAISE EXCEPTION
            'FINANCIAL_ORIGINAL_DATA_IS_IMMUTABLE';
    END IF;

    IF NEW.cancelado_en IS NULL
       OR NEW.cancelado_por IS NULL
       OR NULLIF(
           BTRIM(NEW.motivo_cancelacion),
           ''
       ) IS NULL
    THEN
        RAISE EXCEPTION
            'FINANCIAL_CANCELLATION_METADATA_REQUIRED';
    END IF;

    NEW.activo=FALSE;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION validate_pago_cancellation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.estado_codigo='CANCELADO' THEN
        RAISE EXCEPTION
            'FINANCIAL_MOVEMENT_ALREADY_CANCELLED';
    END IF;

    IF NEW.estado_codigo <> 'CANCELADO' THEN
        RAISE EXCEPTION
            'FINANCIAL_MOVEMENT_IS_IMMUTABLE';
    END IF;

    IF NEW.condominio_id IS DISTINCT FROM OLD.condominio_id
       OR NEW.espacio_id IS DISTINCT FROM OLD.espacio_id
       OR NEW.periodo IS DISTINCT FROM OLD.periodo
       OR NEW.fecha IS DISTINCT FROM OLD.fecha
       OR NEW.monto_mxn IS DISTINCT FROM OLD.monto_mxn
       OR NEW.referencia IS DISTINCT FROM OLD.referencia
       OR NEW.observaciones IS DISTINCT FROM OLD.observaciones
       OR NEW.creado_en IS DISTINCT FROM OLD.creado_en
       OR NEW.creado_por IS DISTINCT FROM OLD.creado_por
    THEN
        RAISE EXCEPTION
            'FINANCIAL_ORIGINAL_DATA_IS_IMMUTABLE';
    END IF;

    IF NEW.cancelado_en IS NULL
       OR NEW.cancelado_por IS NULL
       OR NULLIF(
           BTRIM(NEW.motivo_cancelacion),
           ''
       ) IS NULL
    THEN
        RAISE EXCEPTION
            'FINANCIAL_CANCELLATION_METADATA_REQUIRED';
    END IF;

    NEW.activo=FALSE;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION validate_gasto_cancellation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.estado_codigo='CANCELADO' THEN
        RAISE EXCEPTION
            'FINANCIAL_MOVEMENT_ALREADY_CANCELLED';
    END IF;

    IF NEW.estado_codigo <> 'CANCELADO' THEN
        RAISE EXCEPTION
            'FINANCIAL_MOVEMENT_IS_IMMUTABLE';
    END IF;

    IF NEW.condominio_id IS DISTINCT FROM OLD.condominio_id
       OR NEW.fecha IS DISTINCT FROM OLD.fecha
       OR NEW.categoria_codigo IS DISTINCT
          FROM OLD.categoria_codigo
       OR NEW.concepto IS DISTINCT FROM OLD.concepto
       OR NEW.monto_mxn IS DISTINCT FROM OLD.monto_mxn
       OR NEW.referencia IS DISTINCT FROM OLD.referencia
       OR NEW.observaciones IS DISTINCT FROM OLD.observaciones
       OR NEW.creado_en IS DISTINCT FROM OLD.creado_en
       OR NEW.creado_por IS DISTINCT FROM OLD.creado_por
    THEN
        RAISE EXCEPTION
            'FINANCIAL_ORIGINAL_DATA_IS_IMMUTABLE';
    END IF;

    IF NEW.cancelado_en IS NULL
       OR NEW.cancelado_por IS NULL
       OR NULLIF(
           BTRIM(NEW.motivo_cancelacion),
           ''
       ) IS NULL
    THEN
        RAISE EXCEPTION
            'FINANCIAL_CANCELLATION_METADATA_REQUIRED';
    END IF;

    NEW.activo=FALSE;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS
    trg_cargos_validate_cancellation
ON cargos;

CREATE TRIGGER trg_cargos_validate_cancellation
BEFORE UPDATE
ON cargos
FOR EACH ROW
EXECUTE FUNCTION validate_cargo_cancellation();

DROP TRIGGER IF EXISTS
    trg_pagos_validate_cancellation
ON pagos;

CREATE TRIGGER trg_pagos_validate_cancellation
BEFORE UPDATE
ON pagos
FOR EACH ROW
EXECUTE FUNCTION validate_pago_cancellation();

DROP TRIGGER IF EXISTS
    trg_gastos_validate_cancellation
ON gastos;

CREATE TRIGGER trg_gastos_validate_cancellation
BEFORE UPDATE
ON gastos
FOR EACH ROW
EXECUTE FUNCTION validate_gasto_cancellation();

-- ------------------------------------------------------------
-- 9. ÍNDICES
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS
    idx_cargos_condominio_espacio_periodo
ON cargos(
    condominio_id,
    espacio_id,
    periodo
);

CREATE INDEX IF NOT EXISTS
    idx_cargos_condominio_estado
ON cargos(
    condominio_id,
    estado_codigo
);

CREATE INDEX IF NOT EXISTS
    idx_pagos_condominio_espacio_periodo
ON pagos(
    condominio_id,
    espacio_id,
    periodo
);

CREATE INDEX IF NOT EXISTS
    idx_pagos_condominio_fecha
ON pagos(
    condominio_id,
    fecha DESC
);

CREATE INDEX IF NOT EXISTS
    idx_pagos_condominio_estado
ON pagos(
    condominio_id,
    estado_codigo
);

CREATE INDEX IF NOT EXISTS
    idx_gastos_condominio_fecha
ON gastos(
    condominio_id,
    fecha DESC
);

CREATE INDEX IF NOT EXISTS
    idx_gastos_condominio_categoria
ON gastos(
    condominio_id,
    categoria_codigo
);

CREATE INDEX IF NOT EXISTS
    idx_gastos_condominio_estado
ON gastos(
    condominio_id,
    estado_codigo
);

COMMIT;
