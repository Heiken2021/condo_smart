# ADR-002 - Autorización y Ámbito

Estado: VALIDADO

## Contexto
Un usuario puede operar sobre uno o varios inmuebles.

## Decisión
Las operaciones protegidas deben validar autorización y ámbito en la capa de servicios, no únicamente en la interfaz.

## Razón
Evitar acceso fuera del ámbito asignado.

## Consecuencias
Las vistas y dashboards reutilizan el mismo principio de aislamiento.
