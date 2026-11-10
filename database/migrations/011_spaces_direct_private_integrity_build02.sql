-- Build 02 / B02.2.03
-- Un espacio puede ser directo (estructura_id NULL).
-- Si pertenece a una estructura, esta debe ser una privada activa del mismo fraccionamiento.
CREATE OR REPLACE FUNCTION validar_estructura_espacio_build02()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE inmueble_tipo VARCHAR(80); nodo RECORD;
BEGIN
 IF NEW.estructura_id IS NULL THEN RETURN NEW; END IF;
 SELECT tipo_codigo INTO inmueble_tipo FROM condominios WHERE id=NEW.condominio_id;
 IF inmueble_tipo <> 'FRACCIONAMIENTO' THEN
   RAISE EXCEPTION 'Solo un fraccionamiento puede asignar espacios a privadas';
 END IF;
 SELECT condominio_id,tipo_codigo,activo INTO nodo
 FROM estructura_inmueble WHERE id=NEW.estructura_id;
 IF NOT FOUND OR nodo.condominio_id<>NEW.condominio_id
    OR nodo.tipo_codigo<>'PRIVADA' OR NOT nodo.activo THEN
   RAISE EXCEPTION 'La privada no es valida o no pertenece al inmueble';
 END IF;
 RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS trg_validar_estructura_espacio_build02 ON espacios;
CREATE TRIGGER trg_validar_estructura_espacio_build02
BEFORE INSERT OR UPDATE OF condominio_id,estructura_id ON espacios
FOR EACH ROW EXECUTE FUNCTION validar_estructura_espacio_build02();
