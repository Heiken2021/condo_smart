-- Condo-Smart Build 02 / B02.2
-- Jerarquia: Inmueble -> Conjunto/Fraccionamiento -> Privada -> Espacio.

INSERT INTO catalogo_valores(catalogo_id,codigo,nombre)
SELECT c.id,v.codigo,v.nombre FROM catalogos c
JOIN (VALUES
 ('TIPO_INMUEBLE','CONJUNTO_URBANO','Conjunto Urbano'),
 ('TIPO_INMUEBLE','FRACCIONAMIENTO','Fraccionamiento')
)v(cat,codigo,nombre) ON c.codigo=v.cat
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS estructura_inmueble(
 id BIGSERIAL PRIMARY KEY,
 condominio_id BIGINT NOT NULL REFERENCES condominios(id) ON DELETE CASCADE,
 parent_id BIGINT REFERENCES estructura_inmueble(id) ON DELETE RESTRICT,
 tipo_codigo VARCHAR(40) NOT NULL,
 clave VARCHAR(40),
 nombre VARCHAR(120) NOT NULL,
 descripcion TEXT,
 activo BOOLEAN DEFAULT TRUE,
 creado_en TIMESTAMPTZ DEFAULT NOW(),
 actualizado_en TIMESTAMPTZ DEFAULT NOW(),
 CHECK(tipo_codigo IN ('CONJUNTO_URBANO','FRACCIONAMIENTO','PRIVADA'))
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_estructura_condominio_parent_clave
 ON estructura_inmueble(condominio_id,COALESCE(parent_id,0),clave)
 WHERE clave IS NOT NULL AND clave <> '';
CREATE INDEX IF NOT EXISTS idx_estructura_condominio ON estructura_inmueble(condominio_id,activo);
ALTER TABLE espacios ADD COLUMN IF NOT EXISTS estructura_id BIGINT REFERENCES estructura_inmueble(id);
CREATE INDEX IF NOT EXISTS idx_espacios_estructura ON espacios(estructura_id);
