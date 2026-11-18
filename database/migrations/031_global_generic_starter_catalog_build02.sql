BEGIN;

-- CONDO_SMART BUILD 030B - GLOBAL GENERIC STARTER CATALOG
-- Adds the 16 missing definitions needed to complete a 20-template starter catalog.
-- Reuses the four existing Core definitions.
-- Does not create financial_rules, versions, assignments, approvals or obligations.


INSERT INTO financial_rule_definitions(
    codigo,nombre,descripcion,dominio_codigo,nivel_base_codigo,
    tipo_resultado,esquema_parametros,obligatoria,
    admite_especializacion,admite_herencia,admite_override,
    admite_excepcion,requiere_aprobacion,permite_nivel_inmueble,
    permite_nivel_estructura,permite_nivel_espacio,
    contexto_kpi,contexto_ia,activo
)
SELECT
    'FONDO_RESERVA','Fondo de reserva','Plantilla global genérica para fondo de reserva. Sus valores concretos se definen mediante configuración gobernada y perfiles jurisdiccionales cuando correspondan.','FINANZAS','CORE',
    'POLITICA','{"contribution_method":{"type":"string","allowed":["IMPORTE","PORCENTAJE"]},"contribution_value":{"type":"number","minimum":0},"frequency":{"type":"string","allowed":["MENSUAL","BIMESTRAL","TRIMESTRAL","SEMESTRAL","ANUAL","UNICA"]},"minimum_target":{"type":"number","minimum":0,"optional":true},"requires_authorization":{"type":"boolean"}}'::jsonb,FALSE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,
    TRUE,TRUE,TRUE
WHERE NOT EXISTS(
    SELECT 1 FROM financial_rule_definitions WHERE codigo='FONDO_RESERVA'
);


INSERT INTO financial_rule_definitions(
    codigo,nombre,descripcion,dominio_codigo,nivel_base_codigo,
    tipo_resultado,esquema_parametros,obligatoria,
    admite_especializacion,admite_herencia,admite_override,
    admite_excepcion,requiere_aprobacion,permite_nivel_inmueble,
    permite_nivel_estructura,permite_nivel_espacio,
    contexto_kpi,contexto_ia,activo
)
SELECT
    'CUOTA_EXTRAORDINARIA','Cuota extraordinaria','Plantilla global genérica para cuota extraordinaria. Sus valores concretos se definen mediante configuración gobernada y perfiles jurisdiccionales cuando correspondan.','OBLIGACIONES','CORE',
    'OBLIGACION','{"amount":{"type":"number","minimum":0},"installments":{"type":"integer","minimum":1},"due_day":{"type":"integer","minimum":1,"maximum":31},"distribution_method":{"type":"string","allowed":["IGUALITARIA","INDIVISO","IMPORTE_ESPECIFICO"]},"assembly_reference":{"type":"string"}}'::jsonb,FALSE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,
    TRUE,TRUE,TRUE
WHERE NOT EXISTS(
    SELECT 1 FROM financial_rule_definitions WHERE codigo='CUOTA_EXTRAORDINARIA'
);


INSERT INTO financial_rule_definitions(
    codigo,nombre,descripcion,dominio_codigo,nivel_base_codigo,
    tipo_resultado,esquema_parametros,obligatoria,
    admite_especializacion,admite_herencia,admite_override,
    admite_excepcion,requiere_aprobacion,permite_nivel_inmueble,
    permite_nivel_estructura,permite_nivel_espacio,
    contexto_kpi,contexto_ia,activo
)
SELECT
    'APLICACION_PAGOS','Aplicación de pagos','Plantilla global genérica para aplicación de pagos. Sus valores concretos se definen mediante configuración gobernada y perfiles jurisdiccionales cuando correspondan.','COBRANZA','CORE',
    'POLITICA','{"allocation_order":{"type":"string","allowed":["ANTIGUEDAD","PRINCIPAL_PRIMERO","INTERESES_PRIMERO","CONFIGURABLE"]},"allow_reallocation":{"type":"boolean"},"requires_authorization":{"type":"boolean"}}'::jsonb,FALSE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,
    TRUE,TRUE,TRUE
