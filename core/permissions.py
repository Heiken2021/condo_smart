def allowed(user,key):
 if user.get('rol_global')=='SUPERADMIN':return True
 return key in {'portafolio','dashboard','inmuebles','espacios','personas','usuarios','catalogos','auditoria'}
