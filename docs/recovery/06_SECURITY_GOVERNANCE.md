# Condo_Smart - Gobierno de Seguridad

Estado: VALIDADO

## Modelo

Identidad
-> Rol
-> Permiso
-> Ámbito
-> Autorización
-> Acción
-> Auditoría

## Root Principal

El Root Principal constituye la máxima autoridad de seguridad.

El sistema debe proteger esta autoridad frente a degradación o revocación no autorizada.

## Root Delegado

Puede disponer de acceso global, pero no puede gobernar la autoridad del Root Principal ni promover por sí mismo nuevos usuarios a Root.

## Administración Local

Los administradores sin privilegios Root operan exclusivamente dentro de los inmuebles correspondientes a sus asignaciones activas.

## Defensa en Profundidad

La seguridad no debe depender únicamente de controles visuales.

Las operaciones sensibles deben estar protegidas por servicios, autorización y, cuando corresponda, restricciones de base de datos.

## Auditoría

Los cambios importantes de privilegios deben quedar trazados.

Los eventos críticos pueden producir alertas independientes del hecho de que la operación haya terminado correctamente.
