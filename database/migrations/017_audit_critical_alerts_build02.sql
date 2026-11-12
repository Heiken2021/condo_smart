BEGIN;

CREATE TABLE IF NOT EXISTS auditoria_alertas(
    id BIGSERIAL PRIMARY KEY,

    auditoria_id BIGINT NOT NULL UNIQUE
        REFERENCES auditoria(id)
        ON DELETE CASCADE,

    tipo VARCHAR(30)
        NOT NULL
        DEFAULT 'CRITICO',

    destinatario VARCHAR(254) NOT NULL,

    estado VARCHAR(20)
        NOT NULL
        DEFAULT 'PENDING',

    intentos INTEGER
        NOT NULL
        DEFAULT 0,

    ultimo_error TEXT,

    creado_en TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW(),

    enviado_en TIMESTAMPTZ,

    CHECK(
        estado IN(
            'PENDING',
            'SENT',
            'ERROR'
        )
    )
);

CREATE INDEX IF NOT EXISTS
    idx_auditoria_alertas_estado
ON auditoria_alertas(
    estado,
    creado_en DESC
);

COMMIT;
