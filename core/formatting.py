from decimal import Decimal
CONTEXT={'condominios':{'clave':'Clave','nombre':'Nombre','tipo_codigo':'Tipo De Inmueble','direccion':'Dirección','rfc':'RFC','moneda_base':'Moneda Base','zona_horaria':'Zona Horaria','activo':'Estado'},'espacios':{'nombre':'Espacio','tipo_codigo':'Tipo De Espacio','estado_codigo':'Estado','cuota_base':'Cuota Base','indiviso_pct':'Indiviso %','activo':'Estado'},'usuarios':{'username':'Usuario','nombre':'Nombre','email':'Correo Electrónico','rol_local':'Rol','activo':'Estado'}}
def money(v,currency='MXN',symbol='$'):return f"{symbol}{Decimal(str(v or 0)):,.2f} {currency}"
def labels(entity):return CONTEXT.get(entity,{})
def state(v):return 'Activo' if v else 'Inactivo'
