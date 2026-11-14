# Condo_Smart - Arquitectura Técnica

Estado: AS-IS VALIDADO A NIVEL GENERAL

## Plataforma

Aplicación:
Python / Streamlit.

Persistencia:
PostgreSQL.

Despliegue:
Railway.

Control de versiones:
Git y repositorio remoto.

## Capas

Interfaz / Views
-> Services
-> Authorization / Security
-> Data Access
-> PostgreSQL

## Capacidades Transversales

- auditoría;
- seguridad;
- configuración;
- observabilidad;
- performance;
- inteligencia artificial.

## Migraciones

La evolución del esquema se realiza mediante migraciones versionadas.

Una migración histórica ya aplicada no debe modificarse de forma que invalide su contrato.

## Calidad

Las pruebas automatizadas constituyen una puerta obligatoria antes de publicar cambios.

Baseline documental actual:

471 pruebas aprobadas.

## Observabilidad

Condo_Smart dispone de telemetría para evaluar rendimiento, consultas, errores y comportamiento por módulo.

## Deuda Técnica

Las APIs de Streamlit marcadas como obsoletas deberán actualizarse progresivamente.

El refinamiento visual avanzado de dashboards queda posterior a la consolidación de datos, transacciones y reglas de negocio.
