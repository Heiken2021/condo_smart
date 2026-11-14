from core.db import fetch_all, fetch_one


MANAGEMENT_ROLES = (
    "ADMINISTRADOR",
    "GERENTE",
    "COMITE",
)


def _require_active_user(user):
    if not user or not user.get("id"):
        raise PermissionError("USER_REQUIRED")

    if not user.get("activo"):
        raise PermissionError("USER_INACTIVE")

    return user


def _is_global_root(user):
    return user.get("rol_global") == "SUPERADMIN"


def dashboard_scope(user):
    user = _require_active_user(user)

    if _is_global_root(user):
        authority = user.get("autoridad_root")

        if authority == "PRINCIPAL":
            label = "Root Principal"
        elif authority == "DELEGADO":
            label = "Root Delegado"
        else:
            label = "SuperAdmin"

        return {
            "scope": "GLOBAL",
            "title": "Portafolio Global",
            "role_label": label,
            "description": (
                "Vista ejecutiva de todos los inmuebles registrados "
                "en Condo_Smart."
            ),
        }

    roles = fetch_all(
        """
        SELECT DISTINCT rol_codigo
        FROM usuario_inmuebles
        WHERE usuario_id=%s
          AND activo=TRUE
          AND rol_codigo IN (
              'ADMINISTRADOR',
              'GERENTE',
              'COMITE'
          )
        ORDER BY rol_codigo
        """,
        (user["id"],),
    )

    role_names = [
        row["rol_codigo"]
        for row in roles
    ]

    if not role_names:
        raise PermissionError("ADMINISTRATIVE_SCOPE_REQUIRED")

    return {
        "scope": "ASSIGNED",
        "title": "Mis Inmuebles",
        "role_label": " / ".join(role_names),
        "description": (
            "Vista ejecutiva limitada a los inmuebles "
            "asignados al usuario."
        ),
    }


def property_snapshot(user):
    user = _require_active_user(user)

    select_sql = """
        SELECT
            c.id,
            c.clave,
            c.nombre,
            c.tipo_codigo,
            c.direccion,
            c.activo,
            COUNT(DISTINCT e.id)
                FILTER (WHERE e.activo=TRUE) AS espacios,
            COUNT(DISTINCT e.id)
                FILTER (
                    WHERE e.activo=TRUE
                      AND e.estado_codigo='OCUPADO'
                ) AS ocupados,
            COUNT(DISTINCT e.id)
                FILTER (
                    WHERE e.activo=TRUE
                      AND (
                          e.estado_codigo IS NULL
                          OR e.estado_codigo<>'OCUPADO'
                      )
                ) AS disponibles,
            COUNT(DISTINCT admins.usuario_id)
                FILTER (
                    WHERE admins.activo=TRUE
                      AND admins.rol_codigo IN (
                          'ADMINISTRADOR',
                          'GERENTE',
                          'COMITE'
                      )
                ) AS administradores,
            COALESCE(
                STRING_AGG(
                    DISTINCT own_scope.rol_codigo,
                    ', '
                    ORDER BY own_scope.rol_codigo
                ) FILTER (
                    WHERE own_scope.rol_codigo IS NOT NULL
                ),
                ''
            ) AS roles_usuario
        FROM condominios c
        LEFT JOIN espacios e
          ON e.condominio_id=c.id
        LEFT JOIN usuario_inmuebles admins
          ON admins.condominio_id=c.id
    """

    params = ()

    if _is_global_root(user):
        scope_join = """
            LEFT JOIN usuario_inmuebles own_scope
              ON own_scope.condominio_id=c.id
             AND own_scope.usuario_id=%s
             AND own_scope.activo=TRUE
        """

        params = (user["id"],)

        where_sql = """
            WHERE 1=1
        """

    else:
        scope_join = """
            JOIN usuario_inmuebles own_scope
              ON own_scope.condominio_id=c.id
             AND own_scope.usuario_id=%s
             AND own_scope.activo=TRUE
             AND own_scope.rol_codigo IN (
                 'ADMINISTRADOR',
                 'GERENTE',
                 'COMITE'
             )
        """

        params = (user["id"],)

        where_sql = """
            WHERE 1=1
        """

    group_sql = """
        GROUP BY
            c.id,
            c.clave,
            c.nombre,
            c.tipo_codigo,
            c.direccion,
            c.activo
        ORDER BY
            c.activo DESC,
            c.nombre,
            c.clave
    """

    rows = fetch_all(
        select_sql
        + scope_join
        + where_sql
        + group_sql,
        params,
    )

    result = []

    for row in rows:
        record = dict(row)

        spaces = int(record.get("espacios") or 0)
        occupied = int(record.get("ocupados") or 0)
        available = int(record.get("disponibles") or 0)
        administrators = int(record.get("administradores") or 0)

        occupancy = (
            round((occupied / spaces) * 100, 1)
            if spaces
            else 0.0
        )

        roles = record.get("roles_usuario") or ""

        if _is_global_root(user):
            authority = user.get("autoridad_root")

            if authority == "PRINCIPAL":
                role_label = "ROOT PRINCIPAL"
            elif authority == "DELEGADO":
                role_label = "ROOT DELEGADO"
            else:
                role_label = "SUPERADMIN"
        else:
            role_label = roles or "SIN ROL"

        if not record.get("activo"):
            status = "INACTIVO"
            traffic_light = "🔴"
        elif spaces == 0:
            status = "SIN ESPACIOS"
            traffic_light = "🟡"
        else:
            status = "ACTIVO"
            traffic_light = "🟢"

        record.update(
            {
                "espacios": spaces,
                "ocupados": occupied,
                "disponibles": available,
                "administradores": administrators,
                "ocupacion_pct": occupancy,
                "rol_usuario": role_label,
                "estado_snapshot": status,
                "semaforo": traffic_light,
            }
        )

        result.append(record)

    return result


