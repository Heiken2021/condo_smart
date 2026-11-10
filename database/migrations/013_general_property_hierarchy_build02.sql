-- Condo_Smart Build 02 / B02.2.04
-- Evolucion segura de la jerarquia estructural sin modificar migraciones aplicadas.
-- Modelo: Inmueble -> estructura anidada -> espacios; los espacios directos conservan estructura_id NULL.

ALTER TABLE estructura_inmueble
    DROP CONSTRAINT IF EXISTS ck_estructura_tipo_privada,
    DROP CONSTRAINT IF EXISTS ck_estructura_privada_raiz;

ALTER TABLE estructura_inmueble
    ADD CONSTRAINT ck_estructura_tipo_build02
    CHECK (tipo_codigo IN ('CONJUNTO_URBANO','FRACCIONAMIENTO','PRIVADA','EDIFICIO','TORRE','SECCION','ZONA'));

CREATE OR REPLACE FUNCTION validar_nodo_estructura_build02()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE padre RECORD;
BEGIN
    IF NEW.parent_id = NEW.id THEN
        RAISE EXCEPTION 'Un nodo estructural no puede ser su propio padre';
    END IF;

    IF NEW.parent_id IS NOT NULL THEN
        SELECT id,condominio_id,tipo_codigo,activo INTO padre
        FROM estructura_inmueble WHERE id=NEW.parent_id;
        IF NOT FOUND OR padre.condominio_id <> NEW.condominio_id THEN
            RAISE EXCEPTION 'El nodo padre no pertenece al mismo inmueble';
        END IF;
        IF NOT padre.activo THEN
            RAISE EXCEPTION 'El nodo padre esta inactivo';
        END IF;
    END IF;

    IF NEW.tipo_codigo='PRIVADA' AND NEW.parent_id IS NOT NULL
       AND padre.tipo_codigo NOT IN ('CONJUNTO_URBANO','FRACCIONAMIENTO','ZONA','SECCION') THEN
        RAISE EXCEPTION 'Una privada requiere un padre estructural compatible';
    END IF;

    RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_validar_nodo_estructura_build02 ON estructura_inmueble;
CREATE TRIGGER trg_validar_nodo_estructura_build02
BEFORE INSERT OR UPDATE OF condominio_id,parent_id,tipo_codigo,activo
ON estructura_inmueble
FOR EACH ROW EXECUTE FUNCTION validar_nodo_estructura_build02();

CREATE OR REPLACE FUNCTION validar_estructura_espacio_build02()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE nodo RECORD;
BEGIN
    IF NEW.estructura_id IS NULL THEN RETURN NEW; END IF;

    SELECT condominio_id,tipo_codigo,activo INTO nodo
    FROM estructura_inmueble WHERE id=NEW.estructura_id;

    IF NOT FOUND OR nodo.condominio_id <> NEW.condominio_id OR NOT nodo.activo THEN
        RAISE EXCEPTION 'La ubicacion estructural no es valida o no pertenece al inmueble';
    END IF;

    RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_validar_estructura_espacio_build02 ON espacios;
CREATE TRIGGER trg_validar_estructura_espacio_build02
BEFORE INSERT OR UPDATE OF condominio_id,estructura_id ON espacios
FOR EACH ROW EXECUTE FUNCTION validar_estructura_espacio_build02();

DROP INDEX IF EXISTS uq_estructura_condominio_clave;
CREATE UNIQUE INDEX IF NOT EXISTS uq_estructura_condominio_parent_clave_v2
ON estructura_inmueble(condominio_id,COALESCE(parent_id,0),clave)
WHERE clave IS NOT NULL AND clave<>'';

CREATE INDEX IF NOT EXISTS idx_estructura_parent_activo
ON estructura_inmueble(condominio_id,parent_id,activo);
