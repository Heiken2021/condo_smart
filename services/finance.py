from datetime import date
from decimal import Decimal, InvalidOperation
import json
import re

from core.authorization import require
from core.db import fetch_all, fetch_one, pool
from services.property_structure import structure_scope_spaces
from services.audit_service import (
    new_trace_id,
    sanitize,
)


PERIOD_PATTERN = re.compile(
    r"^[0-9]{4}-(0[1-9]|1[0-2])$"
)

MOVEMENT_TABLES = {
    "CARGO": "cargos",
    "PAGO": "pagos",
    "GASTO": "gastos",
}

MOVEMENT_ENTITIES = {
    "CARGO": "CARGO",
    "PAGO": "PAGO",
    "GASTO": "GASTO",
}


def _actor(actor_id):
    user = fetch_one(
        """
        SELECT
            id,
            username,
            nombre,
            email,
            rol_global,
            activo
        FROM usuarios
        WHERE id=%s
        """,
        (actor_id,),
    )

    if not user or not user.get("activo"):
        raise PermissionError("USER_INACTIVE")

    return dict(user)


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


def _amount(value):
    try:
        amount = Decimal(str(value))
    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "INVALID_FINANCIAL_AMOUNT"
        ) from exc

    if amount <= 0:
        raise ValueError(
            "FINANCIAL_AMOUNT_MUST_BE_POSITIVE"
        )

    return amount.quantize(
        Decimal("0.01")
    )


def _period(value):
    period = str(value or "").strip()

    if not PERIOD_PATTERN.fullmatch(period):
        raise ValueError(
            "INVALID_FINANCIAL_PERIOD"
        )

    return period


def _required_text(
    value,
    error_code,
    max_length=None,
):
    text = str(value or "").strip()

    if not text:
        raise ValueError(error_code)

    if max_length and len(text) > max_length:
        raise ValueError(
            error_code + "_TOO_LONG"
        )

    return text


def _optional_text(
    value,
    max_length=None,
):
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    if max_length and len(text) > max_length:
        raise ValueError(
            "FINANCIAL_TEXT_TOO_LONG"
        )

    return text


