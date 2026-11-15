BEGIN;

-- ============================================================
-- CONDO_SMART · BUILD 02
-- FINANCIAL GOVERNANCE FOUNDATION
--
-- Modelo de precedencia:
--
-- CORE
-- -> TYPE / BUSINESS TYPE
-- -> PROPERTY
-- -> STRUCTURE
-- -> SPACE
-- -> APPROVED EXCEPTION
--
-- Esta migración define gobierno financiero.
-- NO genera obligaciones.
-- NO registra pagos.
-- NO calcula KPIs.
-- NO permite ejecución autónoma de IA.
-- ============================================================


-- ------------------------------------------------------------
-- 01. DEFINICIONES DE REGLAS
--
-- Catálogo gobernado de QUÉ puede regular Condo_Smart.
--
-- Una definición puede ser:
-- - obligatoria;
-- - especializable;
-- - heredable;
-- - sobreescribible;
-- - excepcionable.
--
-- La definición NO contiene el valor económico particular
-- de un inmueble.
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS financial_rule_definitions(
    id BIGSERIAL PRIMARY KEY,

    codigo VARCHAR(100)
        NOT NULL
        UNIQUE,

    nombre VARCHAR(200)
        NOT NULL,

    descripcion TEXT,

    dominio_codigo VARCHAR(80)
        NOT NULL,

    nivel_base_codigo VARCHAR(30)
        NOT NULL
        DEFAULT 'CORE',

    tipo_resultado VARCHAR(40)
        NOT NULL,

    esquema_parametros JSONB
        NOT NULL
        DEFAULT '{}'::jsonb,

    obligatoria BOOLEAN
        NOT NULL
        DEFAULT FALSE,

    admite_especializacion BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    admite_herencia BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    admite_override BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    admite_excepcion BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    requiere_aprobacion BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    permite_nivel_inmueble BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    permite_nivel_estructura BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    permite_nivel_espacio BOOLEAN
        NOT NULL
        DEFAULT FALSE,

    contexto_kpi BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    contexto_ia BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    activo BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    creado_en TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW(),

    CHECK (
        nivel_base_codigo IN (
            'CORE',
            'TIPOLOGIA'
        )
    )
);


-- ------------------------------------------------------------
-- 02. APLICABILIDAD POR TIPOLOGÍA / GIRO
--
-- Permite declarar compatibilidad sin codificar casos
-- especiales dentro del motor.
--
-- Ejemplos futuros:
-- - tipo de inmueble;
-- - tipo estructural;
-- - tipo de espacio;
-- - giro de negocio.
--
-- valor_codigo se relacionará con los catálogos gobernados
-- correspondientes.
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS
financial_rule_applicability(
    id BIGSERIAL PRIMARY KEY,

    rule_definition_id BIGINT NOT NULL
        REFERENCES financial_rule_definitions(id),

    dimension_codigo VARCHAR(40)
        NOT NULL,

    valor_codigo VARCHAR(100)
        NOT NULL,

    incluido BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    creado_en TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW(),

    UNIQUE(
        rule_definition_id,
        dimension_codigo,
        valor_codigo
    ),

    CHECK (
        dimension_codigo IN (
            'TIPO_INMUEBLE',
            'TIPO_ESTRUCTURA',
            'TIPO_ESPACIO',
            'GIRO'
        )
    )
);


-- ------------------------------------------------------------
-- 03. OBJETIVOS FINANCIEROS
--
-- Cada inmueble puede definir objetivos propios.
-- Opcionalmente pueden especializarse por estructura.
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS financial_objectives(
    id BIGSERIAL PRIMARY KEY,

    condominio_id BIGINT NOT NULL
        REFERENCES condominios(id),

    estructura_id BIGINT
        REFERENCES estructura_inmueble(id),

    codigo VARCHAR(80)
        NOT NULL,

    nombre VARCHAR(200)
        NOT NULL,

    descripcion TEXT,

    tipo_objetivo VARCHAR(80),

    parametros JSONB
        NOT NULL
        DEFAULT '{}'::jsonb,

    vigente_desde DATE NOT NULL,
    vigente_hasta DATE,

    estado_codigo VARCHAR(30)
        NOT NULL
        DEFAULT 'BORRADOR',

    prioridad INTEGER
        NOT NULL
        DEFAULT 100,

    creado_por BIGINT
        REFERENCES usuarios(id),

    aprobado_por BIGINT
        REFERENCES usuarios(id),

    aprobado_en TIMESTAMPTZ,

    motivo_cambio TEXT,

    creado_en TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW(),

    CHECK (
        vigente_hasta IS NULL
        OR vigente_hasta >= vigente_desde
    ),

    CHECK (
        estado_codigo IN (
            'BORRADOR',
            'APROBADO',
            'INACTIVO'
        )
    )
);


