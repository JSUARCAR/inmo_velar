# ADR 011: Guía de Sincronización Git - Estrategia de Ramas

**Fecha:** 2026-07-04
**Estado:** Activo
**Contexto:** Integración de funcionalidades concurrentes (`feat/generar-paz-salvo-inactivos` hacia `feat/desarrollo-experto-elite`)

## Índice
1. [Recomendación de Estrategia de Integración](#recomendación-de-estrategia-de-integración)
2. [Comparación: Merge vs Rebase](#comparación-merge-vs-rebase)
3. [Comandos Git Paso a Paso](#comandos-git-paso-a-paso)
4. [Identificación y Resolución de Conflictos](#identificación-y-resolución-de-conflictos)
5. [Verificación de Integración](#verificación-de-integración)
6. [Validaciones Post-Integración](#validaciones-post-integración)
7. [Errores Comunes y Mejores Prácticas](#errores-comunes-y-mejores-prácticas)
8. [Flujo de Trabajo Empresarial Recomendado](#flujo-de-trabajo-empresarial-recomendado)

---

## Recomendación de Estrategia de Integración

En un entorno empresarial, si ambas ramas ya han sido enviadas al servidor remoto y están activas, la estrategia obligatoria es el **`merge` explícito**. No debemos alterar el historial de ramas compartidas, asegurando trazabilidad y evitando romper el trabajo de otros desarrolladores que puedan tener copias locales de estas ramas.

## Comparación: Merge vs Rebase

### Merge (Recomendado)
Crea un commit de unión (merge commit) combinando ambos historiales.
- **Ventaja:** Conserva el contexto histórico real, 100% seguro para ramas remotas compartidas.
- **Desventaja:** Puede crear historiales tipo "red de metro" si se abusa.

### Rebase
Reescribe la historia moviendo los commits de la rama actual al final de la rama base.
- **Ventaja:** Historial estrictamente lineal y limpio.
- **Desventaja:** Modifica los hashes de los commits. Si la rama ya fue subida (`push`), requerirá un `push --force`, lo cual es destructivo en ramas colaborativas. *Úsalo solo en ramas estrictamente locales y privadas.*

## Comandos Git Paso a Paso

1. Obtener la información más reciente del servidor:
   ```bash
   git fetch --all --prune
   ```
2. Asegurarte de estar en la rama destino:
   ```bash
   git checkout feat/desarrollo-experto-elite
   ```
3. Actualizar tu rama destino con los últimos cambios remotos:
   ```bash
   git pull origin feat/desarrollo-experto-elite
   ```
4. Actualizar localmente la rama fuente para tener los últimos cambios:
   ```bash
   git fetch origin feat/generar-paz-salvo-inactivos:feat/generar-paz-salvo-inactivos
   ```
5. Ejecutar la integración (Merge):
   ```bash
   git merge feat/generar-paz-salvo-inactivos --no-ff -m "chore(git): merge feat/generar-paz-salvo-inactivos into feat/desarrollo-experto-elite"
   ```
6. Subir los cambios una vez resueltos los conflictos:
   ```bash
   git push origin feat/desarrollo-experto-elite
   ```

## Identificación y Resolución de Conflictos

Si Git detecta colisiones, pausará el merge. Sigue estos pasos para no perder información (Zero Data Loss):
1. Ejecuta `git status`. Los archivos bajo `Unmerged paths` tienen conflictos.
2. Abre los archivos en tu IDE y busca los marcadores:
   ```text
   <<<<<<< HEAD
   (Tus cambios actuales en experto-elite)
   =======
   (Los cambios entrantes de paz-salvo-inactivos)
   >>>>>>> feat/generar-paz-salvo-inactivos
   ```
3. Edita el archivo manteniendo la lógica final correcta y borra los marcadores de Git.
4. Una vez editados, añádelos: `git add <archivo>`.
5. Cierra la operación con `git commit` (sin parámetros, usará el mensaje por defecto).

*Botón de pánico: Si te equivocas, ejecuta `git merge --abort` para cancelar la operación.*

## Verificación de Integración

Para certificar que la rama destino heredó absolutamente todo de la rama origen:
```bash
git log feat/generar-paz-salvo-inactivos ^feat/desarrollo-experto-elite
```
Si el merge fue exitoso y total, este comando **no debe devolver ninguna salida**. Esto significa que no hay commits en la rama origen que falten en la rama destino.

## Validaciones Post-Integración

Previo a hacer el `push`, ejecuta estrictamente:
- **Técnicas (Estáticas):** `check_syntax.py`, `mypy`, `ruff`, `black` y pruebas unitarias (`pytest`).
- **Técnicas (Build):** `DATABASE_URL=sqlite:///test.db reflex export --frontend-only --no-zip` para validar la compilación del frontend.
- **Funcionales (Runtime):** Levanta el servidor en entorno aislado (`reflex run --env dev`) y verifica la navegación de las funciones afectadas.

## Errores Comunes y Mejores Prácticas

- **Errores:**
  - **Context Flooding:** Ejecutar el merge con archivos "sucios" (sin commit o stash).
  - **Force Push (`--force`):** Hacer rebase y forzar la subida en ramas donde otro compañero está trabajando.
  - **Resolución a ciegas:** Aceptar automáticamente cambios (`--strategy-option theirs`) sin inspeccionar el código.
- **Mejores Prácticas:** Commitear con frecuencia usando Conventional Commits, hacer merges pequeños y tener pruebas automatizadas.

## Flujo de Trabajo Empresarial Recomendado

En la industria **no se recomienda fusionar feature branches entre sí** recurrentemente, pues crea acoplamiento y dependencias. 

**Estrategia Élite (Trunk-Based / GitHub Flow):**
Si `feat/desarrollo-experto-elite` depende del código de `feat/generar-paz-salvo-inactivos`, la segunda debería enviarse por un **Pull Request hacia la rama principal (`develop` o `main`)**, validarse y fusionarse allí. Inmediatamente después, `feat/desarrollo-experto-elite` debe actualizarse **desde la rama principal (`git merge develop`)**.

*Justificación:* Mantiene una única fuente de verdad (el tronco principal), asegura la integración continua (CI) aislando funcionalidades, reduce conflictos y garantiza que toda integración pase por controles de calidad antes de usarse como dependencia.