WHERE NOT EXISTS(
    SELECT 1 FROM financial_rule_definitions WHERE codigo='APLICACION_PAGOS'
);


INSERT INTO financial_rule_definitions(
    codigo,nombre,descripcion,dominio_codigo,nivel_base_codigo,
    tipo_resultado,esquema_parametros,obligatoria,
    admite_especializacion,admite_herencia,admite_override,
    admite_excepcion,requiere_aprobacion,permite_nivel_inmueble,
    permite_nivel_estructura,permite_nivel_espacio,
    contexto_kpi,contexto_ia,activo
)
SELECT
    'DECLARACION_MOROSIDAD','Declaración de morosidad','Plantilla global genérica para declaración de morosidad. Sus valores concretos se definen mediante configuración gobernada y perfiles jurisdiccionales cuando correspondan.','COBRANZA','CORE',
    'CRITERIO','{"ordinary_overdue_count":{"type":"integer","minimum":1},"extraordinary_overdue_count":{"type":"integer","minimum":1},"requires_account_reconciliation":{"type":"boolean"},"requires_notice":{"type":"boolean"}}'::jsonb,FALSE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,
    TRUE,TRUE,TRUE
WHERE NOT EXISTS(
    SELECT 1 FROM financial_rule_definitions WHERE codigo='DECLARACION_MOROSIDAD'
);


INSERT INTO financial_rule_definitions(
    codigo,nombre,descripcion,dominio_codigo,nivel_base_codigo,
    tipo_resultado,esquema_parametros,obligatoria,
    admite_especializacion,admite_herencia,admite_override,
    admite_excepcion,requiere_aprobacion,permite_nivel_inmueble,
    permite_nivel_estructura,permite_nivel_espacio,
    contexto_kpi,contexto_ia,activo
)
SELECT
    'RECORDATORIO_PAGO','Recordatorio preventivo de pago','Plantilla global genérica para recordatorio preventivo de pago. Sus valores concretos se definen mediante configuración gobernada y perfiles jurisdiccionales cuando correspondan.','COBRANZA','CORE',
    'WORKFLOW','{"days_before_due":{"type":"integer","minimum":0},"days_after_due":{"type":"integer","minimum":0,"optional":true},"channel_policy":{"type":"string","allowed":["EMAIL","SMS","WHATSAPP","MULTICANAL"]},"stop_when_payment_identified":{"type":"boolean"}}'::jsonb,FALSE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,
    TRUE,TRUE,TRUE
WHERE NOT EXISTS(
    SELECT 1 FROM financial_rule_definitions WHERE codigo='RECORDATORIO_PAGO'
);


INSERT INTO financial_rule_definitions(
    codigo,nombre,descripcion,dominio_codigo,nivel_base_codigo,
    tipo_resultado,esquema_parametros,obligatoria,
    admite_especializacion,admite_herencia,admite_override,
    admite_excepcion,requiere_aprobacion,permite_nivel_inmueble,
    permite_nivel_estructura,permite_nivel_espacio,
    contexto_kpi,contexto_ia,activo
)
SELECT
    'COBRANZA_ESCALONADA','Cobranza escalonada','Plantilla global genérica para cobranza escalonada. Sus valores concretos se definen mediante configuración gobernada y perfiles jurisdiccionales cuando correspondan.','COBRANZA','CORE',
    'WORKFLOW','{"stage_interval_days":{"type":"integer","minimum":0},"minimum_overdue_amount":{"type":"number","minimum":0,"optional":true},"minimum_overdue_items":{"type":"integer","minimum":1},"requires_acknowledgement":{"type":"boolean"},"requires_escalation_authorization":{"type":"boolean"}}'::jsonb,FALSE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,
    TRUE,TRUE,TRUE
WHERE NOT EXISTS(
    SELECT 1 FROM financial_rule_definitions WHERE codigo='COBRANZA_ESCALONADA'
);


