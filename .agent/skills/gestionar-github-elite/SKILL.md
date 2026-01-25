---
name: gestionar-github-elite
description: Gestiona operaciones de control de versiones en GitHub con estándares de élite. Genera commits detallados, técnicos y asertivos exclusivamente en español. Ideal para subir cambios, versionar código y gestionar el repositorio profesionalmente.
---

# Gestión de GitHub Nivel Experto Elite

## Cuándo usar esta skill
- Cuando el usuario pida subir cambios a GitHub.
- Cuando se soliciten commits detallados y profesionales.
- Para operaciones de "git push", "git commit" o "sincronizar repositorio".
- Cuando se requiera un historial de versiones en español técnico y asertivo.

## Flujo de trabajo
Copie y siga esta lista de verificación para cada operación de control de versiones:

- [ ] **Verificar Estado**: Ejecutar `git status` para entender el contexto actual.
- [ ] **Revisar Cambios**: Identificar qué archivos han sido modificados, creados o eliminados.
- [ ] **Preparar el Stage**: Usar `git add` selectivo o `git add .` según corresponda.
- [ ] **Redactar Commit Elite**: Generar un mensaje de commit siguiendo el formato estándar convencional (ver instrucciones).
- [ ] **Confirmar y Subir**: Ejecutar `git commit` y `git push`.
- [ ] **Validar**: Confirmar que los cambios se reflejan en el remoto correctamente.

## Instrucciones

### 1. Estándar de Mensajes de Commit (Conventional Commits)
Todos los mensajes de commit DEBEN seguir estrictamente este formato y estar **100% en ESPAÑOL**:

```
<tipo>(<alcance>): <descripción corta asertiva>

<cuerpo detallado y técnico>

[<pie: referencias a issues o notas de cambios importantes>]
```

#### Tipos Permitidos (`<tipo>`)
- **feat**: Nueva funcionalidad.
- **fix**: Corrección de bugs.
- **docs**: Cambios solo en documentación.
- **style**: Cambios de formato (espacios, puntos y comas) que no afectan el código.
- **refactor**: Cambio de código que no corrige bugs ni añade funcionalidad (limpieza técnica).
- **perf**: Cambios que mejoran el rendimiento.
- **test**: Añadir o corregir tests.
- **chore**: Tareas de mantenimiento, build, herramientas auxiliares.

#### Reglas de Redacción
1.  **Asertividad**: Usa el modo imperativo y presente.
    *   ✅ "Implementa autenticación OAuth"
    *   ❌ "Implementando...", "Se implementó...", "Agregué..."
2.  **Español Técnico**: Usa terminología correcta pero redacta todo en la lengua de Cervantes.
3.  **Detalle Exquisito**: El cuerpo del commit debe explicar **QUÉ** se hizo y **POR QUÉ**, no solo qué archivos cambiaron.
    *   Explica la motivación del cambio.
    *   Describe los efectos secundarios si los hay.
    *   Menciona decisiones de diseño importantes.

### 2. Ejecución de Comandos
- **Seguridad primero**: Nunca hagas `git push -f` (force) a menos que sea explícitamente solicitado y comprendas los riesgos.
- **Atomicidad**: Intenta agrupar cambios relacionados en un solo commit coherente.
- **Verificación**: Usa `git status` antes de cualquier `git add`.

### 3. Ejemplo de Commit Elite

```text
feat(auth): Implementa sistema de login con persistencia JWT

- Integra autenticación vía JSON Web Tokens para manejo de sesiones seguras.
- Refactoriza el middleware de protección de rutas para validar el token en cada petición.
- Añade manejo de errores para tokens expirados y renovaciones automáticas.
- Actualiza la configuración de seguridad en settings.py para definir el tiempo de vida del token.

Este cambio es necesario para reemplazar el sistema de sesiones basado en cookies que presentaba vulnerabilidades CSRF.
```