CREATE INDEX IF NOT EXISTS
idx_financial_objectives_scope
ON financial_objectives(
    condominio_id,
    estructura_id,
    vigente_desde
);


-- ------------------------------------------------------------
-- 04. POLÍTICAS FINANCIERAS
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS financial_policies(
    id BIGSERIAL PRIMARY KEY,

    condominio_id BIGINT NOT NULL
        REFERENCES condominios(id),

    estructura_id BIGINT
        REFERENCES estructura_inmueble(id),

    objective_id BIGINT
        REFERENCES financial_objectives(id),

    codigo VARCHAR(80)
        NOT NULL,

    nombre VARCHAR(200)
        NOT NULL,

    descripcion TEXT,

    parametros JSONB
        NOT NULL
        DEFAULT '{}'::jsonb,

    vigente_desde DATE NOT NULL,
    vigente_hasta DATE,

    estado_codigo VARCHAR(30)
        NOT NULL
        DEFAULT 'BORRADOR',

    prioridad INTEGER
        NOT NULL
        DEFAULT 100,

    hereda BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    creado_por BIGINT
        REFERENCES usuarios(id),

    aprobado_por BIGINT
        REFERENCES usuarios(id),

    aprobado_en TIMESTAMPTZ,

    motivo_cambio TEXT,

    creado_en TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW(),

    CHECK (
        vigente_hasta IS NULL
        OR vigente_hasta >= vigente_desde
    ),

    CHECK (
        estado_codigo IN (
            'BORRADOR',
            'APROBADO',
            'INACTIVO'
        )
    )
);


CREATE INDEX IF NOT EXISTS
idx_financial_policies_scope
ON financial_policies(
    condominio_id,
    estructura_id,
    vigente_desde
);


-- ------------------------------------------------------------
-- 05. INSTANCIAS DE REGLAS
--
-- Representa una regla aplicada/configurada para un contexto
-- concreto.
--
-- scope_level determina la capa de precedencia.
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS financial_rules(
    id BIGSERIAL PRIMARY KEY,

    rule_definition_id BIGINT NOT NULL
        REFERENCES financial_rule_definitions(id),

    policy_id BIGINT
        REFERENCES financial_policies(id),

    scope_level VARCHAR(30)
        NOT NULL,

    condominio_id BIGINT
        REFERENCES condominios(id),

    estructura_id BIGINT
        REFERENCES estructura_inmueble(id),

    espacio_id BIGINT
        REFERENCES espacios(id),

    tipo_aplicable_codigo VARCHAR(100),

    codigo VARCHAR(100)
        NOT NULL,

    nombre VARCHAR(200)
        NOT NULL,

    descripcion TEXT,

    hereda BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    es_override BOOLEAN
        NOT NULL
        DEFAULT FALSE,

    prioridad INTEGER
        NOT NULL
        DEFAULT 100,

    activo BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    creado_por BIGINT
        REFERENCES usuarios(id),

    creado_en TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW(),

    CHECK (
        scope_level IN (
            'CORE',
            'TIPOLOGIA',
            'INMUEBLE',
            'ESTRUCTURA',
            'ESPACIO'
        )
    ),

    CHECK (
        (
            scope_level IN (
                'CORE',
                'TIPOLOGIA'
            )
            AND condominio_id IS NULL
            AND estructura_id IS NULL
            AND espacio_id IS NULL
        )
        OR
        (
            scope_level='INMUEBLE'
            AND condominio_id IS NOT NULL
            AND estructura_id IS NULL
            AND espacio_id IS NULL
        )
        OR
        (
            scope_level='ESTRUCTURA'
            AND condominio_id IS NOT NULL
            AND estructura_id IS NOT NULL
            AND espacio_id IS NULL
        )
        OR
        (
            scope_level='ESPACIO'
            AND condominio_id IS NOT NULL
            AND espacio_id IS NOT NULL
        )
    )
);


CREATE INDEX IF NOT EXISTS
idx_financial_rules_resolution
ON financial_rules(
    rule_definition_id,
    scope_level,
    condominio_id,
    estructura_id,
    espacio_id,
    prioridad,
    activo
);