INSERT INTO financial_rule_definitions(
    codigo,nombre,descripcion,dominio_codigo,nivel_base_codigo,
    tipo_resultado,esquema_parametros,obligatoria,
    admite_especializacion,admite_herencia,admite_override,
    admite_excepcion,requiere_aprobacion,permite_nivel_inmueble,
    permite_nivel_estructura,permite_nivel_espacio,
    contexto_kpi,contexto_ia,activo
)
SELECT
    'CONVENIO_PAGO','Convenio de pago','Plantilla global genérica para convenio de pago. Sus valores concretos se definen mediante configuración gobernada y perfiles jurisdiccionales cuando correspondan.','COBRANZA','CORE',
    'WORKFLOW','{"installments":{"type":"integer","minimum":1},"minimum_initial_payment_percentage":{"type":"number","minimum":0,"maximum":100,"optional":true},"keep_current_charges":{"type":"boolean"},"reactivate_on_default":{"type":"boolean"},"requires_authorization":{"type":"boolean"}}'::jsonb,FALSE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,
    TRUE,TRUE,TRUE
WHERE NOT EXISTS(
    SELECT 1 FROM financial_rule_definitions WHERE codigo='CONVENIO_PAGO'
);


INSERT INTO financial_rule_definitions(
    codigo,nombre,descripcion,dominio_codigo,nivel_base_codigo,
    tipo_resultado,esquema_parametros,obligatoria,
    admite_especializacion,admite_herencia,admite_override,
    admite_excepcion,requiere_aprobacion,permite_nivel_inmueble,
    permite_nivel_estructura,permite_nivel_espacio,
    contexto_kpi,contexto_ia,activo
)
SELECT
    'MEDIACION_INTERNA','Mediación interna','Plantilla global genérica para mediación interna. Sus valores concretos se definen mediante configuración gobernada y perfiles jurisdiccionales cuando correspondan.','GOBIERNO','CORE',
    'WORKFLOW','{"requires_account_statement":{"type":"boolean"},"requires_prior_notices":{"type":"boolean"},"requires_settlement_proposal":{"type":"boolean"},"requires_closure_record":{"type":"boolean"}}'::jsonb,FALSE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,
    TRUE,TRUE,TRUE
WHERE NOT EXISTS(
    SELECT 1 FROM financial_rule_definitions WHERE codigo='MEDIACION_INTERNA'
);


INSERT INTO financial_rule_definitions(
    codigo,nombre,descripcion,dominio_codigo,nivel_base_codigo,
    tipo_resultado,esquema_parametros,obligatoria,
    admite_especializacion,admite_herencia,admite_override,
    admite_excepcion,requiere_aprobacion,permite_nivel_inmueble,
    permite_nivel_estructura,permite_nivel_espacio,
    contexto_kpi,contexto_ia,activo
)
SELECT
    'EXPEDIENTE_COBRANZA','Expediente de cobranza','Plantilla global genérica para expediente de cobranza. Sus valores concretos se definen mediante configuración gobernada y perfiles jurisdiccionales cuando correspondan.','COBRANZA','CORE',
    'WORKFLOW','{"requires_account_statement":{"type":"boolean"},"requires_supporting_documents":{"type":"boolean"},"requires_internal_process_evidence":{"type":"boolean"},"requires_legal_review":{"type":"boolean"}}'::jsonb,FALSE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,
    TRUE,TRUE,TRUE
WHERE NOT EXISTS(
    SELECT 1 FROM financial_rule_definitions WHERE codigo='EXPEDIENTE_COBRANZA'
);


INSERT INTO financial_rule_definitions(
    codigo,nombre,descripcion,dominio_codigo,nivel_base_codigo,
    tipo_resultado,esquema_parametros,obligatoria,
    admite_especializacion,admite_herencia,admite_override,
    admite_excepcion,requiere_aprobacion,permite_nivel_inmueble,
    permite_nivel_estructura,permite_nivel_espacio,
    contexto_kpi,contexto_ia,activo
)
SELECT
    'ESTADO_CUENTA_PERIODICO','Estado de cuenta periódico','Plantilla global genérica para estado de cuenta periódico. Sus valores concretos se definen mediante configuración gobernada y perfiles jurisdiccionales cuando correspondan.','REPORTES','CORE',
    'WORKFLOW','{"frequency":{"type":"string","allowed":["MENSUAL","BIMESTRAL","TRIMESTRAL","SEMESTRAL","ANUAL"]},"include_income_expenses":{"type":"boolean"},"include_balances":{"type":"boolean"},"include_overdue_summary":{"type":"boolean"},"requires_review":{"type":"boolean"}}'::jsonb,FALSE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,
    TRUE,TRUE,TRUE
