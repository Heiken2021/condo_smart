def allowed(user,key):
    if key == 'configuracion':
        return user.get('rol_global') == 'SUPERADMIN'
    if user.get('rol_global') == 'SUPERADMIN':
        return True
    return key in {'portafolio','dashboard','inmuebles','espacios','personas','usuarios','finanzas','catalogos','auditoria'}
