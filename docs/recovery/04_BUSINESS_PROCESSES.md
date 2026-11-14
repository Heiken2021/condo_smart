# Condo_Smart - Procesos de Negocio

Estado: CONTROLADO V1 / EVOLUTIVO

## Proceso General

Organización
-> Inmueble
-> Estructura
-> Espacios
-> Personas
-> Usuarios y responsables
-> Operación
-> Transacciones
-> Auditoría
-> Indicadores
-> Interpretación
-> Optimización.

## BP-001 - Gestión de Inmuebles

Objetivo:
mantener la identidad y estructura administrativa de cada inmueble.

Incluye progresivamente:

- datos generales;
- estructura;
- administradores;
- identidad;
- áreas comunes;
- planos;
- estado.

## BP-002 - Gestión de Estructura

Objetivo:
representar jerárquicamente la organización física o administrativa interna
del inmueble.

La estructura debe mantener coherencia con los espacios dependientes.

## BP-003 - Gestión de Espacios

Objetivo:
administrar las unidades operativas finales del inmueble.

Los espacios constituyen puntos fundamentales de relación con ocupación,
personas y futuras transacciones del negocio.

## BP-004 - Gestión de Personas

Objetivo:
representar personas relacionadas funcionalmente con espacios.

Las relaciones pueden incluir propietario, inquilino u ocupante según las
reglas correspondientes.

## BP-005 - Gestión de Usuarios y Accesos

Objetivo:
controlar quién puede utilizar Condo_Smart y dentro de qué ámbito.

Usuario
-> rol
-> permiso
-> ámbito
-> autorización.

## BP-006 - Administración Multi-Inmueble

Objetivo:
permitir que una misma identidad administrativa gestione uno o múltiples
inmuebles sin perder aislamiento entre ellos.

Mi Gestión proporciona una vista consolidada dentro del ámbito autorizado.

## BP-007 - Gobierno Root

Objetivo:
controlar la administración de privilegios globales.

Root Principal
-> aprobación
-> Root Delegado
-> auditoría
-> alerta crítica cuando corresponda.

## BP-008 - Auditoría

Objetivo:
preservar evidencia explicable de acontecimientos relevantes.

La arquitectura contempla auditoría de sistema y auditoría financiera.

## BP-009 - Gestión Financiera

Estado: EN EVOLUCIÓN.

Objetivo:
representar las transacciones necesarias para comprender ingresos, cobranza,
gastos y posteriormente sostenibilidad financiera.

La madurez del proceso financiero será requisito para formalizar los KPIs
financieros estratégicos.

## BP-010 - Observabilidad y Performance

Objetivo:
medir el comportamiento técnico de Condo_Smart mediante evidencia real.

Telemetría
-> indicadores
-> interpretación
-> recomendación técnica
-> validación posterior.

## BP-011 - Gestión mediante KPIs

Estado: ROADMAP.

Reglas de negocio
-> datos transaccionales
-> KPI
-> objetivo
-> desviación
-> interpretación.

## BP-012 - Agentes Inteligentes

Estado: ROADMAP / PARCIALMENTE IMPLEMENTADO EN PERFORMANCE.

KPI
-> contexto
-> agente
-> evidencia
-> interpretación
-> recomendación
-> autorización
-> acción
-> medición del resultado.

## Principio de Trazabilidad

Cada proceso futuro relevante deberá poder relacionarse con:

Necesidad empresarial
-> Proceso
-> Regla
-> Dato
-> Transacción
-> KPI
-> Decisión
-> Resultado.
