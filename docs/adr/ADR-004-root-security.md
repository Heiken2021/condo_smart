# ADR-004 - Root Security Governance

Estado: VALIDADO

## Contexto
Se necesita delegar acceso global sin convertir todas las cuentas globales en autoridades equivalentes sobre la seguridad.

## Decisión
Conservar SUPERADMIN como rol global y distinguir Root Principal de Root Delegado.

## Razón
Mantener compatibilidad y controlar la delegación de privilegios.

## Consecuencias
Únicamente el Root Principal gobierna la delegación Root. Las operaciones quedan auditadas y pueden generar alertas críticas.
