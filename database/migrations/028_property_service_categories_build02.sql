-- ============================================================
-- Condo_Smart - Build 02
-- Migration 028
-- Dynamic service categories by property
-- ============================================================

CREATE TABLE IF NOT EXISTS property_service_categories(
    id BIGSERIAL PRIMARY KEY,

    condominio_id BIGINT NOT NULL
        REFERENCES condominios(id),

    codigo VARCHAR(100) NOT NULL,
    nombre VARCHAR(160) NOT NULL,
    descripcion TEXT,

    orden INTEGER NOT NULL DEFAULT 100,

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
    ),

    CHECK (
        orden >= 0
    )
);


CREATE INDEX IF NOT EXISTS
idx_property_service_categories_property
ON property_service_categories(
    condominio_id,
    activo,
    orden,
    nombre
);


ALTER TABLE property_service_catalog
ADD COLUMN IF NOT EXISTS categoria_id BIGINT
    REFERENCES property_service_categories(id);


CREATE INDEX IF NOT EXISTS
idx_property_service_catalog_category
ON property_service_catalog(
    categoria_id
)
WHERE categoria_id IS NOT NULL;


-- ============================================================
-- Category and service must belong to the same property.
-- ============================================================

CREATE OR REPLACE FUNCTION
validate_property_service_category()
RETURNS TRIGGER AS $$
DECLARE
    category_property_id BIGINT;
BEGIN
    IF NEW.categoria_id IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT condominio_id
    INTO category_property_id
    FROM property_service_categories
    WHERE id=NEW.categoria_id;

    IF category_property_id IS NULL THEN
        RAISE EXCEPTION
            'PROPERTY_SERVICE_CATEGORY_NOT_FOUND';
    END IF;

    IF category_property_id
       IS DISTINCT FROM
       NEW.condominio_id THEN
        RAISE EXCEPTION
            'PROPERTY_SERVICE_CATEGORY_PROPERTY_MISMATCH';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS
trg_validate_property_service_category
ON property_service_catalog;


CREATE TRIGGER
trg_validate_property_service_category
BEFORE INSERT OR UPDATE OF
    condominio_id,
    categoria_id
ON property_service_catalog
FOR EACH ROW
EXECUTE FUNCTION
validate_property_service_category();


-- ============================================================
-- Explicit non-goals
-- ============================================================
-- This migration intentionally does not:
--   - seed categories;
--   - seed services;
--   - apply continuity restrictions;
--   - alter financial obligations;
--   - alter payments;
--   - alter fees;
--   - encode specific service families in SQL.
