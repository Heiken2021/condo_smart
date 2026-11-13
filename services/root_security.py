from core.db import fetch_all, fetch_one, execute


ROOT_PRINCIPAL = "PRINCIPAL"
ROOT_DELEGADO = "DELEGADO"


def _user(user_id):
    return fetch_one(
        """
        SELECT
            id,
            username,
            nombre,
            email,
            rol_global,
            autoridad_root,
            activo,
            root_asignado_por,
            root_asignado_en,
            root_revocado_por,
            root_revocado_en
        FROM usuarios
        WHERE id=%s
        """,
        (user_id,),
    )


def require_root_principal(actor_id):
    actor = _user(actor_id)

    if not actor or not actor.get("activo"):
        raise PermissionError("ROOT_ACTOR_INACTIVE")

    if (
        actor.get("rol_global") != "SUPERADMIN"
        or actor.get("autoridad_root") != ROOT_PRINCIPAL
    ):
        raise PermissionError("ROOT_PRINCIPAL_REQUIRED")

    return dict(actor)


def is_root_principal(user):
    return bool(
        user
        and user.get("activo")
        and user.get("rol_global") == "SUPERADMIN"
        and user.get("autoridad_root") == ROOT_PRINCIPAL
    )


def list_roots(actor_id):
    require_root_principal(actor_id)

    return fetch_all(
        """
        SELECT
            u.id,
            u.username,
            u.nombre,
            u.email,
            u.rol_global,
            u.autoridad_root,
            u.activo,
            u.root_asignado_en,
            concedente.username AS asignado_por_username
        FROM usuarios u
        LEFT JOIN usuarios concedente
          ON concedente.id=u.root_asignado_por
        WHERE u.rol_global='SUPERADMIN'
           OR u.autoridad_root IS NOT NULL
        ORDER BY
            CASE
                WHEN u.autoridad_root='PRINCIPAL' THEN 0
                WHEN u.autoridad_root='DELEGADO' THEN 1
                ELSE 2
            END,
            u.nombre,
            u.username
        """
    )


def list_root_candidates(actor_id):
    require_root_principal(actor_id)

    return fetch_all(
        """
        SELECT id,username,nombre,email,activo
        FROM usuarios
        WHERE activo=TRUE
          AND rol_global='USUARIO'
          AND autoridad_root IS NULL
        ORDER BY nombre,username
        """
    )


def grant_delegated_root(user_id, actor_id):
    require_root_principal(actor_id)

    if user_id == actor_id:
        raise ValueError("ROOT_SELF_PROMOTION_NOT_ALLOWED")

    target = _user(user_id)

    if not target:
        raise ValueError("ROOT_TARGET_NOT_FOUND")

    if not target.get("activo"):
        raise ValueError("ROOT_TARGET_INACTIVE")

    if (
        target.get("rol_global") == "SUPERADMIN"
        or target.get("autoridad_root") is not None
    ):
        raise ValueError("ROOT_TARGET_ALREADY_PRIVILEGED")

    execute(
        """
        UPDATE usuarios
        SET rol_global='SUPERADMIN',
            autoridad_root='DELEGADO',
            root_asignado_por=%s,
            root_asignado_en=NOW(),
            root_revocado_por=NULL,
            root_revocado_en=NULL,
            actualizado_en=NOW()
        WHERE id=%s
          AND activo=TRUE
          AND rol_global='USUARIO'
          AND autoridad_root IS NULL
        """,
        (actor_id, user_id),
    )

    updated = _user(user_id)

    if (
        not updated
        or updated.get("rol_global") != "SUPERADMIN"
        or updated.get("autoridad_root") != ROOT_DELEGADO
    ):
        raise RuntimeError("ROOT_GRANT_FAILED")

    return dict(updated)


def revoke_delegated_root(user_id, actor_id):
    require_root_principal(actor_id)

    if user_id == actor_id:
        raise ValueError("ROOT_PRINCIPAL_PROTECTED")

    target = _user(user_id)

    if not target:
        raise ValueError("ROOT_TARGET_NOT_FOUND")

    if target.get("autoridad_root") == ROOT_PRINCIPAL:
        raise ValueError("ROOT_PRINCIPAL_PROTECTED")

    if (
        target.get("rol_global") != "SUPERADMIN"
        or target.get("autoridad_root") != ROOT_DELEGADO
    ):
        raise ValueError("ROOT_DELEGATE_REQUIRED")

    execute(
        """
        UPDATE usuarios
        SET rol_global='USUARIO',
            autoridad_root=NULL,
            root_revocado_por=%s,
            root_revocado_en=NOW(),
            actualizado_en=NOW()
        WHERE id=%s
          AND rol_global='SUPERADMIN'
          AND autoridad_root='DELEGADO'
        """,
        (actor_id, user_id),
    )

    updated = _user(user_id)

    if (
        not updated
        or updated.get("rol_global") != "USUARIO"
        or updated.get("autoridad_root") is not None
    ):
        raise RuntimeError("ROOT_REVOKE_FAILED")

    return dict(updated)
