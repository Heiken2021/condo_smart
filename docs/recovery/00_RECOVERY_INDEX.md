# Condo_Smart - Master Recovery Pack

## Propósito

Este Recovery Pack preserva el conocimiento conceptual, funcional, empresarial y técnico necesario para comprender, operar, continuar y reconstruir Condo_Smart ante una pérdida grave de contexto o de conocimiento del proyecto.

El código fuente por sí solo no constituye documentación suficiente para recuperar el producto.

## Principio de recuperación

Un equipo competente, utilizando conjuntamente:

1. este Recovery Pack;
2. el repositorio Git;
3. las migraciones de base de datos;
4. los backups de PostgreSQL;
5. las pruebas automatizadas;
6. la documentación de cada Build;

debe poder determinar:

- qué es Condo_Smart;
- qué problema empresarial resuelve;
- cómo está estructurado conceptualmente;
- cuáles son sus reglas de negocio;
- qué funcionalidades existen realmente;
- cómo funciona su modelo de seguridad;
- cómo se generan e interpretan sus datos;
- qué decisiones arquitectónicas fueron tomadas y por qué;
- qué componentes están implementados;
- qué componentes pertenecen al roadmap;
- cómo restaurar el proyecto y continuar su evolución.

## Estados documentales

Toda capacidad relevante deberá clasificarse como:

- VALIDADO: implementado y comprobado.
- DECISION_APROBADA: decisión adoptada pero no necesariamente completada.
- PENDIENTE: requisito identificado todavía no implementado o no cerrado.
- ROADMAP: capacidad prevista para una fase futura.
- DEPRECADO: decisión o implementación sustituida.

## Estructura

### 01_PRODUCT_VISION.md
Misión, visión, propósito, usuarios objetivo y propuesta de valor.

### 02_BUSINESS_MODEL.md
Problemas empresariales abordados, modelo de servicio, monetización y creación de valor.

### 03_CONCEPTUAL_MODEL.md
Modelo conceptual independiente de la tecnología: organizaciones, inmuebles, estructuras, espacios, personas, usuarios, administración, operación, finanzas, auditoría, KPIs e IA.

### 04_BUSINESS_PROCESSES.md
Procesos operativos y relaciones entre módulos.

### 05_BUSINESS_RULES.md
Registro formal de reglas de negocio.

### 06_SECURITY_GOVERNANCE.md
Roles, permisos, ámbitos, Root Principal, Root Delegado, aislamiento y auditoría.

### 07_FINANCIAL_MODEL.md
Modelo financiero y sostenibilidad financiera del inmueble.

### 08_KPI_DICTIONARY.md
Definición, fórmula, fuente, periodicidad, umbral e interpretación de cada KPI.

### 09_AI_GOVERNANCE.md
Arquitectura y reglas de actuación de agentes inteligentes.

### 10_TECHNICAL_ARCHITECTURE.md
Arquitectura física y lógica del sistema.

### 11_BUILD_STATUS_AND_ROADMAP.md
Estado AS-IS, TO-BE y evolución por Build.

### 12_DISASTER_RECOVERY.md
Procedimiento para restaurar código, datos, arquitectura y conocimiento del producto.

## Modelo de trazabilidad

Necesidad de negocio
  -> Proceso
  -> Regla de negocio
  -> Dato
  -> Transacción
  -> KPI
  -> Interpretación IA
  -> Recomendación
  -> Acción
  -> Resultado
  -> Retroalimentación

## Gobierno documental

Cada Build estable deberá actualizar, cuando corresponda:

- código;
- pruebas;
- migraciones;
- modelo conceptual;
- reglas de negocio;
- decisiones arquitectónicas;
- diccionario de datos;
- KPIs;
- roadmap;
- documentación de recuperación.

Ninguna decisión crítica de Condo_Smart deberá depender exclusivamente de conversaciones o memoria de sus participantes.

## Baseline actual

Build: Build 02
Branch: feature/build-02-b02-1-spaces-foundation
Baseline técnico documentado: 4ddbb2c
Suite validada en checkpoint: 471 pruebas aprobadas.

El inventario técnico detallado se conserva temporalmente en knowledge_reports y se utiliza como evidencia para construir esta documentación curada.
