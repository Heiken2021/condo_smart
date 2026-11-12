BEGIN;

ALTER TABLE auditoria
    ADD COLUMN IF NOT EXISTS modulo VARCHAR(80),
    ADD COLUMN IF NOT EXISTS trace_id VARCHAR(100);

CREATE INDEX IF NOT EXISTS idx_auditoria_usuario_fecha
    ON auditoria(usuario_id, fecha DESC);

CREATE INDEX IF NOT EXISTS idx_auditoria_accion_fecha
    ON auditoria(accion, fecha DESC);

CREATE TABLE IF NOT EXISTS auditoria_financiera(
    id BIGSERIAL PRIMARY KEY,
    fecha TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    condominio_id BIGINT REFERENCES condominios(id),
    usuario_id BIGINT REFERENCES usuarios(id),
    username VARCHAR(100),

    tipo_operacion VARCHAR(80) NOT NULL,
    entidad VARCHAR(40) NOT NULL,
    entidad_id BIGINT,

    espacio_id BIGINT REFERENCES espacios(id),
    persona_id BIGINT REFERENCES personas(id),

    monto_mxn NUMERIC(14,2),
    moneda VARCHAR(3) NOT NULL DEFAULT 'MXN',

    estado_anterior VARCHAR(80),
    estado_nuevo VARCHAR(80),

    referencia VARCHAR(200),
    evento_relacionado_id BIGINT
        REFERENCES auditoria_financiera(id),

    detalle TEXT,
    metadata JSONB,

    trace_id VARCHAR(100),

    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_auditoria_financiera_condominio_fecha
    ON auditoria_financiera(condominio_id, fecha DESC);

CREATE INDEX IF NOT EXISTS idx_auditoria_financiera_entidad
    ON auditoria_financiera(entidad, entidad_id);

CREATE INDEX IF NOT EXISTS idx_auditoria_financiera_espacio_fecha
    ON auditoria_financiera(espacio_id, fecha DESC);

INSERT INTO permisos(
    codigo,
    nombre,
    modulo,
    accion
)
VALUES
(
    'AUDITORIA_INMUEBLE',
    'Consultar Auditoría Del Inmueble',
    'AUDITORIA',
    'READ'
),
(
    'AUDITORIA_FINANCIERA',
    'Consultar Auditoría Financiera',
    'AUDITORIA',
    'READ'
)
ON CONFLICT DO NOTHING;

INSERT INTO rol_permisos(
    rol_codigo,
    permiso_codigo,
    permitido
)
SELECT
    r.codigo,
    p.codigo,
    TRUE
FROM roles r
JOIN permisos p
  ON p.codigo IN (
      'AUDITORIA_INMUEBLE',
      'AUDITORIA_FINANCIERA'
  )
WHERE r.codigo IN (
    'SUPERADMIN',
    'ADMINISTRADOR',
    'GERENTE',
    'CONTABILIDAD'
)
ON CONFLICT DO NOTHING;

CREATE OR REPLACE FUNCTION prevent_auditoria_financiera_mutation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION
        'AUDITORIA_FINANCIERA_IS_APPEND_ONLY';
END;
$$;

DROP TRIGGER IF EXISTS
    trg_auditoria_financiera_no_update_delete
ON auditoria_financiera;

CREATE TRIGGER
    trg_auditoria_financiera_no_update_delete
BEFORE UPDATE OR DELETE
ON auditoria_financiera
FOR EACH ROW
EXECUTE FUNCTION prevent_auditoria_financiera_mutation();

COMMIT;