-- ------------------------------------------------------------
-- 06. VERSIONES INMUTABLES DE REGLA
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS financial_rule_versions(
    id BIGSERIAL PRIMARY KEY,

    rule_id BIGINT NOT NULL
        REFERENCES financial_rules(id),

    version_num INTEGER
        NOT NULL,

    vigente_desde DATE
        NOT NULL,

    vigente_hasta DATE,

    estado_codigo VARCHAR(30)
        NOT NULL
        DEFAULT 'BORRADOR',

    parametros JSONB
        NOT NULL
        DEFAULT '{}'::jsonb,

    creado_por BIGINT
        REFERENCES usuarios(id),

    aprobado_por BIGINT
        REFERENCES usuarios(id),

    aprobado_en TIMESTAMPTZ,

    motivo_cambio TEXT,

    creado_en TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW(),

    UNIQUE(
        rule_id,
        version_num
    ),

    CHECK (
        version_num > 0
    ),

    CHECK (
        vigente_hasta IS NULL
        OR vigente_hasta >= vigente_desde
    ),

    CHECK (
        estado_codigo IN (
            'BORRADOR',
            'APROBADO',
            'INACTIVO'
        )
    )
);


CREATE INDEX IF NOT EXISTS
idx_financial_rule_versions_effective
ON financial_rule_versions(
    rule_id,
    vigente_desde,
    vigente_hasta,
    estado_codigo
);


-- ------------------------------------------------------------
-- 07. HISTÓRICO DE CUOTAS POR ESPACIO
--
-- espacios.cuota_base permanece por compatibilidad.
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS space_fee_history(
    id BIGSERIAL PRIMARY KEY,

    condominio_id BIGINT NOT NULL
        REFERENCES condominios(id),

    espacio_id BIGINT NOT NULL
        REFERENCES espacios(id),

    tipo_cuota_codigo VARCHAR(80)
        NOT NULL,

    monto_mxn NUMERIC(14,2)
        NOT NULL,

    vigente_desde DATE
        NOT NULL,

    vigente_hasta DATE,

    origen_codigo VARCHAR(40)
        NOT NULL
        DEFAULT 'CONFIGURACION',

    rule_version_id BIGINT
        REFERENCES financial_rule_versions(id),

    estado_codigo VARCHAR(30)
        NOT NULL
        DEFAULT 'APROBADO',

    creado_por BIGINT
        REFERENCES usuarios(id),

    aprobado_por BIGINT
        REFERENCES usuarios(id),

    aprobado_en TIMESTAMPTZ,

    motivo_cambio TEXT,

    creado_en TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW(),

    CHECK (
        monto_mxn >= 0
    ),

    CHECK (
        vigente_hasta IS NULL
        OR vigente_hasta >= vigente_desde
    ),

    CHECK (
        estado_codigo IN (
            'BORRADOR',
            'APROBADO',
            'INACTIVO'
        )
    )
);


CREATE INDEX IF NOT EXISTS
idx_space_fee_history_effective
ON space_fee_history(
    condominio_id,
    espacio_id,
    tipo_cuota_codigo,
    vigente_desde,
    vigente_hasta
);


-- ------------------------------------------------------------
-- 08. EXCEPCIONES FINANCIERAS
--
-- Una excepción nunca modifica la regla histórica.
-- Declara una desviación gobernada de una regla vigente.
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS financial_rule_exceptions(
    id BIGSERIAL PRIMARY KEY,

    condominio_id BIGINT NOT NULL
        REFERENCES condominios(id),

    estructura_id BIGINT
        REFERENCES estructura_inmueble(id),

    espacio_id BIGINT
        REFERENCES espacios(id),

    rule_version_id BIGINT NOT NULL
        REFERENCES financial_rule_versions(id),

    tipo_excepcion VARCHAR(80),

    parametros JSONB
        NOT NULL
        DEFAULT '{}'::jsonb,

    motivo TEXT
        NOT NULL,

    estado_codigo VARCHAR(30)
        NOT NULL
        DEFAULT 'PENDIENTE',

    vigente_desde DATE,
    vigente_hasta DATE,

    solicitado_por BIGINT
        REFERENCES usuarios(id),

    solicitado_en TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW(),

    resuelto_por BIGINT
        REFERENCES usuarios(id),

    resuelto_en TIMESTAMPTZ,

    decision_detalle TEXT,

    CHECK (
        vigente_hasta IS NULL
        OR vigente_desde IS NULL
        OR vigente_hasta >= vigente_desde
    ),

    CHECK (
        estado_codigo IN (
            'PENDIENTE',
            'APROBADA',
            'RECHAZADA',
            'CANCELADA',
            'VENCIDA'
        )
    )
);


CREATE INDEX IF NOT EXISTS
idx_financial_rule_exceptions_scope
ON financial_rule_exceptions(
    condominio_id,
    estructura_id,
    espacio_id,
    estado_codigo
);


-- ------------------------------------------------------------
-- 09. VALIDACIÓN DE SCOPE DE GOBIERNO
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION
validate_financial_governance_scope()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    structure_property_id BIGINT;
    space_property_id BIGINT;
