# Quickstart: Validación de la Auditoría

Este documento provee instrucciones sobre cómo validar que el informe final de Ingeniería Inversa cumple con los requerimientos.

## Criterios de Aceptación del Entregable

Para validar el resultado de esta feature, el revisor debe leer el documento maestro de auditoría generado (típicamente `AUDIT_REPORT.md` o similar en la raíz de documentación de este feature).

### Lista de Verificación de Lectura

1.  **¿Existe un Resumen Ejecutivo?**
    *   Verificar que al principio del documento haya una visión global del estado del módulo.
2.  **¿Están mapeados los flujos funcionales?**
    *   Debe existir una descripción del ciclo de vida de los registros principales (por ejemplo, el ciclo de una liquidación o recaudo en Propiedad Horizontal).
3.  **¿Se presenta un inventario funcional con estados?**
    *   Buscar una tabla que clasifique las funciones en operativas, obsoletas, etc.
4.  **¿Se cubrió la arquitectura técnica?**
    *   Comprobar si se hace mención al frontend (Reflex), backend (Python) y base de datos.
5.  **¿Existe un catálogo de Deuda Técnica y Riesgos?**
    *   Verificar matrices que califiquen los riesgos por criticidad (Crítico, Alto, Medio, Bajo).
6.  **¿Hay un Plan de Evolución accionable?**
    *   Revisar si existen pasos sugeridos a corto (bugs/seguridad), mediano (refactorizaciones) y largo plazo (nuevas features).

### Validación de Precisión
Dado que esto es una auditoría técnica, la validación de precisión implica abrir un archivo de código al azar referenciado en el reporte (e.g. un `repositorio_xxx.py` o un archivo de UI Reflex) y comprobar que lo que la auditoría afirma sobre él es verídico (por ejemplo, si afirma que hay "consultas N+1", verificar que el código efectivamente las tenga).
