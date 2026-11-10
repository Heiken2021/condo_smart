-- Condo_Smart Build 02 / B02.2.06
-- Recuperacion segura de contrasena y permisos de estructura.

CREATE TABLE IF NOT EXISTS password_reset_tokens(
 id BIGSERIAL PRIMARY KEY,
 usuario_id BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
 token_hash VARCHAR(64) NOT NULL UNIQUE,
 creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 expira_en TIMESTAMPTZ NOT NULL,
 usado_en TIMESTAMPTZ,
 solicitado_ip VARCHAR(80)
);
CREATE INDEX IF NOT EXISTS idx_password_reset_usuario
ON password_reset_tokens(usuario_id,expira_en DESC);

INSERT INTO permisos(codigo,nombre,modulo,accion) VALUES
('ESTRUCTURA_CREAR','Crear Estructura','INMUEBLES','CREATE'),
('ESTRUCTURA_MODIFICAR','Modificar Estructura','INMUEBLES','UPDATE'),
('ESTRUCTURA_DESACTIVAR','Desactivar Estructura','INMUEBLES','UPDATE'),
('ESTRUCTURA_REACTIVAR','Reactivar Estructura','INMUEBLES','UPDATE'),
('ESTRUCTURA_ELIMINAR','Eliminar Estructura','INMUEBLES','DELETE')
ON CONFLICT DO NOTHING;

INSERT INTO rol_permisos(rol_codigo,permiso_codigo)
SELECT r.codigo,p.codigo FROM roles r CROSS JOIN permisos p
WHERE r.codigo IN ('SUPERADMIN','ADMINISTRADOR')
AND p.codigo IN ('ESTRUCTURA_CREAR','ESTRUCTURA_MODIFICAR','ESTRUCTURA_DESACTIVAR','ESTRUCTURA_REACTIVAR','ESTRUCTURA_ELIMINAR')
ON CONFLICT DO NOTHING;