BEGIN

    IF NEW.estructura_id IS NOT NULL THEN

        SELECT condominio_id
        INTO structure_property_id
        FROM estructura_inmueble
        WHERE id=NEW.estructura_id;

        IF structure_property_id IS NULL THEN
            RAISE EXCEPTION
                'FINANCIAL_GOVERNANCE_STRUCTURE_NOT_FOUND';
        END IF;

        IF NEW.condominio_id IS NULL
           OR structure_property_id
              <> NEW.condominio_id
        THEN
            RAISE EXCEPTION
                'FINANCIAL_GOVERNANCE_SCOPE_MISMATCH';
        END IF;

    END IF;


    IF NEW.espacio_id IS NOT NULL THEN

        SELECT condominio_id
        INTO space_property_id
        FROM espacios
        WHERE id=NEW.espacio_id;

        IF space_property_id IS NULL THEN
            RAISE EXCEPTION
                'FINANCIAL_GOVERNANCE_SPACE_NOT_FOUND';
        END IF;

        IF NEW.condominio_id IS NULL
           OR space_property_id
              <> NEW.condominio_id
        THEN
            RAISE EXCEPTION
                'FINANCIAL_GOVERNANCE_SPACE_SCOPE_MISMATCH';
        END IF;

    END IF;

    RETURN NEW;
END;
$$;


DROP TRIGGER IF EXISTS
trg_financial_rules_scope
ON financial_rules;

CREATE TRIGGER
trg_financial_rules_scope
BEFORE INSERT OR UPDATE OF
    condominio_id,
    estructura_id,
    espacio_id,
    scope_level
ON financial_rules
FOR EACH ROW
EXECUTE FUNCTION
validate_financial_governance_scope();


DROP TRIGGER IF EXISTS
trg_financial_exceptions_scope
ON financial_rule_exceptions;

CREATE TRIGGER
trg_financial_exceptions_scope
BEFORE INSERT OR UPDATE OF
    condominio_id,
    estructura_id,
    espacio_id
ON financial_rule_exceptions
FOR EACH ROW
EXECUTE FUNCTION
validate_financial_governance_scope();


-- ------------------------------------------------------------
-- 10. VALIDACIÓN DE CUOTA / ESPACIO
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION
validate_space_fee_scope()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    space_property_id BIGINT;
BEGIN

    SELECT condominio_id
    INTO space_property_id
    FROM espacios
    WHERE id=NEW.espacio_id;

    IF space_property_id IS NULL THEN
        RAISE EXCEPTION
            'FINANCIAL_FEE_SPACE_NOT_FOUND';
    END IF;

    IF space_property_id <> NEW.condominio_id THEN
        RAISE EXCEPTION
            'FINANCIAL_FEE_SCOPE_MISMATCH';
    END IF;

    RETURN NEW;
END;
$$;


DROP TRIGGER IF EXISTS
trg_space_fee_scope
ON space_fee_history;

CREATE TRIGGER
trg_space_fee_scope
BEFORE INSERT OR UPDATE OF
    condominio_id,
    espacio_id
ON space_fee_history
FOR EACH ROW
EXECUTE FUNCTION
validate_space_fee_scope();


-- ------------------------------------------------------------
-- 11. CATÁLOGOS DE GOBIERNO
-- ------------------------------------------------------------

