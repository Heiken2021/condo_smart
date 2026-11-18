from pathlib import Path

MIGRATION = Path("database/migrations/031_global_generic_starter_catalog_build02.sql").read_text(encoding="utf-8")

NEW_CODES = ['FONDO_RESERVA', 'CUOTA_EXTRAORDINARIA', 'APLICACION_PAGOS', 'DECLARACION_MOROSIDAD', 'RECORDATORIO_PAGO', 'COBRANZA_ESCALONADA', 'CONVENIO_PAGO', 'MEDIACION_INTERNA', 'EXPEDIENTE_COBRANZA', 'ESTADO_CUENTA_PERIODICO', 'EMISION_RECIBOS', 'CONSTANCIA_NO_ADEUDO', 'DERECHOS_ASAMBLEA', 'PROTECCION_DATOS_MOROSIDAD', 'RENTA_PERIODICA', 'INCUMPLIMIENTO_RENTA']
EXISTING_CORE = [
    "MANTENIMIENTO_ORDINARIO",
    "PAGO_MINIMO_PARCIAL",
    "RECARGO_MOROSIDAD",
    "CONTINUIDAD_SERVICIOS",
]


def test_030b_adds_exactly_sixteen_missing_definitions():
    assert len(NEW_CODES) == 16
    for code in NEW_CODES:
        assert f"'{code}'" in MIGRATION


def test_030b_reuses_existing_core_definitions():
    for code in EXISTING_CORE:
        assert f"WHERE NOT EXISTS" in MIGRATION
        assert f"INSERT INTO financial_rule_definitions" in MIGRATION
    assert "FEM-2026-RN001" not in NEW_CODES


def test_030b_uses_dynamic_parameter_schemas():
    assert MIGRATION.count("esquema_parametros") == 16
    assert MIGRATION.count("::jsonb") == 16
    for parameter_type in ('\"number\"','\"integer\"','\"string\"','\"boolean\"'):
        assert parameter_type in MIGRATION


def test_030b_has_no_jurisdiction_specific_values():
    forbidden = ("CDMX", "EDOMEX", "ESTADO DE MEXICO", "9 %", "0.75 %")
    upper = MIGRATION.upper()
    for token in forbidden:
        assert token not in upper


def test_030b_does_not_create_lifecycle_records():
    forbidden = (
        "INSERT INTO financial_rules",
        "INSERT INTO financial_rule_versions",
        "INSERT INTO financial_obligations",
        "UPDATE space_fee_history",
        "INSERT INTO financial_rule_jurisdiction_profiles",
        "INSERT INTO financial_rule_definition_profiles",
    )
    for token in forbidden:
        assert token not in MIGRATION
