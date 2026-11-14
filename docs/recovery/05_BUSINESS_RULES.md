# Condo_Smart - Registro de Reglas de Negocio

Estado: CONTROLADO V1

## BR-SEC-001 - Aislamiento por inmueble

Estado: VALIDADO.

Un usuario sin privilegios globales únicamente debe acceder a información correspondiente a los inmuebles incluidos en su ámbito autorizado.

## BR-SEC-002 - Root Principal

Estado: VALIDADO.

El Root Principal representa la máxima autoridad de seguridad del sistema.

Su protección no debe depender exclusivamente de la interfaz.

## BR-SEC-003 - Root Delegado

Estado: VALIDADO.

La concesión y revocación de privilegios Root Delegado requieren autoridad del Root Principal.

Un Root Delegado no debe poder gobernar al Root Principal ni conceder por sí mismo nueva autoridad Root.

## BR-AUD-001 - Trazabilidad

Estado: VALIDADO.

Las operaciones relevantes deben permitir identificar la acción, entidad, ejecutor, resultado y trazabilidad correspondiente.

## BR-AUD-002 - Criticidad

Estado: VALIDADO.

Una operación puede finalizar correctamente y ser simultáneamente clasificada como crítica debido a su importancia para la seguridad o el negocio.

## BR-MGT-001 - Mi Gestión

Estado: VALIDADO.

Root dispone de alcance global.

Los perfiles administrativos locales sólo disponen del alcance correspondiente a sus asignaciones vigentes.

## BR-KPI-001 - KPIs gobernados por reglas

Estado: DECISIÓN APROBADA.

Un KPI estratégico no deberá gobernar decisiones hasta que su definición, fuente, fórmula, granularidad y reglas de negocio estén formalizadas.

## BR-AI-001 - IA sobre datos gobernados

Estado: DECISIÓN APROBADA.

Los agentes de IA interpretarán información derivada de datos y reglas controladas.

Los agentes no deben inventar la definición empresarial de un KPI.

## BR-FIN-001 - Sostenibilidad financiera

Estado: DECISIÓN APROBADA.

La sostenibilidad financiera representa la capacidad presente y proyectada del inmueble para generar y recaudar recursos suficientes para cubrir sus necesidades operativas, mantenimiento, servicios, obligaciones y reservas, preservando la continuidad financiera de su operación.

La fórmula compuesta y sus umbrales permanecerán PENDIENTES hasta que el modelo transaccional financiero esté suficientemente consolidado.