INSERT INTO catalogos(
    codigo,
    nombre,
    activo
)
VALUES
    (
        'FINANCIAL_RULE_DOMAIN',
        'Dominio De Regla Financiera',
        TRUE
    ),
    (
        'FINANCIAL_FEE_TYPE',
        'Tipo De Cuota Financiera',
        TRUE
    ),
    (
        'FINANCIAL_RULE_SCOPE',
        'Nivel De Aplicación De Regla',
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
    value.codigo,
    value.nombre,
    TRUE
FROM catalogos catalogo
JOIN (
    VALUES

        (
            'FINANCIAL_RULE_DOMAIN',
            'OBLIGACIONES',
            'Obligaciones'
        ),
        (
            'FINANCIAL_RULE_DOMAIN',
            'PAGOS',
            'Pagos'
        ),
        (
            'FINANCIAL_RULE_DOMAIN',
            'EXCEPCIONES',
            'Excepciones'
        ),
        (
            'FINANCIAL_RULE_DOMAIN',
            'COBRANZA',
            'Cobranza'
        ),

        (
            'FINANCIAL_FEE_TYPE',
            'MANTENIMIENTO_ORDINARIO',
            'Mantenimiento Ordinario'
        ),
        (
            'FINANCIAL_FEE_TYPE',
            'EXTRAORDINARIA',
            'Cuota Extraordinaria'
        ),

        (
            'FINANCIAL_RULE_SCOPE',
            'CORE',
            'Estándar Condo Smart'
        ),
        (
            'FINANCIAL_RULE_SCOPE',
            'TIPOLOGIA',
            'Tipología O Giro'
        ),
        (
            'FINANCIAL_RULE_SCOPE',
            'INMUEBLE',
            'Inmueble'
        ),
        (
            'FINANCIAL_RULE_SCOPE',
            'ESTRUCTURA',
            'Estructura'
        ),
        (
            'FINANCIAL_RULE_SCOPE',
            'ESPACIO',
            'Espacio'
        )

) AS value(
    catalog_code,
    codigo,
    nombre
)
ON catalogo.codigo=value.catalog_code

ON CONFLICT(
    catalogo_id,
    codigo
)
DO NOTHING;


-- ------------------------------------------------------------
-- 12. PERMISOS
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
        'FINANZAS_GOBIERNO_CONSULTAR',
        'Consultar Gobierno Financiero',
        'FINANZAS',
        'READ',
        TRUE
    ),

    (
        'FINANZAS_OBJETIVO_GESTIONAR',
        'Gestionar Objetivos Financieros',
        'FINANZAS',
        'UPDATE',
        TRUE
    ),

    (
        'FINANZAS_POLITICA_GESTIONAR',
        'Gestionar Políticas Financieras',
        'FINANZAS',
        'UPDATE',
        TRUE
    ),

    (
        'FINANZAS_REGLA_GESTIONAR',
        'Gestionar Reglas Financieras',
        'FINANZAS',
        'UPDATE',
        TRUE
    ),

    (
        'FINANZAS_REGLA_APROBAR',
        'Aprobar Reglas Financieras',
        'FINANZAS',
        'APPROVE',
        TRUE
    ),

    (
        'FINANZAS_CUOTA_GESTIONAR',
        'Gestionar Vigencia De Cuotas',
        'FINANZAS',
        'UPDATE',
        TRUE
    ),

    (
        'FINANZAS_EXCEPCION_SOLICITAR',
        'Solicitar Excepción Financiera',
        'FINANZAS',
        'CREATE',
        TRUE
    ),

    (
        'FINANZAS_EXCEPCION_RESOLVER',
        'Resolver Excepción Financiera',
        'FINANZAS',
        'APPROVE',
        TRUE
    )

ON CONFLICT (codigo) DO NOTHING;


-- Lectura de gobierno financiero.

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
  ON permiso.codigo=
     'FINANZAS_GOBIERNO_CONSULTAR'

WHERE rol.codigo IN (
    'ADMINISTRADOR',
    'GERENTE',
    'CONTABILIDAD',
    'COMITE'
)

ON CONFLICT DO NOTHING;


-- Gestión inicial conservadora.

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
      'FINANZAS_OBJETIVO_GESTIONAR',
      'FINANZAS_POLITICA_GESTIONAR',
      'FINANZAS_REGLA_GESTIONAR',
      'FINANZAS_REGLA_APROBAR',
      'FINANZAS_CUOTA_GESTIONAR',
      'FINANZAS_EXCEPCION_SOLICITAR',
      'FINANZAS_EXCEPCION_RESOLVER'
  )

WHERE rol.codigo='ADMINISTRADOR'

ON CONFLICT DO NOTHING;



-- ------------------------------------------------------------
-- 13. INTEGRIDAD DE OBJETIVOS Y POLÍTICAS
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION
validate_financial_property_structure_scope()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    structure_property_id BIGINT;
BEGIN
    IF NEW.estructura_id IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT condominio_id
    INTO structure_property_id
    FROM estructura_inmueble
    WHERE id=NEW.estructura_id;

    IF structure_property_id IS NULL THEN
        RAISE EXCEPTION
            'FINANCIAL_GOVERNANCE_STRUCTURE_NOT_FOUND';
    END IF;

    IF structure_property_id <> NEW.condominio_id THEN
        RAISE EXCEPTION
            'FINANCIAL_GOVERNANCE_SCOPE_MISMATCH';
    END IF;

    RETURN NEW;
END;
$$;


DROP TRIGGER IF EXISTS
trg_financial_objectives_scope
ON financial_objectives;

CREATE TRIGGER
trg_financial_objectives_scope
BEFORE INSERT OR UPDATE OF
    condominio_id,
    estructura_id
ON financial_objectives
FOR EACH ROW
EXECUTE FUNCTION
validate_financial_property_structure_scope();


