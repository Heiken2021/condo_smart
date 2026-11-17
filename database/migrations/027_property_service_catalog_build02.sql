-- ============================================================
-- Condo_Smart - Build 02
-- Migration 027
-- Governed property service catalog and continuity policy
--
-- Foundation only:
--   - Does not seed universal services.
--   - Does not apply operational restrictions.
--   - Does not modify financial obligations or fees.
-- ============================================================


-- ============================================================
-- 1. Dynamic service catalog per property
-- ============================================================

CREATE TABLE IF NOT EXISTS property_service_catalog(
    id BIGSERIAL PRIMARY KEY,

    condominio_id BIGINT NOT NULL
        REFERENCES condominios(id),

    codigo VARCHAR(100) NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    categoria_codigo VARCHAR(100),

    activo BOOLEAN NOT NULL DEFAULT TRUE,

    creado_por BIGINT
        REFERENCES usuarios(id),

    creado_en TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    actualizado_por BIGINT
        REFERENCES usuarios(id),

    actualizado_en TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    UNIQUE(
        condominio_id,
        codigo
    )
);


CREATE INDEX IF NOT EXISTS
idx_property_service_catalog_property_active
ON property_service_catalog(
    condominio_id,
    activo,
    nombre
);


-- ============================================================
-- 2. Availability by hierarchical scope
--
-- INMUEBLE:
--   estructura_id and espacio_id are null.
--
-- ESTRUCTURA:
--   estructura_id is required.
--
-- ESPACIO:
--   espacio_id is required.
--
-- Availability is effective-dated and supports inheritance,
-- override, and priority.
-- ============================================================

CREATE TABLE IF NOT EXISTS property_service_availability(
    id BIGSERIAL PRIMARY KEY,

    service_id BIGINT NOT NULL
        REFERENCES property_service_catalog(id),

    scope_level VARCHAR(20) NOT NULL,

    estructura_id BIGINT
        REFERENCES estructura_inmueble(id),

    espacio_id BIGINT
        REFERENCES espacios(id),

    disponible BOOLEAN NOT NULL DEFAULT TRUE,

    hereda BOOLEAN NOT NULL DEFAULT TRUE,
    es_override BOOLEAN NOT NULL DEFAULT FALSE,

    prioridad INTEGER NOT NULL DEFAULT 100,

    vigente_desde DATE NOT NULL,
    vigente_hasta DATE,

    motivo_cambio TEXT,

    creado_por BIGINT
        REFERENCES usuarios(id),

    creado_en TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    actualizado_por BIGINT
        REFERENCES usuarios(id),

    actualizado_en TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    CHECK (
        scope_level IN (
            'INMUEBLE',
            'ESTRUCTURA',
            'ESPACIO'
        )
    ),

    CHECK (
        (
            scope_level='INMUEBLE'
            AND estructura_id IS NULL
            AND espacio_id IS NULL
        )
        OR
        (
            scope_level='ESTRUCTURA'
            AND estructura_id IS NOT NULL
            AND espacio_id IS NULL
        )
        OR
        (
            scope_level='ESPACIO'
            AND espacio_id IS NOT NULL
        )
    ),

    CHECK (
        vigente_hasta IS NULL
        OR vigente_hasta >= vigente_desde
    )
);


CREATE INDEX IF NOT EXISTS
idx_property_service_availability_service
ON property_service_availability(
    service_id,
    vigente_desde,
    vigente_hasta
);


CREATE INDEX IF NOT EXISTS
idx_property_service_availability_structure
ON property_service_availability(
    estructura_id,
    service_id
)
WHERE estructura_id IS NOT NULL;


CREATE INDEX IF NOT EXISTS
idx_property_service_availability_space
ON property_service_availability(
    espacio_id,
    service_id
)
WHERE espacio_id IS NOT NULL;


-- ============================================================
-- 3. Selective continuity policy by rule version
--
-- A continuity rule version chooses which configured services
-- participate and what governed treatment applies.
--
-- MANTENER:
--   Service remains available.
--
-- LIMITAR:
--   Partial restriction according to configured instructions.
--
-- BLOQUEAR:
--   Service becomes unavailable while the governed condition
--   remains active.
--
-- No mode is inferred globally and no service is blocked by
-- default.
-- ============================================================

