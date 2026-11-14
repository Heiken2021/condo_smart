# Condo_Smart - Recuperación Integral del Proyecto

Estado: PROCEDIMIENTO V1

## Objetivo

Recuperar tanto la aplicación como el conocimiento necesario para comprender y continuar Condo_Smart.

## Activos Críticos

### Software

- repositorio Git;
- ramas y tags;
- código fuente;
- dependencias;
- migraciones;
- pruebas.

### Datos

- PostgreSQL;
- backups;
- esquema;
- historial de migraciones.

### Configuración

Debe conservarse un inventario de las variables necesarias para reconstruir los entornos.

Los secretos reales no deben almacenarse dentro del Recovery Pack.

### Conocimiento

- modelo conceptual;
- reglas de negocio;
- ADRs;
- seguridad;
- modelo financiero;
- diccionario de KPIs;
- gobierno de IA;
- arquitectura;
- roadmap;
- diccionario de datos;
- documentación maestra de cada Build.

## Recovery Test

Ante pérdida total del contexto conversacional debe ser posible:

1. identificar el último Build estable;
2. recuperar el código correspondiente;
3. reconstruir dependencias;
4. recuperar PostgreSQL desde un respaldo válido;
5. conocer y aplicar las migraciones correspondientes;
6. reconstruir la configuración;
7. ejecutar la suite de pruebas;
8. comprender el modelo conceptual;
9. identificar las reglas de negocio;
10. entender el modelo de seguridad;
11. distinguir AS-IS de ROADMAP;
12. identificar decisiones arquitectónicas;
13. conocer los pendientes;
14. continuar el desarrollo sin depender de memoria informal.

## Criterio de Recuperación

La recuperación no se considera completa simplemente porque Condo_Smart arranque.

Debe ser posible explicar:

- qué problema resuelve;
- cómo está organizado;
- cómo funciona;
- por qué fue diseñado de esa forma;
- qué reglas gobiernan el negocio;
- qué está validado;
- qué permanece pendiente;
- hacia dónde evoluciona.

## Gobierno

Este Recovery Pack debe revisarse en cada Build estable.
