-- Condo-Smart Build 02 / B02.1.4
-- Ampliacion descriptiva y responsable del Espacio.

ALTER TABLE espacios ADD COLUMN IF NOT EXISTS clave VARCHAR(40);
ALTER TABLE espacios ADD COLUMN IF NOT EXISTS superficie_m2 NUMERIC(12,2) DEFAULT 0;
ALTER TABLE espacios ADD COLUMN IF NOT EXISTS ubicacion VARCHAR(160);
ALTER TABLE espacios ADD COLUMN IF NOT EXISTS nivel VARCHAR(60);
ALTER TABLE espacios ADD COLUMN IF NOT EXISTS uso_codigo VARCHAR(80);
ALTER TABLE espacios ADD COLUMN IF NOT EXISTS descripcion TEXT;
ALTER TABLE espacios ADD COLUMN IF NOT EXISTS responsable_persona_id BIGINT REFERENCES personas(id);
ALTER TABLE espacios ADD COLUMN IF NOT EXISTS responsable_relacion VARCHAR(30);

CREATE UNIQUE INDEX IF NOT EXISTS uq_espacios_condominio_clave
ON espacios(condominio_id, clave)
WHERE clave IS NOT NULL AND clave <> '';

INSERT INTO catalogos(codigo,nombre)
VALUES('USO_ESPACIO','Uso De Espacio')
ON CONFLICT DO NOTHING;

INSERT INTO catalogo_valores(catalogo_id,codigo,nombre)
SELECT c.id,v.codigo,v.nombre
FROM catalogos c
JOIN (VALUES
 ('USO_ESPACIO','HABITACIONAL','Habitacional'),
 ('USO_ESPACIO','COMERCIAL','Comercial'),
 ('USO_ESPACIO','OFICINA','Oficina'),
 ('USO_ESPACIO','BODEGA','Bodega'),
 ('USO_ESPACIO','AREA_COMUN','Area Comun'),
 ('USO_ESPACIO','ESTACIONAMIENTO','Estacionamiento')
)v(cat,codigo,nombre) ON c.codigo=v.cat
ON CONFLICT DO NOTHING;