DROP TRIGGER IF EXISTS
trg_financial_policies_scope
ON financial_policies;

CREATE TRIGGER
trg_financial_policies_scope
BEFORE INSERT OR UPDATE OF
    condominio_id,
    estructura_id
ON financial_policies
FOR EACH ROW
EXECUTE FUNCTION
validate_financial_property_structure_scope();


-- ------------------------------------------------------------
-- 14. INTEGRIDAD OBJETIVO / POLÍTICA
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION
validate_financial_policy_objective()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    objective_row RECORD;
BEGIN
    IF NEW.objective_id IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT
        condominio_id,
        estructura_id
    INTO objective_row
    FROM financial_objectives
    WHERE id=NEW.objective_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'FINANCIAL_OBJECTIVE_NOT_FOUND';
    END IF;

    IF objective_row.condominio_id
       <> NEW.condominio_id
    THEN
        RAISE EXCEPTION
            'FINANCIAL_POLICY_OBJECTIVE_SCOPE_MISMATCH';
    END IF;

    IF objective_row.estructura_id IS NOT NULL
       AND objective_row.estructura_id
           IS DISTINCT FROM NEW.estructura_id
    THEN
        RAISE EXCEPTION
            'FINANCIAL_POLICY_OBJECTIVE_STRUCTURE_MISMATCH';
    END IF;

    RETURN NEW;
END;
$$;


DROP TRIGGER IF EXISTS
trg_financial_policy_objective
ON financial_policies;

CREATE TRIGGER
trg_financial_policy_objective
BEFORE INSERT OR UPDATE OF
    objective_id,
    condominio_id,
    estructura_id
ON financial_policies
FOR EACH ROW
EXECUTE FUNCTION
validate_financial_policy_objective();


-- ------------------------------------------------------------
-- 15. CAPACIDADES DE DEFINICIÓN DE REGLA
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION
validate_financial_rule_capabilities()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    definition_row RECORD;
BEGIN
    SELECT *
    INTO definition_row
    FROM financial_rule_definitions
    WHERE id=NEW.rule_definition_id
      AND activo=TRUE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'FINANCIAL_RULE_DEFINITION_NOT_FOUND';
    END IF;

    IF NEW.scope_level='TIPOLOGIA'
       AND NOT definition_row.admite_especializacion
    THEN
        RAISE EXCEPTION
            'FINANCIAL_RULE_SPECIALIZATION_NOT_ALLOWED';
    END IF;

    IF NEW.scope_level='INMUEBLE'
       AND NOT definition_row.permite_nivel_inmueble
    THEN
        RAISE EXCEPTION
            'FINANCIAL_RULE_PROPERTY_LEVEL_NOT_ALLOWED';
    END IF;

    IF NEW.scope_level='ESTRUCTURA'
       AND NOT definition_row.permite_nivel_estructura
    THEN
        RAISE EXCEPTION
            'FINANCIAL_RULE_STRUCTURE_LEVEL_NOT_ALLOWED';
    END IF;

    IF NEW.scope_level='ESPACIO'
       AND NOT definition_row.permite_nivel_espacio
    THEN
        RAISE EXCEPTION
            'FINANCIAL_RULE_SPACE_LEVEL_NOT_ALLOWED';
    END IF;

    IF NEW.es_override
       AND NOT definition_row.admite_override
    THEN
        RAISE EXCEPTION
            'FINANCIAL_RULE_OVERRIDE_NOT_ALLOWED';
    END IF;

    IF NEW.hereda
       AND NOT definition_row.admite_herencia
    THEN
        RAISE EXCEPTION
            'FINANCIAL_RULE_INHERITANCE_NOT_ALLOWED';
    END IF;

    IF definition_row.obligatoria
       AND NOT definition_row.admite_override
       AND NEW.scope_level NOT IN (
           'CORE',
           'TIPOLOGIA'
       )
    THEN
        RAISE EXCEPTION
            'FINANCIAL_MANDATORY_RULE_CANNOT_BE_REDEFINED';
    END IF;

    RETURN NEW;
END;
$$;


DROP TRIGGER IF EXISTS
trg_financial_rule_capabilities
ON financial_rules;

CREATE TRIGGER
trg_financial_rule_capabilities
BEFORE INSERT OR UPDATE OF
    rule_definition_id,
    scope_level,
    hereda,
    es_override
ON financial_rules
FOR EACH ROW
EXECUTE FUNCTION
validate_financial_rule_capabilities();


-- ------------------------------------------------------------
-- 16. APROBACIÓN COMPLETA Y TRAZABLE
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION
validate_financial_approval_metadata()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.estado_codigo='APROBADO'
       AND (
           NEW.aprobado_por IS NULL
           OR NEW.aprobado_en IS NULL
       )
    THEN
        RAISE EXCEPTION
            'FINANCIAL_APPROVAL_METADATA_REQUIRED';
    END IF;

    RETURN NEW;
