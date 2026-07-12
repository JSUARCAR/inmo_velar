# Research: Reordenar Columnas Tabla Liquidaciones

**Date**: 2026-07-11

## Decision Log

### D1: Columna "Propiedad" — Eliminar del orden objetivo

**Decision**: La columna "Propiedad" NO aparece en el orden de 16 columnas solicitado por el usuario. Se elimina de la tabla individual.

**Rationale**: El usuario definió explícitamente 16 columnas. "Propiedad" no está en esa lista. La información de propiedad es accesible desde la vista de detalle de cada liquidación.

**Alternatives considered**:
- Mantener "Propiedad" y agregar al final → Rechazado: el usuario especificó 16 columnas exactas
- Mover "Propiedad" a otra posición → Rechazado: no está en el orden solicitado

---

### D2: Tabla Agrupada — Alinear patrón de columnas

**Decision**: La tabla agrupada también se reordena para alinearse con el patrón ingresos → egresos → neto, moviendo "Total IVA Com." después de "Canon Total".

**Rationale**: Consistencia visual entre vista individual y agrupada. El usuario espera el mismo patrón de lectura en ambas vistas.

**Alternatives considered**:
- No modificar tabla agrupada → Rechazado: FR-002 requiere consistencia en "todas las vistas"
- Reordenar completamente la agrupada → Considerado innecesario: solo mover IVA Comisión

---

### D3: Backend — Sin cambios requeridos

**Decision**: No se modifican repositorios, servicios, ni entidades de dominio.

**Rationale**: La reorganización es puramente de presentación. Los `column_id` se mantienen intactos, solo cambia el orden en que se renderizan las celdas.

**Alternatives considered**:
- Agregar campo `display_order` a la entidad → Rechazado: over-engineering para un cambio estático
- Crear configuración de columnas centralizada → Rechazado: fuera de alcance

---

### D4: Exportación — Sin impacto

**Decision**: La exportación PDF/ZIP no se ve afectada.

**Rationale**: Los PDFs se generan con un layout propio (Elite engine) que no depende del orden de columnas de la tabla UI. El orden de datos en el PDF ya está definido en la plantilla.

**Alternatives considered**:
- Ninguna alternativa relevante: la exportación es independiente del orden de tabla

---

### D5: Configuración de columnas por usuario

**Decision**: El nuevo orden se establece como default. Si el usuario tenía configuración personalizada, se respeta.

**Rationale**: Decisión tomada durante `/speckit-clarify`. Evita disruptar usuarios existentes.

**Alternatives considered**:
- Forzar nuevo orden a todos → Ya descartado en clarify
- Resetear todas las configuraciones → Ya descartado en clarify
