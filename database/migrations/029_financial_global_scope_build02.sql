BEGIN;

-- CONDO_SMART BUILD 02 - GLOBAL FINANCIAL RULE SCOPE
-- Adds an explicit reusable global base layer.
-- This migration does not create rules, versions, fees or obligations.
-- Existing property configurations remain unchanged.
-- Dynamic definitions and applicability are managed as governed data.
-- No property name, property type or rule code is hardcoded here.

ALTER TABLE financial_rules DROP CONSTRAINT IF EXISTS financial_rules_scope_level_check;
ALTER TABLE financial_rules ADD CONSTRAINT financial_rules_scope_level_check CHECK (scope_level IN ('GLOBAL','CORE','TIPOLOGIA','INMUEBLE','ESTRUCTURA','ESPACIO'));

ALTER TABLE financial_rules DROP CONSTRAINT IF EXISTS financial_rules_check;
ALTER TABLE financial_rules ADD CONSTRAINT financial_rules_check CHECK (
 ((scope_level IN ('GLOBAL','CORE','TIPOLOGIA')) AND condominio_id IS NULL AND estructura_id IS NULL AND espacio_id IS NULL) OR
 (scope_level='INMUEBLE' AND condominio_id IS NOT NULL AND estructura_id IS NULL AND espacio_id IS NULL) OR
 (scope_level='ESTRUCTURA' AND condominio_id IS NOT NULL AND estructura_id IS NOT NULL AND espacio_id IS NULL) OR
 (scope_level='ESPACIO' AND condominio_id IS NOT NULL AND espacio_id IS NOT NULL)
);

COMMIT;
