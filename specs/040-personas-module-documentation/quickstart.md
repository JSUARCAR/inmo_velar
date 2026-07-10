# Quickstart: Validación del Manual de Usuario

**Date**: 2026-07-08

## Prerequisites

- MkDocs instalado (`pip install mkdocs-material`)
- Acceso al repositorio del proyecto
- Capturas de pantalla realizadas (ver `docs/assets/screenshots/Personas/README.md`)

## Validation Scenarios

### Scenario 1: Renderizado del Manual

**Objective**: Verificar que el manual renderiza correctamente en MkDocs

**Steps**:
1. Navegar al directorio raíz del proyecto
2. Ejecutar: `mkdocs serve`
3. Abrir navegador en `http://127.0.0.1:8000`
4. Navegar a Manual de Usuario → Módulos → Personas

**Expected Outcome**:
- El manual se muestra completo con 16 secciones
- Las imágenes se cargan correctamente
- Los diagramas Mermaid se renderizan
- Las admoniciones (note, warning, tip) se muestran con estilos correctos
- La navegación lateral funciona correctamente

### Scenario 2: Contenido del Manual

**Objective**: Verificar que todas las funcionalidades están documentadas

**Checklist**:
- [ ] Sección 1: Descripción General
- [ ] Sección 2: Acceso al Módulo
- [ ] Sección 3: Interfaz de Usuario
- [ ] Sección 4: Barra de Filtros Avanzados
- [ ] Sección 5: Modos de Visualización
- [ ] Sección 6: Tabla de Datos - Detalles
- [ ] Sección 7: Funcionalidades Principales (CRUD)
- [ ] Sección 8: Paginación
- [ ] Sección 9: Reglas de Negocio
- [ ] Sección 10: Flujo de Trabajo (Mermaid)
- [ ] Sección 11: Ejemplos Prácticos
- [ ] Sección 12: Buenas Prácticas
- [ ] Sección 13: Preguntas Frecuentes (FAQ)
- [ ] Sección 14: Solución de Problemas
- [ ] Sección 15: Glossario
- [ ] Sección 16: Información de Contacto

### Scenario 3: Capturas de Pantalla

**Objective**: Verificar que las imágenes existen y son correctas

**Steps**:
1. Verificar que existen 8-10 archivos PNG en `docs/assets/screenshots/Personas/`
2. Verificar que los nombres coinciden con el README.md
3. Verificar que las imágenes son legibles (resolución mínima 1920x1080)

**Expected Files**:
- `01-vista-general.png`
- `02-kpi-indicadores.png`
- `03-filtros-avanzados.png`
- `04-vista-tabla.png`
- `05-vista-cards.png`
- `06-acciones-fila.png`
- `07-modal-crear-paso2.png` (roles)
- `10-modal-detalles.png`

### Scenario 4: Navegación y Búsqueda

**Objective**: Verificar que la documentación es navegable

**Steps**:
1. Usar la barra de búsqueda de MkDocs
2. Buscar términos clave: "filtro", "crear", "exportar", "KPI"
3. Verificar que los resultados incluyen secciones relevantes

**Expected Outcome**:
- La búsqueda encuentra términos en múltiples secciones
- Los enlaces internos funcionan correctamente
- El índice del manual está completo

## Validation Commands

```bash
# Iniciar servidor de desarrollo
mkdocs serve

# Construir sitio estático
mkdocs build

# Verificar estructura
ls -la docs/manual-usuario/modulos/personas.md
ls -la docs/assets/screenshots/Personas/
```

## Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Renderizado | 100% | Manual completo visible |
| Imágenes | 8-10 | Archivos PNG legibles |
| Búsqueda | Funcional | Términos encontrados |
| Navegación | Funcional | Enlaces correctos |
| Contenido | 16 secciones | Todas documentadas |