WHERE NOT EXISTS(
    SELECT 1 FROM financial_rule_definitions WHERE codigo='ESTADO_CUENTA_PERIODICO'
);


INSERT INTO financial_rule_definitions(
    codigo,nombre,descripcion,dominio_codigo,nivel_base_codigo,
    tipo_resultado,esquema_parametros,obligatoria,
    admite_especializacion,admite_herencia,admite_override,
    admite_excepcion,requiere_aprobacion,permite_nivel_inmueble,
    permite_nivel_estructura,permite_nivel_espacio,
    contexto_kpi,contexto_ia,activo
)
SELECT
    'EMISION_RECIBOS','Emisión de recibos','Plantilla global genérica para emisión de recibos. Sus valores concretos se definen mediante configuración gobernada y perfiles jurisdiccionales cuando correspondan.','TESORERIA','CORE',
    'WORKFLOW','{"automatic_folio":{"type":"boolean"},"include_allocation_detail":{"type":"boolean"},"include_remaining_balance":{"type":"boolean"},"digital_document":{"type":"boolean"}}'::jsonb,FALSE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,
    TRUE,TRUE,TRUE
WHERE NOT EXISTS(
    SELECT 1 FROM financial_rule_definitions WHERE codigo='EMISION_RECIBOS'
);


INSERT INTO financial_rule_definitions(
    codigo,nombre,descripcion,dominio_codigo,nivel_base_codigo,
    tipo_resultado,esquema_parametros,obligatoria,
    admite_especializacion,admite_herencia,admite_override,
    admite_excepcion,requiere_aprobacion,permite_nivel_inmueble,
    permite_nivel_estructura,permite_nivel_espacio,
    contexto_kpi,contexto_ia,activo
)
SELECT
    'CONSTANCIA_NO_ADEUDO','Constancia de no adeudo','Plantilla global genérica para constancia de no adeudo. Sus valores concretos se definen mediante configuración gobernada y perfiles jurisdiccionales cuando correspondan.','REPORTES','CORE',
    'WORKFLOW','{"response_days":{"type":"integer","minimum":0},"validate_ordinary_fees":{"type":"boolean"},"validate_extraordinary_fees":{"type":"boolean"},"validate_other_approved_concepts":{"type":"boolean"},"requires_authorized_signature":{"type":"boolean"}}'::jsonb,FALSE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,
    TRUE,TRUE,TRUE
WHERE NOT EXISTS(
    SELECT 1 FROM financial_rule_definitions WHERE codigo='CONSTANCIA_NO_ADEUDO'
);


INSERT INTO financial_rule_definitions(
    codigo,nombre,descripcion,dominio_codigo,nivel_base_codigo,
    tipo_resultado,esquema_parametros,obligatoria,
    admite_especializacion,admite_herencia,admite_override,
    admite_excepcion,requiere_aprobacion,permite_nivel_inmueble,
    permite_nivel_estructura,permite_nivel_espacio,
    contexto_kpi,contexto_ia,activo
)
SELECT
    'DERECHOS_ASAMBLEA','Derechos en asamblea','Plantilla global genérica para derechos en asamblea. Sus valores concretos se definen mediante configuración gobernada y perfiles jurisdiccionales cuando correspondan.','GOBIERNO','CORE',
    'POLITICA','{"voice_allowed":{"type":"boolean"},"vote_allowed":{"type":"boolean"},"counts_for_quorum":{"type":"boolean"},"eligible_for_governance_roles":{"type":"boolean"},"requires_jurisdiction_profile":{"type":"boolean"}}'::jsonb,FALSE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,
    TRUE,TRUE,TRUE
