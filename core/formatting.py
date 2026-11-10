from decimal import Decimal
CONTEXT={'condominios':{'clave':'Clave','nombre':'Nombre','tipo_codigo':'Tipo De Inmueble','direccion':'Dirección','rfc':'RFC','moneda_base':'Moneda Base','zona_horaria':'Zona Horaria','activo':'Activo'},'espacios':{'nombre':'Espacio','tipo_codigo':'Tipo De Espacio','estado_codigo':'Estado De Ocupación','cuota_base':'Cuota Base','indiviso_pct':'Indiviso %','activo':'Estado'},'usuarios':{'username':'Usuario','nombre':'Nombre','email':'Correo Electrónico','rol_local':'Rol','activo':'Estado'}}
CURRENCY_SYMBOLS={"MXN":"$","USD":"$","EUR":"€","CAD":"$"}
def global_currency():
 from services.system_settings import get_setting
 return str(get_setting("DEFAULT_CURRENCY","MXN") or "MXN").upper()
def money(v,currency=None,symbol=None):
 currency=(currency or global_currency()).upper()
 symbol=symbol or CURRENCY_SYMBOLS.get(currency,currency)
 return f"{symbol}{Decimal(str(v or 0)):,.2f} {currency}"
def labels(entity):return CONTEXT.get(entity,{})
def state(v):return 'Activo' if v else 'Inactivo'
