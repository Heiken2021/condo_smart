CREATE TABLE IF NOT EXISTS configuracion_sistema(
    id BIGSERIAL PRIMARY KEY,
    clave VARCHAR(120) NOT NULL UNIQUE,
    valor TEXT,
    tipo VARCHAR(30) NOT NULL DEFAULT 'TEXTO',
    descripcion TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    actualizado_por BIGINT REFERENCES usuarios(id),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS identidad_sistema(
    id SMALLINT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    logo_data BYTEA,
    logo_mime VARCHAR(120),
    actualizado_por BIGINT REFERENCES usuarios(id),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO identidad_sistema(id) VALUES(1) ON CONFLICT (id) DO NOTHING;
