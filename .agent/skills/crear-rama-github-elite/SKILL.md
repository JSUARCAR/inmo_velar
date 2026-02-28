---
name: crear-rama-github-elite
description: Crea ramas en Git/GitHub siguiendo convenciones de nomenclatura de élite y mejores prácticas para desarrollo ágil e integración continua. Úsese cuando el usuario pida crear una nueva rama, feature, fix, o empezar a trabajar en algo nuevo.
---

# Creación de Ramas Git Nivel Experto Elite

## Cuándo usar esta skill
- Cuando el usuario solicite crear una nueva rama en el repositorio.
- Al iniciar el desarrollo de una nueva funcionalidad, corrección de errores, o refactorización.
- Cuando se requiera organizar el flujo de trabajo bajo un estándar de nomenclatura profesional.

## Flujo de trabajo
Copie y siga esta lista de verificación para la creación de una rama de élite:

- [ ] **Validar Estado Actual**: Ejecutar `git status` para asegurar que el directorio de trabajo está limpio.
- [ ] **Sincronizar Base**: Cambiar a la rama base (usualmente `main` o `master`) usando `git checkout <base>` y actualizarla con `git pull` para evitar conflictos futuros.
- [ ] **Definir Nomenclatura**: Construir el nombre de la rama siguiendo estrictamente el estándar de élite definido abajo.
- [ ] **Crear la Rama**: Ejecutar `git checkout -b <nombre-de-rama>` para crearla y posicionarse en ella.
- [ ] **Vincular con Remoto (Recomendado)**: Ejecutar `git push -u origin <nombre-de-rama>` para crear el seguimiento remoto desde el inicio.

## Instrucciones

### 1. Estándar de Nomenclatura de Ramas
El nombre de la rama **DEBE** ser autodescriptivo, usar exclusivamente minúsculas y separar las palabras con guiones (`-`). Debe seguir estrictamente este patrón jerárquico:

`<tipo>/[referencia-ticket-opcional]-<breve-descripcion>`

#### Tipos Permitidos (`<tipo>`)
Debe alinearse con las convenciones de Commits (Conventional Commits):
- **feat**: Para nuevas funcionalidades o características.
- **fix**: Para corrección de errores (bugs).
- **hotfix**: Para correcciones críticas urgentes sobre el entorno de producción (`main`/`master`).
- **release**: Para estabilizar y preparar un nuevo lanzamiento.
- **refactor**: Para reestructuración de código que no altera su comportamiento funcional.
- **docs**: Para cambios o creación de documentación.
- **test**: Para adición o modificación de pruebas unitarias o de integración.
- **chore**: Para tareas de mantenimiento, actualización de librerías, configuración, etc.

#### Reglas de Redacción de la Descripción (`<breve-descripcion>`)
1.  **Enfoque Asertivo**: Debe describir la esencia del cambio (ej. `navbar-responsive`, `auth-jwt`, `filtro-fechas`).
2.  **Formato Estricto**: Cero espacios, sin mayúsculas, sin tildes, sin caracteres especiales (ñ, @, !, etc.). Solo letras, números y guiones.
3.  **Contexto Preciso**: Tres a cinco palabras suelen ser el tamaño ideal. Evite nombres demasiado genéricos como `fix/error-pantalla`.

### 2. Ejemplos de Ramas de Élite

*   ✅ `feat/auth-login-jwt`
*   ✅ `fix/TK-124-boton-guardar-inactivo`
*   ✅ `hotfix/caida-pasarela-pagos`
*   ✅ `refactor/modulo-incidentes`
*   ✅ `chore/actualizar-dependencias-npm`
*   ❌ `Feature_Login_Nuevo` (Usa mayúsculas, guiones bajos, no usa barra jerárquica)
*   ❌ `fix-boton` (Falta la barra jerárquica para categorizar y falta contexto)
*   ❌ `mi-nueva-rama` (No proporciona información sobre el tipo de trabajo ni su propósito)

### 3. Buenas Prácticas y Consejos Adicionales
- La rama siempre debe ramificarse desde el último estado estable del repositorio principal (normalmente `main`), a menos que sea una sub-feature de una rama épica mayor.
- Una rama, un propósito. Si mientras desarrolla nota otro error distinto, no lo corrija en esta misma rama; proceda a crear una rama tipo `fix/` dedicada a eso.