END;
$$;


DROP TRIGGER IF EXISTS
trg_financial_objective_approval
ON financial_objectives;

CREATE TRIGGER
trg_financial_objective_approval
BEFORE INSERT OR UPDATE OF
    estado_codigo,
    aprobado_por,
    aprobado_en
ON financial_objectives
FOR EACH ROW
EXECUTE FUNCTION
validate_financial_approval_metadata();


DROP TRIGGER IF EXISTS
trg_financial_policy_approval
ON financial_policies;

CREATE TRIGGER
trg_financial_policy_approval
BEFORE INSERT OR UPDATE OF
    estado_codigo,
    aprobado_por,
    aprobado_en
ON financial_policies
FOR EACH ROW
EXECUTE FUNCTION
validate_financial_approval_metadata();


DROP TRIGGER IF EXISTS
trg_financial_rule_version_approval
ON financial_rule_versions;

CREATE TRIGGER
trg_financial_rule_version_approval
BEFORE INSERT OR UPDATE OF
    estado_codigo,
    aprobado_por,
    aprobado_en
ON financial_rule_versions
FOR EACH ROW
EXECUTE FUNCTION
validate_financial_approval_metadata();


DROP TRIGGER IF EXISTS
trg_space_fee_approval
ON space_fee_history;

CREATE TRIGGER
trg_space_fee_approval
BEFORE INSERT OR UPDATE OF
    estado_codigo,
    aprobado_por,
    aprobado_en
ON space_fee_history
FOR EACH ROW
EXECUTE FUNCTION
validate_financial_approval_metadata();


-- ------------------------------------------------------------
-- 17. VIGENCIAS APROBADAS NO SUPERPUESTAS
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION
validate_financial_rule_version_overlap()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.estado_codigo <> 'APROBADO' THEN
        RETURN NEW;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM financial_rule_versions existing
        WHERE existing.rule_id=NEW.rule_id
          AND existing.estado_codigo='APROBADO'
          AND existing.id <> COALESCE(NEW.id, 0)
          AND daterange(
              existing.vigente_desde,
              COALESCE(
                  existing.vigente_hasta + 1,
                  'infinity'::date
              ),
              '[)'
          )
          &&
          daterange(
              NEW.vigente_desde,
              COALESCE(
                  NEW.vigente_hasta + 1,
                  'infinity'::date
              ),
              '[)'
          )
    ) THEN
        RAISE EXCEPTION
            'FINANCIAL_RULE_VERSION_OVERLAP';
    END IF;

    RETURN NEW;
END;
$$;


DROP TRIGGER IF EXISTS
trg_financial_rule_version_overlap
ON financial_rule_versions;

CREATE TRIGGER
trg_financial_rule_version_overlap
BEFORE INSERT OR UPDATE OF
    rule_id,
    vigente_desde,
    vigente_hasta,
    estado_codigo
ON financial_rule_versions
FOR EACH ROW
EXECUTE FUNCTION
validate_financial_rule_version_overlap();


CREATE OR REPLACE FUNCTION
validate_space_fee_overlap()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.estado_codigo <> 'APROBADO' THEN
        RETURN NEW;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM space_fee_history existing
        WHERE existing.condominio_id=NEW.condominio_id
          AND existing.espacio_id=NEW.espacio_id
          AND existing.tipo_cuota_codigo=
              NEW.tipo_cuota_codigo
          AND existing.estado_codigo='APROBADO'
          AND existing.id <> COALESCE(NEW.id, 0)
          AND daterange(
              existing.vigente_desde,
              COALESCE(
                  existing.vigente_hasta + 1,
                  'infinity'::date
              ),
              '[)'
          )
          &&
          daterange(
              NEW.vigente_desde,
              COALESCE(
                  NEW.vigente_hasta + 1,
                  'infinity'::date
              ),
              '[)'
          )
    ) THEN
        RAISE EXCEPTION
            'FINANCIAL_SPACE_FEE_OVERLAP';
    END IF;

    RETURN NEW;
END;
$$;


DROP TRIGGER IF EXISTS
trg_space_fee_overlap
ON space_fee_history;

CREATE TRIGGER
trg_space_fee_overlap
BEFORE INSERT OR UPDATE OF
    condominio_id,
    espacio_id,
    tipo_cuota_codigo,
    vigente_desde,
    vigente_hasta,
    estado_codigo
ON space_fee_history
FOR EACH ROW
EXECUTE FUNCTION
validate_space_fee_overlap();


