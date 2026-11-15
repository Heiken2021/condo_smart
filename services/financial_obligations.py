from datetime import date
from decimal import Decimal, InvalidOperation

from core.authorization import require
from core.db import fetch_all, fetch_one, pool
from services.financial_governance_commands import (
    _actor,
    _insert_audit,
    _optional_text,
    _required_text,
)
from services.audit_service import new_trace_id


def _require_actor(
    actor_id,
    permission,
    property_id,
):
    actor = _actor(actor_id)

    require(
        actor,
        permission,
        property_id,
    )

    return actor


def _money(value, error_code):
    try:
        amount = Decimal(str(value))
    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):
        raise ValueError(error_code)

    if amount <= Decimal("0"):
        raise ValueError(error_code)

    return amount.quantize(
        Decimal("0.01")
    )


def _period(value):
    text = _required_text(
        value,
        "FINANCIAL_OBLIGATION_PERIOD_REQUIRED",
        7,
    )

    if (
        len(text) != 7
        or text[4] != "-"
        or not text[:4].isdigit()
        or not text[5:].isdigit()
        or int(text[5:]) not in range(1, 13)
    ):
        raise ValueError(
            "INVALID_FINANCIAL_OBLIGATION_PERIOD"
        )

    return text


def get_obligation_balance(
    *,
    property_id,
    obligation_id,
    actor_id,
):
    _require_actor(
        actor_id,
        "FINANZAS_GOBIERNO_CONSULTAR",
        property_id,
    )

    row = fetch_one(
        """
        SELECT *
        FROM financial_obligation_balances
        WHERE obligation_id=%s
          AND condominio_id=%s
        """,
        (
            obligation_id,
            property_id,
        ),
    )

    if not row:
        raise ValueError(
            "FINANCIAL_OBLIGATION_NOT_FOUND"
        )

    return dict(row)


def list_financial_obligations(
    *,
    property_id,
    actor_id,
    space_ids=None,
    period=None,
    situation=None,
):
    _require_actor(
        actor_id,
        "FINANZAS_GOBIERNO_CONSULTAR",
        property_id,
    )

    clauses = [
        "balance.condominio_id=%s",
    ]

    params = [
        property_id,
    ]

    if space_ids is not None:
        ids = [
            int(space_id)
            for space_id in space_ids
        ]

        if not ids:
            return []

        clauses.append(
            "balance.espacio_id=ANY(%s)"
        )
        params.append(ids)

    if period:
        clauses.append(
            "balance.periodo=%s"
        )
        params.append(
            _period(period)
        )

    if situation:
        clauses.append(
            "balance.situacion_codigo=%s"
        )
        params.append(
            str(situation).strip().upper()
        )

    rows = fetch_all(
        f"""
        SELECT
            balance.*,
            obligation.fecha_generacion,
            obligation.fecha_vencimiento,
            obligation.estado_codigo,
            obligation.rule_version_id,
            obligation.space_fee_history_id,
            obligation.referencia,
            obligation.creado_en
        FROM financial_obligation_balances balance
        JOIN financial_obligations obligation
          ON obligation.id=
             balance.obligation_id
        WHERE {' AND '.join(clauses)}
        ORDER BY
            balance.periodo DESC,
            obligation.fecha_vencimiento,
            balance.obligation_id
        """,
        tuple(params),
    )

    return [
        dict(row)
        for row in rows
    ]


