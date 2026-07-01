# Progress Ledger — Plan Maestro: Estabilización Dashboard y Suite 86 Fallos
# Plan: docs/superpowers/plans/2026-06-23-estabilizacion-dashboard-y-suite-pruebas.md
# Base commit: ec14ba4

## Tasks

- [x] Task 1: Instalar dependencias faltantes (holidays, python-barcode) — COMPLETA (commit 1656065, 43/43 passing)
- [x] Task 2: Actualizar esquema SQLite en TestDatabaseManager — COMPLETA (commit 01714aa, 11/11 passing)
- [x] Task 3: Corregir booleanos enteros en PostgreSQL — COMPLETA (commit d52bd8d, 13/13 passing). Concern: 46 tests preexistentes con %s vs ? en SQLite (Task 4 los resolverá)
- [ ] Task 4: Resolver obtener_por_matricula — interfaz faltante en repositorio
- [ ] Task 5: Corregir tests de estado Reflex (DashboardBase, integración y Plotly)
- [ ] Task 6: Corregir in_managed_transaction, desocupación y documental
- [ ] Task 7: Corregir Dashboard UI — "0 días" y duplicados remanentes
- [ ] Task 8: Verificación Final Global
Task 1: complete (commits 80a2219..HEAD, review clean)
Task 2: complete (commits 25d6d5e..HEAD, review clean)
