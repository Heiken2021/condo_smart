-- Condo-Smart Build 02 / B02.1.6
-- Fechas de construccion y ocupacion.
ALTER TABLE condominios ADD COLUMN IF NOT EXISTS fecha_construccion DATE;
ALTER TABLE condominios ADD COLUMN IF NOT EXISTS condicion_codigo VARCHAR(80);
ALTER TABLE espacios ADD COLUMN IF NOT EXISTS fecha_construccion DATE;