def _validate_space(
    property_id,
    space_id,
):
    row = fetch_one(
        """
        SELECT
            id,
            condominio_id,
            clave,
            nombre,
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

    if not row:
        raise ValueError(
            "FINANCIAL_SPACE_NOT_FOUND"
        )

    if not row.get("activo"):
        raise ValueError(
            "FINANCIAL_SPACE_INACTIVE"
        )

    return dict(row)


def _insert_financial_audit(
    cursor,
    *,
    actor,
    property_id,
    operation_type,
    entity,
    entity_id,
    space_id=None,
    amount=None,
    previous_status=None,
    new_status=None,
    reference=None,
    detail=None,
    metadata=None,
    trace_id=None,
):
    trace_id = trace_id or new_trace_id()

    sanitized_metadata = sanitize(
        metadata
    )

    cursor.execute(
        """
        INSERT INTO auditoria_financiera(
            condominio_id,
            usuario_id,
            username,
            tipo_operacion,
            entidad,
            entidad_id,
            espacio_id,
            monto_mxn,
            moneda,
            estado_anterior,
            estado_nuevo,
            referencia,
            detalle,
            metadata,
            trace_id
        )
        VALUES(
            %s,%s,%s,%s,%s,%s,%s,%s,
            'MXN',%s,%s,%s,%s,%s::jsonb,%s
        )
        RETURNING id
        """,
        (
            property_id,
            actor["id"],
            actor.get("username"),
            operation_type,
            entity,
            entity_id,
            space_id,
            amount,
            previous_status,
            new_status,
            reference,
            detail,
            (
                json.dumps(
                    sanitized_metadata,
                    default=str,
                    ensure_ascii=False,
                )
                if sanitized_metadata is not None
                else None
            ),
            trace_id,
        ),
    )

    return cursor.fetchone()


def list_charges(
    property_id,
    actor_id,
    period=None,
    space_id=None,
    include_cancelled=False,
):
    _require_actor(
        actor_id,
        "FINANZAS_CONSULTAR",
        property_id,
    )

    filters = [
        "c.condominio_id=%s",
    ]
    params = [property_id]

    if period:
        filters.append("c.periodo=%s")
        params.append(_period(period))

    if space_id:
        filters.append("c.espacio_id=%s")
        params.append(space_id)

    if not include_cancelled:
        filters.append(
            "c.estado_codigo='REGISTRADO'"
        )

    return fetch_all(
        f"""
        SELECT
            c.id,
            c.condominio_id,
            c.espacio_id,
            e.clave AS espacio_clave,
            e.nombre AS espacio_nombre,
            c.periodo,
            c.tipo_codigo,
            c.concepto,
            c.monto_mxn,
            c.estado_codigo,
            c.referencia,
            c.observaciones,
            c.creado_en,
            c.creado_por,
            c.cancelado_en,
            c.cancelado_por,
            c.motivo_cancelacion,
            c.activo
        FROM cargos c
        JOIN espacios e
          ON e.id=c.espacio_id
         AND e.condominio_id=c.condominio_id
        WHERE {" AND ".join(filters)}
        ORDER BY
            c.periodo DESC,
            c.creado_en DESC,
            c.id DESC
        """,
        tuple(params),
    )


def create_charge(
    property_id,
    space_id,
    period,
    charge_type,
    concept,
    amount,
    actor_id,
    reference=None,
    observations=None,
):
    actor = _require_actor(
        actor_id,
        "FINANZAS_CARGO_CREAR",
        property_id,
    )

    space = _validate_space(
        property_id,
        space_id,
    )

    period = _period(period)
    charge_type = _required_text(
        charge_type,
        "FINANCIAL_CHARGE_TYPE_REQUIRED",
        80,
    )
    concept = _required_text(
        concept,
        "FINANCIAL_CONCEPT_REQUIRED",
        200,
    )
    amount = _amount(amount)
    reference = _optional_text(
        reference,
        120,
    )
    observations = _optional_text(
        observations,
    )
    trace_id = new_trace_id()

    with pool().connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO cargos(
                        condominio_id,
                        espacio_id,
                        periodo,
                        tipo_codigo,
                        concepto,
                        monto_mxn,
                        estado_codigo,
                        referencia,
                        observaciones,
                        creado_por,
                        activo
                    )
                    VALUES(
                        %s,%s,%s,%s,%s,%s,
                        'REGISTRADO',%s,%s,%s,TRUE
                    )
                    RETURNING *
                    """,
                    (
                        property_id,
                        space_id,
                        period,
                        charge_type,
                        concept,
                        amount,
                        reference,
                        observations,
                        actor["id"],
                    ),
                )

                movement = dict(
                    cursor.fetchone()
                )

                audit = _insert_financial_audit(
                    cursor,
                    actor=actor,
                    property_id=property_id,
                    operation_type="CARGO_REGISTRADO",
                    entity="CARGO",
                    entity_id=movement["id"],
                    space_id=space_id,
                    amount=amount,
                    previous_status=None,
                    new_status="REGISTRADO",
                    reference=reference,
                    detail=concept,
                    metadata={
                        "periodo": period,
                        "tipo_codigo": charge_type,
                        "espacio": {
                            "id": space["id"],
                            "clave": space.get("clave"),
                            "nombre": space.get("nombre"),
                        },
                    },
                    trace_id=trace_id,
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    movement["audit_event_id"] = (
        audit["id"]
    )
    movement["trace_id"] = trace_id

    return movement


def list_payments(
    property_id,
    actor_id,
    period=None,
    space_id=None,
    include_cancelled=False,
):
    _require_actor(
        actor_id,
        "FINANZAS_CONSULTAR",
        property_id,
    )

    filters = [
        "p.condominio_id=%s",
    ]
    params = [property_id]

    if period:
        filters.append("p.periodo=%s")
        params.append(_period(period))

    if space_id:
        filters.append("p.espacio_id=%s")
        params.append(space_id)

    if not include_cancelled:
        filters.append(
            "p.estado_codigo='REGISTRADO'"
        )

    return fetch_all(
        f"""
        SELECT
            p.id,
            p.condominio_id,
            p.espacio_id,
            e.clave AS espacio_clave,
            e.nombre AS espacio_nombre,
            p.periodo,
            p.fecha,
            p.monto_mxn,
            p.estado_codigo,
            p.referencia,
            p.observaciones,
            p.creado_en,
            p.creado_por,
            p.cancelado_en,
            p.cancelado_por,
            p.motivo_cancelacion,
            p.activo
        FROM pagos p
        JOIN espacios e
          ON e.id=p.espacio_id
         AND e.condominio_id=p.condominio_id
        WHERE {" AND ".join(filters)}
        ORDER BY
            p.fecha DESC,
            p.creado_en DESC,
            p.id DESC
        """,
        tuple(params),
    )


def register_payment(
    property_id,
    space_id,
    period,
    payment_date,
    amount,
    actor_id,
    reference=None,
    observations=None,
):
    actor = _require_actor(
        actor_id,
        "FINANZAS_PAGO_REGISTRAR",
        property_id,
    )

    space = _validate_space(
        property_id,
        space_id,
    )

    period = _period(period)

    if not isinstance(payment_date, date):
        raise ValueError(
            "INVALID_PAYMENT_DATE"
        )

    amount = _amount(amount)
    reference = _optional_text(
        reference,
        120,
    )
    observations = _optional_text(
        observations,
    )
    trace_id = new_trace_id()

    with pool().connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO pagos(
                        condominio_id,
                        espacio_id,
                        periodo,
                        fecha,
                        monto_mxn,
                        estado_codigo,
                        referencia,
                        observaciones,
                        creado_por,
                        activo
                    )
                    VALUES(
                        %s,%s,%s,%s,%s,
                        'REGISTRADO',%s,%s,%s,TRUE
                    )
                    RETURNING *
                    """,
                    (
                        property_id,
                        space_id,
                        period,
                        payment_date,
                        amount,
                        reference,
                        observations,
                        actor["id"],
                    ),
                )

                movement = dict(
                    cursor.fetchone()
                )

                audit = _insert_financial_audit(
                    cursor,
                    actor=actor,
                    property_id=property_id,
                    operation_type="PAGO_REGISTRADO",
                    entity="PAGO",
                    entity_id=movement["id"],
                    space_id=space_id,
                    amount=amount,
                    previous_status=None,
                    new_status="REGISTRADO",
                    reference=reference,
                    detail="Registro de pago",
                    metadata={
                        "periodo": period,
                        "fecha": payment_date,
                        "espacio": {
                            "id": space["id"],
                            "clave": space.get("clave"),
                            "nombre": space.get("nombre"),
                        },
                    },
                    trace_id=trace_id,
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    movement["audit_event_id"] = (
        audit["id"]
    )
    movement["trace_id"] = trace_id

    return movement


def list_expenses(
    property_id,
    actor_id,
    date_from=None,
    date_to=None,
    category=None,
    include_cancelled=False,
):
    _require_actor(
        actor_id,
        "FINANZAS_CONSULTAR",
        property_id,
    )

    filters = [
        "g.condominio_id=%s",
    ]
    params = [property_id]

    if date_from:
        filters.append("g.fecha >= %s")
        params.append(date_from)

    if date_to:
        filters.append("g.fecha <= %s")
        params.append(date_to)

    if category:
        filters.append(
            "g.categoria_codigo=%s"
        )
        params.append(category)

    if not include_cancelled:
        filters.append(
            "g.estado_codigo='REGISTRADO'"
        )

    return fetch_all(
        f"""
        SELECT
            g.id,
            g.condominio_id,
            g.fecha,
            g.categoria_codigo,
            g.concepto,
            g.monto_mxn,
            g.estado_codigo,
            g.referencia,
            g.observaciones,
            g.creado_en,
            g.creado_por,
            g.cancelado_en,
            g.cancelado_por,
            g.motivo_cancelacion,
            g.activo
        FROM gastos g
        WHERE {" AND ".join(filters)}
        ORDER BY
            g.fecha DESC,
            g.creado_en DESC,
            g.id DESC
        """,
        tuple(params),
    )


def register_expense(
    property_id,
    expense_date,
    category,
    concept,
    amount,
    actor_id,
    reference=None,
    observations=None,
):
    actor = _require_actor(
        actor_id,
        "FINANZAS_GASTO_REGISTRAR",
        property_id,
    )

    if not isinstance(expense_date, date):
        raise ValueError(
            "INVALID_EXPENSE_DATE"
        )

    category = _required_text(
        category,
        "FINANCIAL_EXPENSE_CATEGORY_REQUIRED",
        80,
    )
    concept = _required_text(
        concept,
        "FINANCIAL_CONCEPT_REQUIRED",
        200,
    )
    amount = _amount(amount)
    reference = _optional_text(
        reference,
        120,
    )
    observations = _optional_text(
        observations,
    )
    trace_id = new_trace_id()

    with pool().connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO gastos(
                        condominio_id,
                        fecha,
                        categoria_codigo,
                        concepto,
                        monto_mxn,
                        estado_codigo,
                        referencia,
                        observaciones,
                        creado_por,
                        activo
                    )
                    VALUES(
                        %s,%s,%s,%s,%s,
                        'REGISTRADO',%s,%s,%s,TRUE
                    )
                    RETURNING *
                    """,
                    (
                        property_id,
                        expense_date,
                        category,
                        concept,
                        amount,
                        reference,
                        observations,
                        actor["id"],
                    ),
                )

                movement = dict(
                    cursor.fetchone()
                )

                audit = _insert_financial_audit(
                    cursor,
                    actor=actor,
                    property_id=property_id,
                    operation_type="GASTO_REGISTRADO",
                    entity="GASTO",
                    entity_id=movement["id"],
                    amount=amount,
                    previous_status=None,
                    new_status="REGISTRADO",
                    reference=reference,
                    detail=concept,
                    metadata={
                        "fecha": expense_date,
                        "categoria_codigo": category,
                    },
                    trace_id=trace_id,
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    movement["audit_event_id"] = (
        audit["id"]
    )
    movement["trace_id"] = trace_id

    return movement


def cancel_movement(
    property_id,
    movement_type,
    movement_id,
    reason,
    actor_id,
):
    actor = _require_actor(
        actor_id,
        "FINANZAS_MOVIMIENTO_CANCELAR",
        property_id,
    )

    movement_type = str(
        movement_type or ""
    ).upper()

    if movement_type not in MOVEMENT_TABLES:
        raise ValueError(
            "INVALID_FINANCIAL_MOVEMENT_TYPE"
        )

    reason = _required_text(
        reason,
        "FINANCIAL_CANCELLATION_REASON_REQUIRED",
    )

    table = MOVEMENT_TABLES[
        movement_type
    ]
    entity = MOVEMENT_ENTITIES[
        movement_type
    ]
    trace_id = new_trace_id()

    with pool().connection() as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT *
                    FROM {table}
                    WHERE id=%s
                      AND condominio_id=%s
                    FOR UPDATE
                    """,
                    (
                        movement_id,
                        property_id,
                    ),
                )

                current = cursor.fetchone()

                if not current:
                    raise ValueError(
                        "FINANCIAL_MOVEMENT_NOT_FOUND"
                    )

                current = dict(current)

                if (
                    current.get("estado_codigo")
                    == "CANCELADO"
                ):
                    raise ValueError(
                        "FINANCIAL_MOVEMENT_ALREADY_CANCELLED"
                    )

                cursor.execute(
                    f"""
                    UPDATE {table}
                    SET
                        estado_codigo='CANCELADO',
                        cancelado_en=NOW(),
                        cancelado_por=%s,
                        motivo_cancelacion=%s
                    WHERE id=%s
                      AND condominio_id=%s
                    RETURNING *
                    """,
                    (
                        actor["id"],
                        reason,
                        movement_id,
                        property_id,
                    ),
                )

                movement = dict(
                    cursor.fetchone()
                )

                audit = _insert_financial_audit(
                    cursor,
                    actor=actor,
                    property_id=property_id,
                    operation_type=(
                        f"{movement_type}_CANCELADO"
                    ),
                    entity=entity,
                    entity_id=movement_id,
                    space_id=current.get(
                        "espacio_id"
                    ),
                    amount=current.get(
                        "monto_mxn"
                    ),
                    previous_status="REGISTRADO",
                    new_status="CANCELADO",
                    reference=current.get(
                        "referencia"
                    ),
                    detail=reason,
                    metadata={
                        "motivo_cancelacion": reason,
                        "datos_originales": {
                            "periodo": current.get(
                                "periodo"
                            ),
                            "fecha": current.get(
                                "fecha"
                            ),
                            "concepto": current.get(
                                "concepto"
                            ),
                            "categoria_codigo": current.get(
                                "categoria_codigo"
                            ),
                            "tipo_codigo": current.get(
                                "tipo_codigo"
                            ),
                        },
                    },
                    trace_id=trace_id,
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    movement["audit_event_id"] = (
        audit["id"]
    )
    movement["trace_id"] = trace_id

    return movement


def account_statement(
    property_id,
    space_id,
    actor_id,
    period=None,
):
    _require_actor(
        actor_id,
        "FINANZAS_ESTADO_CUENTA",
        property_id,
    )

    _validate_space(
        property_id,
        space_id,
    )

    filters_charge = [
        "c.condominio_id=%s",
        "c.espacio_id=%s",
        "c.estado_codigo='REGISTRADO'",
    ]
    filters_payment = [
        "p.condominio_id=%s",
        "p.espacio_id=%s",
        "p.estado_codigo='REGISTRADO'",
    ]

    charge_params = [
        property_id,
        space_id,
    ]
    payment_params = [
        property_id,
        space_id,
    ]

    if period:
        period = _period(period)

        filters_charge.append(
            "c.periodo=%s"
        )
        charge_params.append(period)

        filters_payment.append(
            "p.periodo=%s"
        )
        payment_params.append(period)

    charges = fetch_all(
        f"""
        SELECT
            c.id,
            'CARGO' AS movimiento,
            c.periodo,
            c.creado_en AS fecha_movimiento,
            c.concepto,
            c.referencia,
            c.monto_mxn,
            c.estado_codigo
        FROM cargos c
        WHERE {" AND ".join(filters_charge)}
        ORDER BY
            c.periodo,
            c.creado_en,
            c.id
        """,
        tuple(charge_params),
    )

    payments = fetch_all(
        f"""
        SELECT
            p.id,
            'PAGO' AS movimiento,
            p.periodo,
            p.fecha AS fecha_movimiento,
            'Pago registrado' AS concepto,
            p.referencia,
            p.monto_mxn,
            p.estado_codigo
        FROM pagos p
        WHERE {" AND ".join(filters_payment)}
        ORDER BY
            p.periodo,
            p.fecha,
            p.id
        """,
        tuple(payment_params),
    )

    total_charges = sum(
        (
            Decimal(
                str(row.get("monto_mxn") or 0)
            )
            for row in charges
        ),
        Decimal("0"),
    )

    total_payments = sum(
        (
            Decimal(
                str(row.get("monto_mxn") or 0)
            )
            for row in payments
        ),
        Decimal("0"),
    )

    return {
        "property_id": property_id,
        "space_id": space_id,
        "period": period,
        "charges": charges,
        "payments": payments,
        "total_charges": total_charges,
        "total_payments": total_payments,
        "balance": total_charges - total_payments,
    }


def financial_summary(
    property_id,
    actor_id,
    period=None,
):
    _require_actor(
        actor_id,
        "FINANZAS_CONSULTAR",
        property_id,
    )

    charge_filter = ""
    payment_filter = ""
    charge_params = [property_id]
    payment_params = [property_id]

    if period:
        period = _period(period)
        charge_filter = " AND periodo=%s"
        payment_filter = " AND periodo=%s"
        charge_params.append(period)
        payment_params.append(period)

    charges = fetch_one(
        f"""
        SELECT
            COALESCE(SUM(monto_mxn), 0)
            AS total
        FROM cargos
        WHERE condominio_id=%s
          AND estado_codigo='REGISTRADO'
          {charge_filter}
        """,
        tuple(charge_params),
    )

    payments = fetch_one(
        f"""
        SELECT
            COALESCE(SUM(monto_mxn), 0)
            AS total
        FROM pagos
        WHERE condominio_id=%s
          AND estado_codigo='REGISTRADO'
          {payment_filter}
        """,
        tuple(payment_params),
    )

    expenses = fetch_one(
        """
        SELECT
            COALESCE(SUM(monto_mxn), 0)
            AS total
        FROM gastos
        WHERE condominio_id=%s
          AND estado_codigo='REGISTRADO'
        """,
        (property_id,),
    )

    total_charges = Decimal(
        str(charges["total"])
    )
    total_payments = Decimal(
        str(payments["total"])
    )
    total_expenses = Decimal(
        str(expenses["total"])
    )

    return {
        "property_id": property_id,
        "period": period,
        "charges": total_charges,
        "payments": total_payments,
        "pending": max(
            total_charges - total_payments,
            Decimal("0"),
        ),
        "expenses": total_expenses,
        "available_balance": (
            total_payments - total_expenses
        ),
    }



def financial_scope_space_ids(
    property_id,
    scope_kind="ALL",
    structure_id=None,
):
    rows = structure_scope_spaces(
        property_id,
        scope_kind,
        structure_id=structure_id,
        active_only=True,
    )

    return [
        row["id"]
        for row in rows
    ]


def financial_scope_options(
    property_id,
):
    from services.property_structure import (
        list_nodes,
        node_path,
    )

    nodes = list_nodes(
        property_id,
        active_only=True,
    )

    options = [
        {
            "kind": "ALL",
            "structure_id": None,
            "label": "Todo el inmueble",
        },
        {
            "kind": "DIRECT",
            "structure_id": None,
            "label": "Espacios Directos",
        },
    ]

    options.extend(
        {
            "kind": "NODE",
            "structure_id": node["id"],
            "label": (
                node_path(
                    nodes,
                    node["id"],
                )
                or node.get("nombre")
                or str(node["id"])
            ),
            "type": node.get("tipo_codigo"),
        }
        for node in nodes
    )

    return options


def scope_financial_rows(
    rows,
    allowed_space_ids,
):
    allowed = set(
        allowed_space_ids
    )

    return [
        row
        for row in rows
        if row.get("espacio_id") in allowed
    ]
