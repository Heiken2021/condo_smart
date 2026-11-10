-- Build 02 / PERF-01: observabilidad historica
CREATE TABLE IF NOT EXISTS performance_events(
 id BIGSERIAL PRIMARY KEY,
 recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 build_version VARCHAR(120) NOT NULL,
 session_key VARCHAR(80),
 module VARCHAR(80) NOT NULL,
 operation VARCHAR(160) NOT NULL,
 duration_ms NUMERIC(14,3) NOT NULL CHECK(duration_ms>=0),
 sql_duration_ms NUMERIC(14,3) NOT NULL DEFAULT 0 CHECK(sql_duration_ms>=0),
 query_count INTEGER NOT NULL DEFAULT 0 CHECK(query_count>=0),
 slowest_query_ms NUMERIC(14,3) NOT NULL DEFAULT 0 CHECK(slowest_query_ms>=0),
 status VARCHAR(20) NOT NULL DEFAULT 'OK' CHECK(status IN ('OK','ERROR')),
 condominio_id BIGINT REFERENCES condominios(id) ON DELETE SET NULL,
 metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_performance_events_recorded ON performance_events(recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_performance_events_module_operation ON performance_events(module,operation,recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_performance_events_build ON performance_events(build_version,recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_performance_events_status ON performance_events(status,recorded_at DESC);