WHERE NOT EXISTS(
    SELECT 1 FROM financial_rule_definitions WHERE codigo='DERECHOS_ASAMBLEA'
);


INSERT INTO financial_rule_definitions(
    codigo,nombre,descripcion,dominio_codigo,nivel_base_codigo,
    tipo_resultado,esquema_parametros,obligatoria,
    admite_especializacion,admite_herencia,admite_override,
    admite_excepcion,requiere_aprobacion,permite_nivel_inmueble,
    permite_nivel_estructura,permite_nivel_espacio,
    contexto_kpi,contexto_ia,activo
)
SELECT
    'PROTECCION_DATOS_MOROSIDAD','Protección de datos de morosidad','Plantilla global genérica para protección de datos de morosidad. Sus valores concretos se definen mediante configuración gobernada y perfiles jurisdiccionales cuando correspondan.','CUMPLIMIENTO','CORE',
    'POLITICA','{"visibility_level":{"type":"string","allowed":["RESTRINGIDA","ANONIMIZADA","POR_UNIDAD","AUTORIDAD"]},"allow_exports":{"type":"boolean"},"retention_days":{"type":"integer","minimum":0,"optional":true},"audit_access":{"type":"boolean"}}'::jsonb,FALSE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,
    TRUE,TRUE,TRUE
WHERE NOT EXISTS(
    SELECT 1 FROM financial_rule_definitions WHERE codigo='PROTECCION_DATOS_MOROSIDAD'
);


INSERT INTO financial_rule_definitions(
    codigo,nombre,descripcion,dominio_codigo,nivel_base_codigo,
    tipo_resultado,esquema_parametros,obligatoria,
    admite_especializacion,admite_herencia,admite_override,
    admite_excepcion,requiere_aprobacion,permite_nivel_inmueble,
    permite_nivel_estructura,permite_nivel_espacio,
    contexto_kpi,contexto_ia,activo
)
SELECT
    'RENTA_PERIODICA','Renta periódica','Plantilla global genérica para renta periódica. Sus valores concretos se definen mediante configuración gobernada y perfiles jurisdiccionales cuando correspondan.','RENTAS','CORE',
    'OBLIGACION','{"amount":{"type":"number","minimum":0},"payment_day":{"type":"integer","minimum":1,"maximum":31},"frequency":{"type":"string","allowed":["MENSUAL","BIMESTRAL","TRIMESTRAL","SEMESTRAL","ANUAL"]},"grace_days":{"type":"integer","minimum":0,"optional":true},"renewal_notice_days":{"type":"integer","minimum":0,"optional":true}}'::jsonb,FALSE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,
    TRUE,TRUE,TRUE
WHERE NOT EXISTS(
    SELECT 1 FROM financial_rule_definitions WHERE codigo='RENTA_PERIODICA'
);


INSERT INTO financial_rule_definitions(
    codigo,nombre,descripcion,dominio_codigo,nivel_base_codigo,
    tipo_resultado,esquema_parametros,obligatoria,
    admite_especializacion,admite_herencia,admite_override,
    admite_excepcion,requiere_aprobacion,permite_nivel_inmueble,
    permite_nivel_estructura,permite_nivel_espacio,
    contexto_kpi,contexto_ia,activo
)
SELECT
    'INCUMPLIMIENTO_RENTA','Incumplimiento de renta','Plantilla global genérica para incumplimiento de renta. Sus valores concretos se definen mediante configuración gobernada y perfiles jurisdiccionales cuando correspondan.','RENTAS','CORE',
    'WORKFLOW','{"overdue_days":{"type":"integer","minimum":0},"reminder_interval_days":{"type":"integer","minimum":0},"allow_payment_agreement":{"type":"boolean"},"requires_legal_review":{"type":"boolean"},"deposit_application_requires_evidence":{"type":"boolean"}}'::jsonb,FALSE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,TRUE,
    TRUE,TRUE,
    TRUE,TRUE,TRUE
WHERE NOT EXISTS(
    SELECT 1 FROM financial_rule_definitions WHERE codigo='INCUMPLIMIENTO_RENTA'
);

COMMIT;
