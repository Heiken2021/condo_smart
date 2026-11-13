-- Build 02 - Gobierno de seguridad Root.
-- Conserva SUPERADMIN como rol global y agrega autoridad PRINCIPAL/DELEGADO.

ALTER TABLE usuarios
    ADD COLUMN IF NOT EXISTS autoridad_root VARCHAR(20),
    ADD COLUMN IF NOT EXISTS root_asignado_por BIGINT REFERENCES usuarios(id),
    ADD COLUMN IF NOT EXISTS root_asignado_en TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS root_revocado_por BIGINT REFERENCES usuarios(id),
    ADD COLUMN IF NOT EXISTS root_revocado_en TIMESTAMPTZ;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'usuarios_autoridad_root_check'
    ) THEN
        ALTER TABLE usuarios
            ADD CONSTRAINT usuarios_autoridad_root_check
            CHECK (
                autoridad_root IS NULL
                OR autoridad_root IN ('PRINCIPAL', 'DELEGADO')
            );
    END IF;
END $$;

-- La cuenta admin será preferida como Root Principal.
-- Si no existe, se toma el SuperAdmin activo más antiguo.
WITH principal AS (
    SELECT id
    FROM usuarios
    WHERE rol_global = 'SUPERADMIN'
      AND activo = TRUE
    ORDER BY
        CASE WHEN username = 'admin' THEN 0 ELSE 1 END,
        creado_en,
        id
    LIMIT 1
)
UPDATE usuarios
SET autoridad_root = 'PRINCIPAL',
    root_asignado_en = COALESCE(root_asignado_en, NOW()),
    root_revocado_por = NULL,
    root_revocado_en = NULL
WHERE id = (SELECT id FROM principal)
  AND autoridad_root IS DISTINCT FROM 'PRINCIPAL';

-- Los SuperAdmin activos restantes quedan identificados como delegados.
UPDATE usuarios
SET autoridad_root = 'DELEGADO',
    root_asignado_en = COALESCE(root_asignado_en, NOW()),
    root_revocado_por = NULL,
    root_revocado_en = NULL
WHERE rol_global = 'SUPERADMIN'
  AND activo = TRUE
  AND autoridad_root IS NULL;

-- Los usuarios normales no pueden conservar autoridad Root activa.
UPDATE usuarios
SET autoridad_root = NULL
WHERE rol_global <> 'SUPERADMIN'
  AND autoridad_root IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS ux_usuarios_root_principal_activo
ON usuarios (autoridad_root)
WHERE autoridad_root = 'PRINCIPAL'
  AND rol_global = 'SUPERADMIN'
  AND activo = TRUE;

CREATE OR REPLACE FUNCTION proteger_gobierno_root()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.autoridad_root = 'PRINCIPAL'
       AND OLD.rol_global = 'SUPERADMIN'
       AND OLD.activo = TRUE
       AND (
           NEW.autoridad_root IS DISTINCT FROM 'PRINCIPAL'
           OR NEW.rol_global IS DISTINCT FROM 'SUPERADMIN'
           OR NEW.activo IS DISTINCT FROM TRUE
       )
    THEN
        RAISE EXCEPTION
            'ROOT_PRINCIPAL_PROTECTED: no es posible degradar o desactivar al Root Principal';
    END IF;

    IF NEW.autoridad_root IS NOT NULL
       AND (
           NEW.rol_global <> 'SUPERADMIN'
           OR NEW.activo <> TRUE
       )
    THEN
        RAISE EXCEPTION
            'ROOT_AUTHORITY_INVALID: la autoridad Root requiere un SuperAdmin activo';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_proteger_gobierno_root ON usuarios;

CREATE TRIGGER trg_proteger_gobierno_root
BEFORE UPDATE ON usuarios
FOR EACH ROW
EXECUTE FUNCTION proteger_gobierno_root();