CREATE TABLE IF NOT EXISTS continuity_service_policy(
    id BIGSERIAL PRIMARY KEY,

    rule_version_id BIGINT NOT NULL
        REFERENCES financial_rule_versions(id),

    service_id BIGINT NOT NULL
        REFERENCES property_service_catalog(id),

    treatment_code VARCHAR(30) NOT NULL
        DEFAULT 'MANTENER',

    restriction_detail TEXT,

    restoration_detail TEXT,

    prioridad INTEGER NOT NULL DEFAULT 100,

    activo BOOLEAN NOT NULL DEFAULT TRUE,

    creado_por BIGINT
        REFERENCES usuarios(id),

    creado_en TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    actualizado_por BIGINT
        REFERENCES usuarios(id),

    actualizado_en TIMESTAMPTZ
        NOT NULL DEFAULT NOW(),

    UNIQUE(
        rule_version_id,
        service_id
    ),

    CHECK (
        treatment_code IN (
            'MANTENER',
            'LIMITAR',
            'BLOQUEAR'
        )
    )
);


CREATE INDEX IF NOT EXISTS
idx_continuity_service_policy_version
ON continuity_service_policy(
    rule_version_id,
    activo,
    prioridad
);


CREATE INDEX IF NOT EXISTS
idx_continuity_service_policy_service
ON continuity_service_policy(
    service_id,
    activo
);


-- ============================================================
-- 4. Cross-property integrity
-- ============================================================

CREATE OR REPLACE FUNCTION
validate_property_service_availability_scope()
RETURNS TRIGGER AS $$
DECLARE
    service_property_id BIGINT;
    structure_property_id BIGINT;
    space_property_id BIGINT;
BEGIN
    SELECT condominio_id
    INTO service_property_id
    FROM property_service_catalog
    WHERE id=NEW.service_id;

    IF service_property_id IS NULL THEN
        RAISE EXCEPTION
            'PROPERTY_SERVICE_NOT_FOUND';
    END IF;

    IF NEW.estructura_id IS NOT NULL THEN
        SELECT condominio_id
        INTO structure_property_id
        FROM estructura_inmueble
        WHERE id=NEW.estructura_id;

        IF structure_property_id IS DISTINCT
           FROM service_property_id THEN
            RAISE EXCEPTION
                'PROPERTY_SERVICE_STRUCTURE_SCOPE_MISMATCH';
        END IF;
    END IF;

    IF NEW.espacio_id IS NOT NULL THEN
        SELECT condominio_id
        INTO space_property_id
        FROM espacios
        WHERE id=NEW.espacio_id;

        IF space_property_id IS DISTINCT
           FROM service_property_id THEN
            RAISE EXCEPTION
                'PROPERTY_SERVICE_SPACE_SCOPE_MISMATCH';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS
trg_validate_property_service_availability_scope
ON property_service_availability;


CREATE TRIGGER
trg_validate_property_service_availability_scope
BEFORE INSERT OR UPDATE OF
    service_id,
    scope_level,
    estructura_id,
    espacio_id
ON property_service_availability
FOR EACH ROW
EXECUTE FUNCTION
validate_property_service_availability_scope();


CREATE OR REPLACE FUNCTION
validate_continuity_service_policy()
RETURNS TRIGGER AS $$
DECLARE
    service_property_id BIGINT;
    rule_property_id BIGINT;
    rule_definition_code VARCHAR(100);
BEGIN
    SELECT condominio_id
    INTO service_property_id
    FROM property_service_catalog
    WHERE id=NEW.service_id;

    SELECT
        rule.condominio_id,
        definition.codigo
    INTO
        rule_property_id,
        rule_definition_code
    FROM financial_rule_versions version
    JOIN financial_rules rule
      ON rule.id=version.rule_id
    JOIN financial_rule_definitions definition
      ON definition.id=rule.rule_definition_id
    WHERE version.id=NEW.rule_version_id;

    IF rule_property_id IS NULL THEN
        RAISE EXCEPTION
            'CONTINUITY_RULE_VERSION_NOT_FOUND';
    END IF;

    IF rule_definition_code
       IS DISTINCT FROM
       'CONTINUIDAD_SERVICIOS' THEN
        RAISE EXCEPTION
            'CONTINUITY_SERVICE_POLICY_INVALID_RULE';
    END IF;

    IF service_property_id
       IS DISTINCT FROM
       rule_property_id THEN
        RAISE EXCEPTION
            'CONTINUITY_SERVICE_POLICY_PROPERTY_MISMATCH';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS
trg_validate_continuity_service_policy
ON continuity_service_policy;


CREATE TRIGGER
trg_validate_continuity_service_policy
BEFORE INSERT OR UPDATE OF
    rule_version_id,
    service_id
ON continuity_service_policy
FOR EACH ROW
EXECUTE FUNCTION
validate_continuity_service_policy();


-- ============================================================
-- Explicit non-goals
-- ============================================================
-- This migration intentionally does not:
--   - seed service catalog records;
--   - create operational restriction records;
--   - block services for any resident or space;
--   - alter financial obligations;
--   - alter payment allocations;
--   - alter space_fee_history;
--   - encode an 80 percent threshold;
--   - encode a 3 day tolerance.
