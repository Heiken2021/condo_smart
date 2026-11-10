-- Condo_Smart Build 02 / B02.2.07
-- Eliminacion definitiva y controlada de administradores sin asignaciones activas.

INSERT INTO permisos(codigo,nombre,modulo,accion) VALUES
('ADMINISTRADOR_ELIMINAR','Eliminar Administrador Definitivamente','USUARIOS','DELETE')
ON CONFLICT DO NOTHING;

INSERT INTO rol_permisos(rol_codigo,permiso_codigo)
SELECT r.codigo,p.codigo FROM roles r CROSS JOIN permisos p
WHERE r.codigo='SUPERADMIN' AND p.codigo='ADMINISTRADOR_ELIMINAR'
ON CONFLICT DO NOTHING;
