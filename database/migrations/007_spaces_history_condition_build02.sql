-- Condo-Smart Build 02 / B02.1.5
-- Edificio/Zona, antiguedad, condicion fisica e historial cronologico.

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='espacios' AND column_name='ubicacion'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='espacios' AND column_name='edificio_zona'
    ) THEN
        ALTER TABLE espacios RENAME COLUMN ubicacion TO edificio_zona;
    END IF;
END $$;

ALTER TABLE espacios ADD COLUMN IF NOT EXISTS edificio_zona VARCHAR(160);
ALTER TABLE espacios ADD COLUMN IF NOT EXISTS anio_construccion SMALLINT;
ALTER TABLE espacios ADD COLUMN IF NOT EXISTS condicion_codigo VARCHAR(80);

INSERT INTO catalogos(codigo,nombre)
VALUES('CONDICION_FISICA','Condicion Fisica')
ON CONFLICT DO NOTHING;

INSERT INTO catalogo_valores(catalogo_id,codigo,nombre)
SELECT c.id,v.codigo,v.nombre
FROM catalogos c
JOIN (VALUES
 ('CONDICION_FISICA','NUEVO','Nuevo'),
 ('CONDICION_FISICA','ANTIGUO','Antiguo'),
 ('CONDICION_FISICA','RESTAURADO','Restaurado'),
 ('CONDICION_FISICA','VIEJO','Viejo'),
 ('CONDICION_FISICA','DEMOLER','Construccion a Demoler'),
 ('CONDICION_FISICA','SOLO_TERRENO','Solo Terreno')
)v(cat,codigo,nombre) ON c.codigo=v.cat
ON CONFLICT DO NOTHING;