-- ------------------------------------------------------------
-- 18. EXCEPCIONES PERMITIDAS Y ATRIBUIBLES
-- ------------------------------------------------------------

CREATE OR REPLACE FUNCTION
validate_financial_rule_exception()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    version_row RECORD;
BEGIN
    SELECT
        definition.admite_excepcion,
        rule.condominio_id,
        rule.estructura_id,
        rule.espacio_id
    INTO version_row
    FROM financial_rule_versions version
    JOIN financial_rules rule
      ON rule.id=version.rule_id
    JOIN financial_rule_definitions definition
      ON definition.id=
         rule.rule_definition_id
    WHERE version.id=NEW.rule_version_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'FINANCIAL_RULE_VERSION_NOT_FOUND';
    END IF;

    IF NOT version_row.admite_excepcion THEN
        RAISE EXCEPTION
            'FINANCIAL_RULE_EXCEPTION_NOT_ALLOWED';
    END IF;

    IF version_row.condominio_id IS NOT NULL
       AND version_row.condominio_id
           <> NEW.condominio_id
    THEN
        RAISE EXCEPTION
            'FINANCIAL_EXCEPTION_RULE_SCOPE_MISMATCH';
    END IF;

    IF NEW.solicitado_por IS NULL THEN
        RAISE EXCEPTION
            'FINANCIAL_EXCEPTION_REQUESTER_REQUIRED';
    END IF;

    IF NEW.estado_codigo IN (
        'APROBADA',
        'RECHAZADA'
    )
       AND (
           NEW.resuelto_por IS NULL
           OR NEW.resuelto_en IS NULL
           OR NULLIF(
               BTRIM(NEW.decision_detalle),
               ''
           ) IS NULL
       )
    THEN
        RAISE EXCEPTION
            'FINANCIAL_EXCEPTION_DECISION_REQUIRED';
    END IF;

    RETURN NEW;
END;
$$;


DROP TRIGGER IF EXISTS
trg_financial_rule_exception
ON financial_rule_exceptions;

CREATE TRIGGER
trg_financial_rule_exception
BEFORE INSERT OR UPDATE
ON financial_rule_exceptions
FOR EACH ROW
EXECUTE FUNCTION
validate_financial_rule_exception();


-- ------------------------------------------------------------
-- 19. VERSIONES APROBADAS INMUTABLES
-- ------------------------------------------------------------

ALTER TABLE financial_rule_versions
    ADD COLUMN IF NOT EXISTS cerrado_por BIGINT
        REFERENCES usuarios(id),
    ADD COLUMN IF NOT EXISTS cerrado_en TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS motivo_cierre TEXT;


CREATE OR REPLACE FUNCTION
prevent_approved_financial_rule_version_mutation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.estado_codigo <> 'APROBADO' THEN
        RETURN NEW;
    END IF;

    IF TG_OP='DELETE' THEN
        RAISE EXCEPTION
            'APPROVED_FINANCIAL_RULE_VERSION_IS_IMMUTABLE';
    END IF;

    IF OLD.vigente_hasta IS NOT NULL THEN
        RAISE EXCEPTION
            'CLOSED_FINANCIAL_RULE_VERSION_IS_IMMUTABLE';
    END IF;

    IF NEW.vigente_hasta IS NULL
       OR NEW.cerrado_por IS NULL
       OR NEW.cerrado_en IS NULL
       OR NULLIF(
           BTRIM(NEW.motivo_cierre),
           ''
       ) IS NULL
    THEN
        RAISE EXCEPTION
            'FINANCIAL_RULE_VERSION_CLOSURE_METADATA_REQUIRED';
    END IF;

    IF (
        to_jsonb(NEW)
        - ARRAY[
            'vigente_hasta',
            'cerrado_por',
            'cerrado_en',
            'motivo_cierre'
        ]
    )
    IS DISTINCT FROM
    (
        to_jsonb(OLD)
        - ARRAY[
            'vigente_hasta',
            'cerrado_por',
            'cerrado_en',
            'motivo_cierre'
        ]
    )
    THEN
        RAISE EXCEPTION
            'APPROVED_FINANCIAL_RULE_VERSION_IS_IMMUTABLE';
    END IF;

    RETURN NEW;
END;
$$;


DROP TRIGGER IF EXISTS
trg_financial_rule_version_immutable
ON financial_rule_versions;

CREATE TRIGGER
trg_financial_rule_version_immutable
BEFORE UPDATE OR DELETE
ON financial_rule_versions
FOR EACH ROW
EXECUTE FUNCTION
prevent_approved_financial_rule_version_mutation();


COMMIT;
