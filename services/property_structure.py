from core.authorization import require
from core.db import fetch_all, fetch_one, execute

NODE_TYPES = ('CONJUNTO_URBANO','FRACCIONAMIENTO','PRIVADA','EDIFICIO','TORRE','SECCION','ZONA')


def _actor(actor_id):
    user = fetch_one(
        """
        SELECT id,username,nombre,email,rol_global,activo
        FROM usuarios
        WHERE id=%s
        """,
        (actor_id,),
    )

    if not user or not user.get("activo"):
        raise PermissionError("USER_INACTIVE")

    return dict(user)


def _require_actor(actor_id, permission, property_id):
    return require(
        _actor(actor_id),
        permission,
        property_id,
    )


def property_type(property_id):
    row = fetch_one('SELECT tipo_codigo FROM condominios WHERE id=%s', (property_id,))
    return row.get('tipo_codigo') if row else None


def list_nodes(property_id, active_only=False):
    sql = '''SELECT id,condominio_id,parent_id,tipo_codigo,clave,nombre,descripcion,activo,
                    creado_en,actualizado_en
             FROM estructura_inmueble
             WHERE condominio_id=%s'''
    if active_only:
        sql += ' AND activo=TRUE'
    return fetch_all(sql + ' ORDER BY parent_id NULLS FIRST,tipo_codigo,nombre', (property_id,))


def list_privadas(property_id, active_only=False):
    sql = '''SELECT id,condominio_id,parent_id,tipo_codigo,clave,nombre,descripcion,activo
             FROM estructura_inmueble
             WHERE condominio_id=%s AND tipo_codigo='PRIVADA' '''
    if active_only:
        sql += ' AND activo=TRUE'
    return fetch_all(sql + ' ORDER BY nombre', (property_id,))


def list_space_locations(property_id, active_only=True):
    return list_nodes(property_id, active_only=active_only)


def requires_private(property_id):
    return property_type(property_id) == 'FRACCIONAMIENTO'


def get_node(property_id, node_id):
    return fetch_one('SELECT * FROM estructura_inmueble WHERE id=%s AND condominio_id=%s',
                     (node_id, property_id))


def validate_space_structure(property_id, structure_id):
    if structure_id is None:
        return None
    node = get_node(property_id, structure_id)
    if not node or not node.get('activo'):
        raise ValueError('INVALID_STRUCTURE_LOCATION')
    return structure_id


def _validate_parent(property_id, parent_id):
    if parent_id is None:
        return None
    parent = get_node(property_id, parent_id)
    if not parent or not parent.get('activo'):
        raise ValueError('INVALID_STRUCTURE_PARENT')
    return parent_id


def create_node(
    property_id,
    tipo_codigo,
    nombre,
    clave=None,
    parent_id=None,
    descripcion=None,
    actor_id=None,
):
    _require_actor(
        actor_id,
        "ESTRUCTURA_CREAR",
        property_id,
    )

    if tipo_codigo not in NODE_TYPES:
        raise ValueError('INVALID_STRUCTURE_TYPE')
    parent_id = _validate_parent(property_id, parent_id)
    return execute(
        '''INSERT INTO estructura_inmueble
           (condominio_id,parent_id,tipo_codigo,clave,nombre,descripcion)
           VALUES(%s,%s,%s,%s,%s,%s) RETURNING id''',
        (property_id,parent_id,tipo_codigo,clave,nombre,descripcion), returning=True)


def update_node(
    property_id,
    node_id,
    nombre,
    clave=None,
    descripcion=None,
    tipo_codigo=None,
    parent_id=None,
    actor_id=None,
):
    _require_actor(
        actor_id,
        "ESTRUCTURA_MODIFICAR",
        property_id,
    )

    current = get_node(property_id, node_id)
    if not current:
        raise ValueError('INVALID_STRUCTURE_NODE')
    tipo_codigo = tipo_codigo or current['tipo_codigo']
    if tipo_codigo not in NODE_TYPES:
        raise ValueError('INVALID_STRUCTURE_TYPE')
    parent_id = _validate_parent(property_id, parent_id)
    if parent_id == node_id:
        raise ValueError('STRUCTURE_SELF_PARENT')
    execute(
        '''UPDATE estructura_inmueble
           SET nombre=%s,clave=%s,descripcion=%s,tipo_codigo=%s,parent_id=%s,actualizado_en=NOW()
           WHERE id=%s AND condominio_id=%s''',
        (nombre,clave,descripcion,tipo_codigo,parent_id,node_id,property_id))


def set_node_active(
    property_id,
    node_id,
    active,
    actor_id,
):
    permission = (
        "ESTRUCTURA_REACTIVAR"
        if active
        else "ESTRUCTURA_DESACTIVAR"
    )

    _require_actor(
        actor_id,
        permission,
        property_id,
    )

    if not get_node(property_id, node_id):
        raise ValueError("INVALID_STRUCTURE_NODE")

    execute('''UPDATE estructura_inmueble SET activo=%s,actualizado_en=NOW()
               WHERE id=%s AND condominio_id=%s''', (active,node_id,property_id))


def node_path(nodes, node_id):
    by_id = {n['id']: n for n in nodes}
    labels, seen = [], set()
    current = by_id.get(node_id)
    while current and current['id'] not in seen:
        seen.add(current['id'])
        labels.append(current.get('nombre') or str(current['id']))
        current = by_id.get(current.get('parent_id'))
    return ' / '.join(reversed(labels))


def node_dependencies(
    property_id,
    node_id,
    actor_id=None,
):
    if actor_id is not None:
        _require_actor(
            actor_id,
            "ESTRUCTURA_ELIMINAR",
            property_id,
        )

    if not get_node(property_id,node_id):
        return None
    children=fetch_one('SELECT COUNT(*) n FROM estructura_inmueble WHERE condominio_id=%s AND parent_id=%s',(property_id,node_id))
    spaces=fetch_one('SELECT COUNT(*) n FROM espacios WHERE condominio_id=%s AND estructura_id=%s',(property_id,node_id))
    return {'hijos':int(children['n']),'espacios':int(spaces['n'])}


def delete_node(
    property_id,
    node_id,
    actor_id,
):
    _require_actor(
        actor_id,
        "ESTRUCTURA_ELIMINAR",
        property_id,
    )

    deps = node_dependencies(
        property_id,
        node_id,
    )

    if deps is None or sum(deps.values()):
        return False

    execute(
        "DELETE FROM estructura_inmueble "
        "WHERE id=%s AND condominio_id=%s",
        (node_id, property_id),
    )

    return True
