ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS telefono_of_casa VARCHAR(50);
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS telefono_celular VARCHAR(50);
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS direccion TEXT;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS origen_codigo VARCHAR(50);

INSERT INTO catalogos(codigo,nombre,activo)
VALUES('ORIGEN_ADMIN','Origen De Administrador',TRUE)
ON CONFLICT(codigo) DO UPDATE SET nombre=EXCLUDED.nombre,activo=TRUE;

INSERT INTO catalogo_valores(catalogo_id,codigo,nombre,activo)
SELECT c.id,v.codigo,v.nombre,TRUE
FROM catalogos c
CROSS JOIN (VALUES
 ('EMPRESA','Empresa'),
 ('INQUILINO','Inquilino'),
 ('PRIVADO','Privado')
) AS v(codigo,nombre)
WHERE c.codigo='ORIGEN_ADMIN'
ON CONFLICT(catalogo_id,codigo) DO UPDATE SET nombre=EXCLUDED.nombre,activo=TRUE;
