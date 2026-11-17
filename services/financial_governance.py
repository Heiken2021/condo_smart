from datetime import date

from core.authorization import require
from core.db import fetch_all, fetch_one


SCOPE_RANK = {
    "CORE": 100,
    "TIPOLOGIA": 200,
    "INMUEBLE": 300,
    "ESTRUCTURA": 400,
    "ESPACIO": 500,
}


def _actor(actor_id):
    row = fetch_one(
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

    if not row or not row.get("activo"):
        raise PermissionError(
            "USER_INACTIVE"
        )

    return dict(row)


def _require_governance_read(
    actor_id,
    property_id,
):
    actor = _actor(actor_id)

    require(
        actor,
        "FINANZAS_GOBIERNO_CONSULTAR",
        property_id,
    )

    return actor


def _context(
    property_id,
    space_id=None,
):
    property_row = fetch_one(
        """
        SELECT
            id,
            clave,
            nombre,
            tipo_codigo,
            moneda_base,
            activo
        FROM condominios
        WHERE id=%s
        """,
        (property_id,),
    )

    if not property_row:
        raise ValueError(
            "FINANCIAL_RULE_PROPERTY_NOT_FOUND"
        )

    if not property_row.get("activo"):
        raise ValueError(
            "FINANCIAL_RULE_PROPERTY_INACTIVE"
        )

    context = {
        "property": dict(property_row),
        "space": None,
        "structure_path": [],
        "dimensions": {
            "TIPO_INMUEBLE": {
                property_row.get("tipo_codigo")
            },
            "TIPO_ESTRUCTURA": set(),
            "TIPO_ESPACIO": set(),
            "GIRO": set(),
        },
        "business_use_code": None,
    }

    if space_id is None:
        return context

    space = fetch_one(
        """
        SELECT
            id,
            condominio_id,
            estructura_id,
            clave,
            nombre,
            tipo_codigo,
            uso_codigo,
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

    if not space:
        raise ValueError(
            "FINANCIAL_RULE_SPACE_NOT_FOUND"
        )

    if not space.get("activo"):
        raise ValueError(
            "FINANCIAL_RULE_SPACE_INACTIVE"
        )

    context["space"] = dict(space)
    context["business_use_code"] = (
        space.get("uso_codigo")
    )

    if space.get("tipo_codigo"):
        context["dimensions"][
            "TIPO_ESPACIO"
        ].add(
            space["tipo_codigo"]
        )

    structure_id = space.get(
        "estructura_id"
    )

    if structure_id is None:
        return context

    rows = fetch_all(
        """
        WITH RECURSIVE ancestry AS (
            SELECT
                node.id,
                node.condominio_id,
                node.parent_id,
                node.tipo_codigo,
                node.clave,
                node.nombre,
                0 AS depth_from_space
            FROM estructura_inmueble node
            WHERE node.id=%s
              AND node.condominio_id=%s
              AND node.activo=TRUE

            UNION ALL

            SELECT
                parent.id,
                parent.condominio_id,
                parent.parent_id,
                parent.tipo_codigo,
                parent.clave,
                parent.nombre,
                child.depth_from_space + 1
            FROM ancestry child
            JOIN estructura_inmueble parent
              ON parent.id=child.parent_id
             AND parent.condominio_id=
                 child.condominio_id
             AND parent.activo=TRUE
        )
        SELECT
            id,
            parent_id,
            tipo_codigo,
            clave,
            nombre,
            depth_from_space
        FROM ancestry
        ORDER BY depth_from_space DESC
        """,
        (
            structure_id,
            property_id,
        ),
    )

    context["structure_path"] = [
        dict(row)
        for row in rows
    ]

    for row in rows:
        if row.get("tipo_codigo"):
            context["dimensions"][
                "TIPO_ESTRUCTURA"
            ].add(
                row["tipo_codigo"]
            )

    return context


def _definition_applicable(
    definition_id,
    dimensions,
):
    rows = fetch_all(
        """
        SELECT
            dimension_codigo,
            valor_codigo,
            incluido
        FROM financial_rule_applicability
        WHERE rule_definition_id=%s
        ORDER BY
            dimension_codigo,
            valor_codigo
        """,
        (definition_id,),
    )

    if not rows:
        return {
            "allowed": True,
            "reason": (
                "NO_APPLICABILITY_RESTRICTIONS"
            ),
            "evaluated": [],
        }

    grouped = {}

    for row in rows:
        grouped.setdefault(
            row["dimension_codigo"],
            [],
        ).append(dict(row))

    evaluated = []

    for dimension, rules in grouped.items():
        actual_values = set(
            dimensions.get(
                dimension,
                set(),
            )
        )

        excluded = {
            row["valor_codigo"]
            for row in rules
            if not row["incluido"]
        }

        included = {
            row["valor_codigo"]
            for row in rules
            if row["incluido"]
        }

        if actual_values & excluded:
            evaluated.append({
                "dimension": dimension,
                "actual": sorted(
                    actual_values
                ),
                "allowed": False,
                "reason": "EXPLICITLY_EXCLUDED",
            })

            return {
                "allowed": False,
                "reason": (
                    "APPLICABILITY_EXCLUDED"
                ),
                "evaluated": evaluated,
            }

        if included and not (
            actual_values & included
        ):
            evaluated.append({
                "dimension": dimension,
                "actual": sorted(
                    actual_values
                ),
                "allowed": False,
                "reason": (
                    "NO_INCLUDED_VALUE_MATCH"
                ),
            })

            return {
                "allowed": False,
                "reason": (
                    "APPLICABILITY_NOT_INCLUDED"
                ),
                "evaluated": evaluated,
            }

        evaluated.append({
            "dimension": dimension,
            "actual": sorted(
                actual_values
            ),
            "allowed": True,
            "reason": "MATCH",
        })

    return {
        "allowed": True,
        "reason": "APPLICABILITY_MATCH",
        "evaluated": evaluated,
    }


def _type_rule_matches(
    rule,
    dimensions,
):
    applicable_code = rule.get(
        "tipo_aplicable_codigo"
    )

    if not applicable_code:
        return True

    all_values = set()

    for values in dimensions.values():
        all_values.update(values)

    return applicable_code in all_values


def _structure_rank(
    structure_id,
    structure_path,
):
    for position, node in enumerate(
        structure_path,
        start=1,
    ):
        if node["id"] == structure_id:
            return (
                SCOPE_RANK["ESTRUCTURA"]
                + position
            )

    return None


def _candidate_rank(
    rule,
    context,
):
    level = rule["scope_level"]

    if level == "CORE":
        return SCOPE_RANK["CORE"]

    if level == "TIPOLOGIA":
        if not _type_rule_matches(
            rule,
            context["dimensions"],
        ):
            return None

        return SCOPE_RANK["TIPOLOGIA"]

    if level == "INMUEBLE":
        if (
            rule.get("condominio_id")
            != context["property"]["id"]
        ):
            return None

        return SCOPE_RANK["INMUEBLE"]

    if level == "ESTRUCTURA":
        if (
            rule.get("condominio_id")
            != context["property"]["id"]
        ):
            return None

        return _structure_rank(
            rule.get("estructura_id"),
            context["structure_path"],
        )

    if level == "ESPACIO":
        space = context.get("space")

        if not space:
            return None

        if (
            rule.get("condominio_id")
            != context["property"]["id"]
            or rule.get("espacio_id")
            != space["id"]
        ):
            return None

        return SCOPE_RANK["ESPACIO"]

    return None


def _approved_candidates(
    definition,
    context,
    effective_date,
):
    rows = fetch_all(
        """
        SELECT
            rule.id AS rule_id,
            rule.rule_definition_id,
            rule.policy_id,
            rule.scope_level,
            rule.condominio_id,
            rule.estructura_id,
            rule.espacio_id,
            rule.tipo_aplicable_codigo,
            rule.codigo AS rule_code,
            rule.nombre AS rule_name,
            rule.descripcion,
            rule.hereda,
            rule.es_override,
            rule.prioridad,
            version.id AS version_id,
            version.version_num,
            version.vigente_desde,
            version.vigente_hasta,
            version.parametros,
            version.aprobado_por,
            version.aprobado_en,
            version.motivo_cambio
        FROM financial_rules rule
        JOIN financial_rule_versions version
          ON version.rule_id=rule.id
        WHERE rule.rule_definition_id=%s
          AND rule.activo=TRUE
          AND version.estado_codigo='APROBADO'
          AND version.vigente_desde <= %s
          AND (
              version.vigente_hasta IS NULL
              OR version.vigente_hasta >= %s
          )
        ORDER BY
            rule.prioridad DESC,
            version.version_num DESC,
            version.id DESC
        """,
        (
            definition["id"],
            effective_date,
            effective_date,
        ),
    )

    candidates = []

    for row in rows:
        candidate = dict(row)

        rank = _candidate_rank(
            candidate,
            context,
        )

        if rank is None:
            candidate["eligible"] = False
            candidate["resolution_reason"] = (
                "SCOPE_NOT_APPLICABLE"
            )
            candidate["scope_rank"] = None
            candidates.append(candidate)
            continue

        candidate["eligible"] = True

        candidate["resolution_reason"] = (
            "ELIGIBLE_OVERRIDE"
            if candidate.get(
                "es_override"
            )
            else "ELIGIBLE_BASE_CONFIGURATION"
        )
        candidate["scope_rank"] = rank
        candidates.append(candidate)

    return candidates


def _approved_exception(
    version_id,
    context,
    effective_date,
):
    rows = fetch_all(
        """
        SELECT
            id,
            condominio_id,
            estructura_id,
            espacio_id,
            tipo_excepcion,
            parametros,
            motivo,
            vigente_desde,
            vigente_hasta,
            solicitado_por,
            solicitado_en,
            resuelto_por,
            resuelto_en,
            decision_detalle
        FROM financial_rule_exceptions
        WHERE rule_version_id=%s
          AND estado_codigo='APROBADA'
          AND condominio_id=%s
          AND (
              vigente_desde IS NULL
              OR vigente_desde <= %s
          )
          AND (
              vigente_hasta IS NULL
              OR vigente_hasta >= %s
          )
        ORDER BY
            CASE
                WHEN espacio_id IS NOT NULL
                    THEN 3
                WHEN estructura_id IS NOT NULL
                    THEN 2
                ELSE 1
            END DESC,
            resuelto_en DESC,
            id DESC
        """,
        (
            version_id,
            context["property"]["id"],
            effective_date,
            effective_date,
        ),
    )

    structure_ids = {
        node["id"]
        for node in context[
            "structure_path"
        ]
    }

    space = context.get("space")

    for row in rows:
        exception = dict(row)

        if (
            exception.get("espacio_id")
            is not None
        ):
            if (
                not space
                or exception["espacio_id"]
                != space["id"]
            ):
                continue

        if (
            exception.get("estructura_id")
            is not None
            and exception["estructura_id"]
            not in structure_ids
        ):
            continue

        return exception

    return None


def resolve_effective_rule(
    *,
    rule_code,
    property_id,
    actor_id,
    effective_date=None,
    space_id=None,
):
    effective_date = (
        effective_date
        or date.today()
    )

    if not isinstance(
        effective_date,
        date,
    ):
        raise ValueError(
            "INVALID_FINANCIAL_RULE_DATE"
        )

    _require_governance_read(
        actor_id,
        property_id,
    )

    context = _context(
        property_id,
        space_id=space_id,
    )

    definition = fetch_one(
        """
        SELECT *
        FROM financial_rule_definitions
        WHERE codigo=%s
          AND activo=TRUE
        """,
        (rule_code,),
    )

    if not definition:
        return {
            "found": False,
            "rule_code": rule_code,
            "effective_date": effective_date,
            "context": context,
            "reason": (
                "RULE_DEFINITION_NOT_FOUND"
            ),
            "candidates": [],
        }

    definition = dict(definition)

    applicability = _definition_applicable(
        definition["id"],
        context["dimensions"],
    )

    if not applicability["allowed"]:
        return {
            "found": False,
            "rule_code": rule_code,
            "effective_date": effective_date,
            "definition": definition,
            "context": context,
            "applicability": applicability,
            "reason": (
                "RULE_DEFINITION_NOT_APPLICABLE"
            ),
            "candidates": [],
        }

    candidates = _approved_candidates(
        definition,
        context,
        effective_date,
    )

    eligible = [
        candidate
        for candidate in candidates
        if candidate["eligible"]
    ]

    eligible.sort(
        key=lambda row: (
            row["scope_rank"],
            row["prioridad"],
            row["version_num"],
            row["version_id"],
        ),
        reverse=True,
    )

    if not eligible:
        return {
            "found": False,
            "rule_code": rule_code,
            "effective_date": effective_date,
            "definition": definition,
            "context": context,
            "applicability": applicability,
            "reason": (
                "NO_APPROVED_EFFECTIVE_RULE"
            ),
            "candidates": candidates,
        }

    selected = eligible[0]

    exception = None

    if definition["admite_excepcion"]:
        exception = _approved_exception(
            selected["version_id"],
            context,
            effective_date,
        )

    parameters = dict(
        selected.get("parametros")
        or {}
    )

    if exception:
        parameters.update(
            exception.get("parametros")
            or {}
        )

    policy = None
    objective = None

    if selected.get("policy_id"):
        policy = fetch_one(
            """
            SELECT *
            FROM financial_policies
            WHERE id=%s
            """,
            (selected["policy_id"],),
        )

        if policy:
            policy = dict(policy)

            if policy.get("objective_id"):
                objective = fetch_one(
                    """
                    SELECT *
                    FROM financial_objectives
                    WHERE id=%s
                    """,
                    (
                        policy[
                            "objective_id"
                        ],
                    ),
                )

                objective = (
                    dict(objective)
                    if objective
                    else None
                )

    explanation = {
        "precedence": (
            "CORE > TIPOLOGIA > INMUEBLE > "
            "ESTRUCTURA > ESPACIO > EXCEPCION"
        ),
        "winner_scope": selected[
            "scope_level"
        ],
        "winner_rank": selected[
            "scope_rank"
        ],
        "winner_priority": selected[
            "prioridad"
        ],
        "winner_version": selected[
            "version_num"
        ],
        "exception_applied": bool(
            exception
        ),
        "candidate_count": len(
            candidates
        ),
        "eligible_candidate_count": len(
            eligible
        ),
    }

    return {
        "found": True,
        "rule_code": rule_code,
        "effective_date": effective_date,
        "definition": definition,
        "context": context,
        "applicability": applicability,
        "selected_rule": selected,
        "exception": exception,
        "effective_parameters": parameters,
        "policy": policy,
        "objective": objective,
        "context_kpi": definition[
            "contexto_kpi"
        ],
        "context_ai": definition[
            "contexto_ia"
        ],
        "explanation": explanation,
        "candidates": candidates,
    }


def build_financial_ai_context(
    *,
    property_id,
    actor_id,
    effective_date=None,
    space_id=None,
    rule_codes=None,
):
    effective_date = (
        effective_date
        or date.today()
    )

    if rule_codes is None:
        rows = fetch_all(
            """
            SELECT codigo
            FROM financial_rule_definitions
            WHERE activo=TRUE
              AND contexto_ia=TRUE
            ORDER BY codigo
            """
        )

        rule_codes = [
            row["codigo"]
            for row in rows
        ]

    rules = []

    for rule_code in rule_codes:
        result = resolve_effective_rule(
            rule_code=rule_code,
            property_id=property_id,
            actor_id=actor_id,
            effective_date=effective_date,
            space_id=space_id,
        )

        if (
            result.get("found")
            and result.get("context_ai")
        ):
            rules.append(result)

    return {
        "property_id": property_id,
        "space_id": space_id,
        "effective_date": effective_date,
        "rules": rules,
        "rule_count": len(rules),
        "governance": {
            "ai_may_interpret": True,
            "ai_may_recommend": True,
            "ai_may_modify_rules": False,
            "ai_may_approve_rules": False,
            "ai_may_execute_financial_actions": False,
        },
    }
