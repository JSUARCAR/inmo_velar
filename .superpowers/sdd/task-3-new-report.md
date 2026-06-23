# Task 3: Reporte — Corregir booleanos enteros en PostgreSQL

**Fecha:** 2026-06-23
**Rama:** `feat/desarrollo-experto-elite`
**Estado:** DONE

## 1. Root Cause Analysis

El error `psycopg2.errors.DatatypeMismatch: column "estado_usuario" is of type boolean but expression is of type integer` fue causado por **servicio_configuracion.py linea 126**, donde se instanciaba `Usuario(estado_usuario=1, ...)`.

PostgreSQL rechaza estrictamente enteros en columnas BOOLEAN; SQLite los acepta silenciosamente.

## 2. Archivos Modificados

### src/aplicacion/servicios/servicio_configuracion.py
- estado_usuario=1 -> estado_usuario=True (causa raiz principal)

### src/infraestructura/persistencia/repositorio_usuario.py
- Rama SQLite crear(): `1 if usuario.estado_usuario else 0` -> `bool(usuario.estado_usuario)`
- Metodo actualizar(): `usuario.estado_usuario if self.db.use_postgresql else (1 if ...)` -> `bool(usuario.estado_usuario)`

## 3. Busqueda de Alcance

Se inspeccionaron 34 archivos en src/infraestructura/persistencia/ buscando patrones booleanos enteros.
Resultado: Solo repositorio_usuario.py y servicio_configuracion.py contenian el patron incorrecto.

## 4. Resultados de Tests

pytest tests/integration/test_servicio_configuracion.py -q
  13 passed, 1 warning in 21.04s

pytest tests/integration/ -q --tb=line
  35 passed, 1 warning in 71.15s

Sin regresiones en ningun test de integracion.

## 5. Calidad de Codigo

ruff check  -> All checks passed!
black check -> 2 files would be left unchanged.

## 6. Commit

SHA: d52bd8d
Subject: fix(infra): reemplaza enteros 1/0 por True/False en columnas BOOLEAN de PostgreSQL

Detalle:
- servicio_configuracion.py: estado_usuario=1 -> estado_usuario=True al crear usuario
- repositorio_usuario.py: elimina ternarios 1/0, usa bool() uniforme en ambas ramas DB
- SQLite y PostgreSQL aceptan True/False; enteros son rechazados por psycopg2 en BOOLEAN

## 7. Criterios de Aceptacion

| Criterio | Estado |
|----------|--------|
| pytest test_servicio_configuracion.py -> todos passed | 13/13 PASS |
| Sin regresion en tests de integracion | 35/35 PASS |
| Ruff limpio | PASS |
| Black limpio | PASS |
| Commit en espanol con Conventional Commits | PASS |

## 8. Observaciones

- La entidad Usuario en dominio ya tiene estado_usuario: bool = True (tipado correcto).
- El metodo _to_boolean() del repositorio sigue siendo valido para lectura desde BD.
- No hay otros repositorios con columnas BOOLEAN que usen el patron 1/0 en INSERTs.

## 9. Analisis de Fallos Pre-existentes

Al ejecutar la suite completa: 46 failed, 69 passed, 1 skipped

Los fallos provienen de test_servicio_personas.py y test_servicio_propiedades.py con error:
  sqlite3.OperationalError: near '%': syntax error

Causa: repositorio_persona_postgres.py y repositorio_propiedad_postgres.py usan placeholder '%s'
de PostgreSQL, pero esos tests corren contra SQLite que requiere '?'.

CONFIRMACION: El mismo fallo ocurre con git stash (antes de mis cambios), por lo tanto:
- Son FALLOS PRE-EXISTENTES no causados por esta tarea
- No son regresiones introducidas por Task 3
- Corresponden al scope de Task 1 (placeholders) o una tarea futura

Tests controlados por Task 3 (test_servicio_configuracion.py): 13/13 PASS.
