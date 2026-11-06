CREATE OR REPLACE FUNCTION proteger_ultimo_superadmin() RETURNS TRIGGER AS $$
DECLARE activos INTEGER;
BEGIN
 IF OLD.rol_global='SUPERADMIN' AND OLD.activo=TRUE AND (NEW.activo=FALSE OR NEW.rol_global<>'SUPERADMIN') THEN
  SELECT COUNT(*) INTO activos FROM usuarios WHERE rol_global='SUPERADMIN' AND activo=TRUE AND id<>OLD.id;
  IF activos=0 THEN RAISE EXCEPTION 'No es posible desactivar o degradar el ultimo SuperAdmin'; END IF;
 END IF;
 RETURN NEW;
END; $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_proteger_ultimo_superadmin ON usuarios;
CREATE TRIGGER trg_proteger_ultimo_superadmin BEFORE UPDATE ON usuarios FOR EACH ROW EXECUTE FUNCTION proteger_ultimo_superadmin();
