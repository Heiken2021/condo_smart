# ADR-001 - Jerarquía de Inmuebles

Estado: DECISIÓN APROBADA / IMPLEMENTACIÓN EVOLUTIVA

## Contexto
Condo_Smart necesita representar diferentes configuraciones inmobiliarias.

## Decisión
El inmueble constituye la frontera administrativa principal. Sus subdivisiones se representan mediante una estructura jerárquica y los espacios se relacionan con el nivel correspondiente.

## Razón
Evitar modelos independientes para cada configuración inmobiliaria.

## Consecuencias
La autorización y el aislamiento continúan teniendo al inmueble como ámbito principal.
