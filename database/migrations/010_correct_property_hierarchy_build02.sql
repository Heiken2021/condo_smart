-- Build 02 / B02.2 corrective migration
-- 009 ya fue aplicada; esta migracion corrige el modelo sin reescribir su historial.

INSERT INTO catalogo_valores(catalogo_id,codigo,nombre)
SELECT c.id,v.codigo,v.nombre FROM catalogos c JOIN (VALUES
 ('TIPO_INMUEBLE','EDIFICIO','Edificio'),
 ('TIPO_INMUEBLE','CONDOMINIO','Condominio'),
 ('TIPO_INMUEBLE','FRACCIONAMIENTO','Fraccionamiento')
)v(cat,codigo,nombre) ON c.codigo=v.cat ON CONFLICT DO NOTHING;

-- El diagnostico previo confirmó cero nodos y cero espacios asignados.
-- Aun asi, se aborta si aparecieron datos entre la inspeccion y la migracion.
DO $$
BEGIN
 IF EXISTS (SELECT 1 FROM estructura_inmueble) THEN
   RAISE EXCEPTION '010 requiere estructura_inmueble vacia para corregir el modelo de forma segura';
 END IF;
 IF EXISTS (SELECT 1 FROM espacios WHERE estructura_id IS NOT NULL) THEN
   RAISE EXCEPTION '010 requiere espacios sin asignaciones estructurales';
 END IF;
END $$;

DO $$
DECLARE r record;
BEGIN
 FOR r IN
   SELECT conname FROM pg_constraint
   WHERE conrelid='estructura_inmueble'::regclass AND contype='c'
 LOOP
   EXECUTE format('ALTER TABLE estructura_inmueble DROP CONSTRAINT %I',r.conname);
 END LOOP;
END $$;

ALTER TABLE estructura_inmueble
 ADD CONSTRAINT ck_estructura_tipo_privada CHECK(tipo_codigo='PRIVADA'),
 ADD CONSTRAINT ck_estructura_privada_raiz CHECK(parent_id IS NULL);

DROP INDEX IF EXISTS uq_estructura_condominio_parent_clave;
CREATE UNIQUE INDEX IF NOT EXISTS uq_estructura_condominio_clave
 ON estructura_inmueble(condominio_id,clave)
 WHERE clave IS NOT NULL AND clave<>'';
