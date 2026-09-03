# Data Model: Ingeniería Inversa del Módulo de Propiedad Horizontal

*(Nota: Este documento describe la estructura y objetivos del modelo de datos a extraer durante la auditoría. No define un nuevo modelo, sino los artefactos que deben ser generados).*

## Entidades a Identificar y Auditar

Durante la ejecución de las tareas, se extraerán y documentarán las siguientes entidades y sus características en la base de datos PostgreSQL actual:

1.  **Entidades Core de Propiedad Horizontal**
    *   Propietarios / Residentes
    *   Unidades (Apartamentos, Locales, Casas)
    *   Zonas Comunes
    *   Conceptos de Cobro (Cuotas de administración, extraordinarias)
2.  **Entidades Transaccionales**
    *   Recaudos y Pagos
    *   Liquidaciones y Estados de Cuenta
    *   Incidentes / Peticiones, Quejas y Reclamos (PQRs)
3.  **Relaciones a Documentar**
    *   Relación `Propietario -> Unidad`
    *   Relación `Unidad -> Liquidación`
    *   Relación `Liquidación -> Recaudo`

## Reglas de Validación y Consistencia a Evaluar

*   **Integridad Referencial**: Comprobar si existen claves foráneas estrictas o huérfanos.
*   **Convenciones de Nomenclatura**: Verificar cumplimiento de `snake_case` e idioma (Español).
*   **Tipos Estrictos**: Comprobar el uso de timestamps adecuados, restricciones UNIQUE, y columnas NOT NULL.

## Formato del Modelo Esperado

El resultado de la fase de análisis de Base de Datos deberá producir un Diagrama ER (Entidad-Relación) en formato Mermaid y un diccionario de datos listando las tablas primarias y sus anomalías de diseño detectadas.
