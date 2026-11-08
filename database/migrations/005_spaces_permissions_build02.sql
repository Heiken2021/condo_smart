-- Condo-Smart Build 02 / B02.1
-- Permisos especificos para gestion de Espacios.

INSERT INTO permisos(codigo,nombre,modulo,accion) VALUES
('ESPACIO_CONSULTAR','Consultar Espacios','ESPACIOS','READ'),
('ESPACIO_CREAR','Crear Espacio','ESPACIOS','CREATE'),
('ESPACIO_MODIFICAR','Modificar Espacio','ESPACIOS','UPDATE'),
('ESPACIO_DESACTIVAR','Desactivar Espacio','ESPACIOS','UPDATE'),
('ESPACIO_REACTIVAR','Reactivar Espacio','ESPACIOS','UPDATE'),
('ESPACIO_ELIMINAR','Eliminar Espacio','ESPACIOS','DELETE')
ON CONFLICT DO NOTHING;

INSERT INTO rol_permisos(rol_codigo,permiso_codigo,permitido)
SELECT 'ADMINISTRADOR', codigo, TRUE
FROM permisos
WHERE codigo IN (
    'ESPACIO_CONSULTAR',
    'ESPACIO_CREAR',
    'ESPACIO_MODIFICAR',
    'ESPACIO_DESACTIVAR',
    'ESPACIO_REACTIVAR',
    'ESPACIO_ELIMINAR'
)
ON CONFLICT DO NOTHING;