def create_financial_obligation(
    *,
    property_id,
    space_id,
    period,
    obligation_type,
    concept,
    amount,
    generation_date,
    actor_id,
    due_date=None,
    structure_id=None,
    rule_version_id=None,
    space_fee_history_id=None,
    reference=None,
    observations=None,
):
    actor = _require_actor(
        actor_id,
        "FINANZAS_OBLIGACION_CREAR",
        property_id,
    )

    period = _period(period)

    obligation_type = _required_text(
        obligation_type,
        "FINANCIAL_OBLIGATION_TYPE_REQUIRED",
        80,
    ).upper()

    concept = _required_text(
        concept,
        "FINANCIAL_OBLIGATION_CONCEPT_REQUIRED",
        240,
    )

    amount = _money(
        amount,
        "INVALID_FINANCIAL_OBLIGATION_AMOUNT",
    )

    if not isinstance(
        generation_date,
        date,
    ):
        raise ValueError(
            "INVALID_FINANCIAL_OBLIGATION_GENERATION_DATE"
        )

    if (
        due_date is not None
        and not isinstance(due_date, date)
    ):
        raise ValueError(
            "INVALID_FINANCIAL_OBLIGATION_DUE_DATE"
        )

    if (
        due_date is not None
        and due_date < generation_date
    ):
        raise ValueError(
            "INVALID_FINANCIAL_OBLIGATION_DATE_RANGE"
        )

    trace_id = new_trace_id()

    with pool().connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        condominio_id,
                        estructura_id,
                        clave,
                        activo
                    FROM espacios
                    WHERE id=%s
                      AND condominio_id=%s
                    """,
                    (
                        space_id,
                        property_id,
                    ),
                )

                space = cursor.fetchone()

                if not space:
                    raise ValueError(
                        "FINANCIAL_OBLIGATION_SPACE_NOT_FOUND"
                    )

                if not space.get("activo"):
                    raise ValueError(
                        "FINANCIAL_OBLIGATION_SPACE_INACTIVE"
                    )

                effective_structure_id = (
                    space.get("estructura_id")
                    if structure_id is None
                    else structure_id
                )

                if (
                    effective_structure_id
                    != space.get("estructura_id")
                ):
                    raise ValueError(
                        "FINANCIAL_OBLIGATION_STRUCTURE_CONTEXT_MISMATCH"
                    )

                cursor.execute(
                    """
                    INSERT INTO financial_obligations(
                        condominio_id,
                        estructura_id,
                        espacio_id,
                        periodo,
                        fecha_generacion,
                        fecha_vencimiento,
                        tipo_codigo,
                        concepto,
                        monto_original_mxn,
                        estado_codigo,
                        rule_version_id,
                        space_fee_history_id,
                        referencia,
                        observaciones,
                        creado_por
                    )
                    VALUES(
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,
                        'REGISTRADA',%s,%s,%s,%s,%s
                    )
                    RETURNING *
                    """,
                    (
                        property_id,
                        effective_structure_id,
                        space_id,
                        period,
                        generation_date,
                        due_date,
                        obligation_type,
                        concept,
                        amount,
                        rule_version_id,
                        space_fee_history_id,
                        _optional_text(reference, 120),
                        _optional_text(observations),
                        actor["id"],
                    ),
                )

                obligation = dict(
                    cursor.fetchone()
                )

                audit = _insert_audit(
                    cursor,
                    actor=actor,
                    property_id=property_id,
                    operation_type=(
                        "FINANCIAL_OBLIGATION_CREATED"
                    ),
                    entity="FINANCIAL_OBLIGATION",
                    entity_id=obligation["id"],
                    previous_status=None,
                    new_status="REGISTRADA",
                    detail=concept,
                    metadata={
                        "espacio_id": space_id,
                        "estructura_id": (
                            effective_structure_id
                        ),
                        "periodo": period,
                        "tipo_codigo": (
                            obligation_type
                        ),
                        "monto_original_mxn": (
                            amount
                        ),
                        "rule_version_id": (
                            rule_version_id
                        ),
                        "space_fee_history_id": (
                            space_fee_history_id
                        ),
                    },
                    trace_id=trace_id,
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    obligation["audit_event_id"] = (
        audit["id"]
    )
    obligation["trace_id"] = trace_id

    return obligation


def cancel_financial_obligation(
    *,
    property_id,
    obligation_id,
    actor_id,
    cancellation_reason,
):
    actor = _require_actor(
        actor_id,
        "FINANZAS_OBLIGACION_CANCELAR",
        property_id,
    )

    cancellation_reason = _required_text(
        cancellation_reason,
        "FINANCIAL_OBLIGATION_CANCELLATION_REASON_REQUIRED",
    )

    trace_id = new_trace_id()

    with pool().connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM financial_obligations
                    WHERE id=%s
                      AND condominio_id=%s
                    FOR UPDATE
                    """,
                    (
                        obligation_id,
                        property_id,
                    ),
                )

                current = cursor.fetchone()

                if not current:
                    raise ValueError(
                        "FINANCIAL_OBLIGATION_NOT_FOUND"
                    )

                current = dict(current)

                if (
                    current["estado_codigo"]
                    != "REGISTRADA"
                ):
                    raise ValueError(
                        "FINANCIAL_OBLIGATION_NOT_CANCELLABLE"
                    )

                cursor.execute(
                    """
                    UPDATE financial_obligations
                    SET
                        estado_codigo='CANCELADA',
                        cancelado_por=%s,
                        cancelado_en=NOW(),
                        motivo_cancelacion=%s
                    WHERE id=%s
                      AND condominio_id=%s
                    RETURNING *
                    """,
                    (
                        actor["id"],
                        cancellation_reason,
                        obligation_id,
                        property_id,
                    ),
                )

                obligation = dict(
                    cursor.fetchone()
                )

                audit = _insert_audit(
                    cursor,
                    actor=actor,
                    property_id=property_id,
                    operation_type=(
                        "FINANCIAL_OBLIGATION_CANCELLED"
                    ),
                    entity="FINANCIAL_OBLIGATION",
                    entity_id=obligation_id,
                    previous_status="REGISTRADA",
                    new_status="CANCELADA",
                    detail=cancellation_reason,
                    metadata={
                        "espacio_id": obligation[
                            "espacio_id"
                        ],
                        "periodo": obligation[
                            "periodo"
                        ],
                        "monto_original_mxn": (
                            obligation[
                                "monto_original_mxn"
                            ]
                        ),
                    },
                    trace_id=trace_id,
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    obligation["audit_event_id"] = (
        audit["id"]
    )
    obligation["trace_id"] = trace_id

    return obligation


def apply_payment_to_obligation(
    *,
    property_id,
    payment_id,
    obligation_id,
    amount,
    actor_id,
    exception_id=None,
):
    actor = _require_actor(
        actor_id,
        "FINANZAS_PAGO_APLICAR",
        property_id,
    )

    amount = _money(
        amount,
        "INVALID_PAYMENT_ALLOCATION_AMOUNT",
    )

    trace_id = new_trace_id()

    with pool().connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        condominio_id,
                        espacio_id,
                        monto_mxn,
                        estado_codigo,
                        activo
                    FROM pagos
                    WHERE id=%s
                      AND condominio_id=%s
                    FOR UPDATE
                    """,
                    (
                        payment_id,
                        property_id,
                    ),
                )

                payment = cursor.fetchone()

                if not payment:
                    raise ValueError(
                        "FINANCIAL_ALLOCATION_PAYMENT_NOT_FOUND"
                    )

                cursor.execute(
                    """
                    SELECT
                        id,
                        condominio_id,
                        espacio_id,
                        periodo,
                        monto_original_mxn,
                        estado_codigo
                    FROM financial_obligations
                    WHERE id=%s
                      AND condominio_id=%s
                    FOR UPDATE
                    """,
                    (
                        obligation_id,
                        property_id,
                    ),
                )

                obligation = cursor.fetchone()

                if not obligation:
                    raise ValueError(
                        "FINANCIAL_ALLOCATION_OBLIGATION_NOT_FOUND"
                    )

                cursor.execute(
                    """
                    INSERT INTO payment_allocations(
                        condominio_id,
                        pago_id,
                        obligation_id,
                        monto_aplicado_mxn,
                        financial_rule_exception_id,
                        estado_codigo,
                        aplicado_por
                    )
                    VALUES(
                        %s,%s,%s,%s,%s,
                        'ACTIVA',%s
                    )
                    RETURNING *
                    """,
                    (
                        property_id,
                        payment_id,
                        obligation_id,
                        amount,
                        exception_id,
                        actor["id"],
                    ),
                )

                allocation = dict(
                    cursor.fetchone()
                )

                audit = _insert_audit(
                    cursor,
                    actor=actor,
                    property_id=property_id,
                    operation_type=(
                        "PAYMENT_ALLOCATED_TO_OBLIGATION"
                    ),
                    entity="PAYMENT_ALLOCATION",
                    entity_id=allocation["id"],
                    previous_status=None,
                    new_status="ACTIVA",
                    detail=(
                        "Aplicación de pago a obligación"
                    ),
                    metadata={
                        "pago_id": payment_id,
                        "obligation_id": (
                            obligation_id
                        ),
                        "espacio_id": obligation[
                            "espacio_id"
                        ],
                        "monto_aplicado_mxn": (
                            amount
                        ),
                        "exception_id": (
                            exception_id
                        ),
                    },
                    trace_id=trace_id,
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    allocation["audit_event_id"] = (
        audit["id"]
    )
    allocation["trace_id"] = trace_id

    return allocation


def reverse_payment_allocation(
    *,
    property_id,
    allocation_id,
    actor_id,
    reversal_reason,
):
    actor = _require_actor(
        actor_id,
        "FINANZAS_PAGO_REVERTIR_APLICACION",
        property_id,
    )

    reversal_reason = _required_text(
        reversal_reason,
        "PAYMENT_ALLOCATION_REVERSAL_REASON_REQUIRED",
    )

    trace_id = new_trace_id()

    with pool().connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM payment_allocations
                    WHERE id=%s
                      AND condominio_id=%s
                    FOR UPDATE
                    """,
                    (
                        allocation_id,
                        property_id,
                    ),
                )

                current = cursor.fetchone()

                if not current:
                    raise ValueError(
                        "PAYMENT_ALLOCATION_NOT_FOUND"
                    )

                current = dict(current)

                if (
                    current["estado_codigo"]
                    != "ACTIVA"
                ):
                    raise ValueError(
                        "PAYMENT_ALLOCATION_NOT_REVERSIBLE"
                    )

                cursor.execute(
                    """
                    UPDATE payment_allocations
                    SET
                        estado_codigo='REVERSADA',
                        reversado_por=%s,
                        reversado_en=NOW(),
                        motivo_reversion=%s
                    WHERE id=%s
                      AND condominio_id=%s
                    RETURNING *
                    """,
                    (
                        actor["id"],
                        reversal_reason,
                        allocation_id,
                        property_id,
                    ),
                )

                allocation = dict(
                    cursor.fetchone()
                )

                audit = _insert_audit(
                    cursor,
                    actor=actor,
                    property_id=property_id,
                    operation_type=(
                        "PAYMENT_ALLOCATION_REVERSED"
                    ),
                    entity="PAYMENT_ALLOCATION",
                    entity_id=allocation_id,
                    previous_status="ACTIVA",
                    new_status="REVERSADA",
                    detail=reversal_reason,
                    metadata={
                        "pago_id": allocation[
                            "pago_id"
                        ],
                        "obligation_id": allocation[
                            "obligation_id"
                        ],
                        "monto_aplicado_mxn": (
                            allocation[
                                "monto_aplicado_mxn"
                            ]
                        ),
                    },
                    trace_id=trace_id,
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    allocation["audit_event_id"] = (
        audit["id"]
    )
    allocation["trace_id"] = trace_id

    return allocation



def _period_start(period):
    period = _period(period)

    year = int(period[:4])
    month = int(period[5:7])

    return date(
        year,
        month,
        1,
    )


def _effective_space_fee(
    *,
    property_id,
    space_id,
    fee_type,
    effective_date,
):
    row = fetch_one(
        """
        SELECT
            id,
            condominio_id,
            espacio_id,
            tipo_cuota_codigo,
            monto_mxn,
            vigente_desde,
            vigente_hasta,
            origen_codigo,
            rule_version_id,
            estado_codigo
        FROM space_fee_history
        WHERE condominio_id=%s
          AND espacio_id=%s
          AND tipo_cuota_codigo=%s
          AND estado_codigo='APROBADO'
          AND vigente_desde <= %s
          AND (
              vigente_hasta IS NULL
              OR vigente_hasta >= %s
          )
        ORDER BY
            vigente_desde DESC,
            id DESC
        LIMIT 1
        """,
        (
            property_id,
            space_id,
            fee_type,
            effective_date,
            effective_date,
        ),
    )

    return (
        dict(row)
        if row
        else None
    )


def generate_governed_obligation(
    *,
    property_id,
    space_id,
    period,
    rule_code,
    fee_type,
    concept,
    generation_date,
    actor_id,
    due_date=None,
    reference=None,
    observations=None,
):
    from services.financial_governance import (
        resolve_effective_rule,
    )

    period = _period(period)
    effective_date = _period_start(
        period
    )

    rule = resolve_effective_rule(
        rule_code=rule_code,
        property_id=property_id,
        space_id=space_id,
        actor_id=actor_id,
        effective_date=effective_date,
    )

    if not rule.get("found"):
        raise ValueError(
            "EFFECTIVE_FINANCIAL_RULE_REQUIRED"
        )

    selected = rule[
        "selected_rule"
    ]

    definition = rule[
        "definition"
    ]

    fee_type = _required_text(
        fee_type,
        "FINANCIAL_FEE_TYPE_REQUIRED",
        80,
    ).upper()

    fee = _effective_space_fee(
        property_id=property_id,
        space_id=space_id,
        fee_type=fee_type,
        effective_date=effective_date,
    )

    if not fee:
        raise ValueError(
            "EFFECTIVE_APPROVED_SPACE_FEE_REQUIRED"
        )

    if (
        fee.get("rule_version_id")
        is not None
        and fee["rule_version_id"]
            != selected["version_id"]
    ):
        raise ValueError(
            "SPACE_FEE_RULE_VERSION_MISMATCH"
        )

    context = rule["context"]
    space = context.get("space")

    if not space:
        raise ValueError(
            "FINANCIAL_RULE_SPACE_CONTEXT_REQUIRED"
        )

    structure_id = space.get(
        "estructura_id"
    )

    duplicates = fetch_all(
        """
        SELECT
            id,
            estado_codigo
        FROM financial_obligations
        WHERE condominio_id=%s
          AND espacio_id=%s
          AND periodo=%s
          AND tipo_codigo=%s
          AND estado_codigo='REGISTRADA'
        ORDER BY id
        """,
        (
            property_id,
            space_id,
            period,
            fee_type,
        ),
    )

    if duplicates:
        raise ValueError(
            "ACTIVE_PERIODIC_OBLIGATION_ALREADY_EXISTS"
        )

    obligation = create_financial_obligation(
        property_id=property_id,
        space_id=space_id,
        period=period,
        obligation_type=fee_type,
        concept=concept,
        amount=fee["monto_mxn"],
        generation_date=generation_date,
        due_date=due_date,
        structure_id=structure_id,
        rule_version_id=(
            selected["version_id"]
        ),
        space_fee_history_id=(
            fee["id"]
        ),
        reference=reference,
        observations=observations,
        actor_id=actor_id,
    )

    obligation[
        "governance_context"
    ] = {
        "rule_code": rule_code,
        "rule_definition_id": (
            definition["id"]
        ),
        "rule_version_id": (
            selected["version_id"]
        ),
        "scope_level": (
            selected["scope_level"]
        ),
        "space_fee_history_id": (
            fee["id"]
        ),
        "fee_type": fee_type,
        "fee_amount": fee[
            "monto_mxn"
        ],
        "effective_date": (
            effective_date
        ),
        "exception_applied": (
            rule["explanation"][
                "exception_applied"
            ]
        ),
        "context_kpi": rule[
            "context_kpi"
        ],
        "context_ai": rule[
            "context_ai"
        ],
    }

    return obligation