def portfolio_totals(rows):
    rows = rows or []

    properties = len(rows)
    active_properties = sum(
        1
        for row in rows
        if row.get("activo")
    )
    inactive_properties = properties - active_properties

    spaces = sum(
        int(row.get("espacios") or 0)
        for row in rows
    )
    occupied = sum(
        int(row.get("ocupados") or 0)
        for row in rows
    )
    available = sum(
        int(row.get("disponibles") or 0)
        for row in rows
    )

    occupancy = (
        round((occupied / spaces) * 100, 1)
        if spaces
        else 0.0
    )

    return {
        "inmuebles": properties,
        "inmuebles_activos": active_properties,
        "inmuebles_inactivos": inactive_properties,
        "espacios": spaces,
        "ocupados": occupied,
        "disponibles": available,
        "ocupacion_pct": occupancy,
    }


def property_type_distribution(rows):
    distribution = {}

    for row in rows or []:
        property_type = (
            row.get("tipo_codigo")
            or "SIN TIPO"
        )

        current = distribution.setdefault(
            property_type,
            {
                "tipo": property_type,
                "inmuebles": 0,
                "espacios": 0,
            },
        )

        current["inmuebles"] += 1
        current["espacios"] += int(
            row.get("espacios") or 0
        )

    return sorted(
        distribution.values(),
        key=lambda item: (
            -item["inmuebles"],
            item["tipo"],
        ),
    )



def management_periods(user):
    user = _require_active_user(user)

    if _is_global_root(user):
        return fetch_all(
            """
            WITH charge_periods AS (
                SELECT
                    periodo,
                    SUM(monto_mxn) AS cargos
                FROM cargos
                WHERE activo=TRUE
                GROUP BY periodo
            ),
            payment_periods AS (
                SELECT
                    periodo,
                    SUM(monto_mxn) AS pagos
                FROM pagos
                WHERE activo=TRUE
                GROUP BY periodo
            ),
            periods AS (
                SELECT periodo FROM charge_periods
                UNION
                SELECT periodo FROM payment_periods
            )
            SELECT
                periods.periodo,
                COALESCE(charge_periods.cargos, 0) AS cargos,
                COALESCE(payment_periods.pagos, 0) AS pagos
            FROM periods
            LEFT JOIN charge_periods
              ON charge_periods.periodo=periods.periodo
            LEFT JOIN payment_periods
              ON payment_periods.periodo=periods.periodo
            ORDER BY periods.periodo
            """
        )

    return fetch_all(
        """
        WITH allowed_properties AS (
            SELECT DISTINCT ui.condominio_id
            FROM usuario_inmuebles ui
            WHERE ui.usuario_id=%s
              AND ui.activo=TRUE
              AND ui.rol_codigo IN (
                  'ADMINISTRADOR',
                  'GERENTE',
                  'COMITE'
              )
        ),
        charge_periods AS (
            SELECT
                c.periodo,
                SUM(c.monto_mxn) AS cargos
            FROM cargos c
            JOIN allowed_properties allowed
              ON allowed.condominio_id=c.condominio_id
            WHERE c.activo=TRUE
            GROUP BY c.periodo
        ),
        payment_periods AS (
            SELECT
                p.periodo,
                SUM(p.monto_mxn) AS pagos
            FROM pagos p
            JOIN allowed_properties allowed
              ON allowed.condominio_id=p.condominio_id
            WHERE p.activo=TRUE
            GROUP BY p.periodo
        ),
        periods AS (
            SELECT periodo FROM charge_periods
            UNION
            SELECT periodo FROM payment_periods
        )
        SELECT
            periods.periodo,
            COALESCE(charge_periods.cargos, 0) AS cargos,
            COALESCE(payment_periods.pagos, 0) AS pagos
        FROM periods
        LEFT JOIN charge_periods
          ON charge_periods.periodo=periods.periodo
        LEFT JOIN payment_periods
          ON payment_periods.periodo=periods.periodo
        ORDER BY periods.periodo
        """,
        (
            user["id"],
        ),
    )
