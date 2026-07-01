# Enriquecimiento Reportes Contratos Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enriquecer los reportes de Contratos de Mandato y Arrendamiento mediante consultas SQL especializadas (JOINs) para mostrar nombres y direcciones completas en lugar de solo IDs, desacoplando su lógica del reporteador genérico.

**Architecture:** Se construirán dos métodos nuevos en el `RepositorioReportes` para realizar los cruces en la base de datos (PostgreSQL) garantizando paginación y búsqueda optimizada mediante `ILIKE`. En `ServicioReportes` se interceptarán los `report_id` para enrutarlos a las nuevas funciones.

**Tech Stack:** Python, Reflex, PostgreSQL.

## Global Constraints

- Prohibido modificar el archivo general `presentacion_reflex/...` ya que las tablas son dinámicas y leen de los headers devueltos.
- Evitar mutar in-place diccionarios o listas. 
- Utilizar `COALESCE` en SQL para manejar campos nulos (ej. Codeudores opcionales).
- La cláusula de búsqueda debe usar `ILIKE` en los campos inyectados y `CAST(... AS TEXT)` cuando sea estrictamente necesario.

---

### Task 1: Capa de Infraestructura (Nuevas Consultas SQL)

**Files:**
- Create: `tests/infraestructura/test_repositorio_reportes_contratos.py`
- Modify: `src/infraestructura/persistencia/repositorio_reportes.py`

**Interfaces:**
- Consumes: `_ejecutar_query_paginada` de `RepositorioReportes`.
- Produces: `obtener_reporte_contratos_mandato(self, busqueda, page, limit) -> Tuple[List[Dict[str, Any]], int]`
- Produces: `obtener_reporte_contratos_arrendamiento(self, busqueda, page, limit) -> Tuple[List[Dict[str, Any]], int]`

- [ ] **Step 1: Write the failing tests**

```python
# tests/infraestructura/test_repositorio_reportes_contratos.py
import pytest
from unittest.mock import patch, MagicMock
from src.infraestructura.persistencia.repositorio_reportes import RepositorioReportes

def test_obtener_reporte_contratos_mandato_llama_paginacion():
    repo = RepositorioReportes()
    with patch.object(repo, '_ejecutar_query_paginada', return_value=([], 0)) as mock_ejecutar:
        result = repo.obtener_reporte_contratos_mandato(busqueda="Juan", page=1, limit=20)
        assert mock_ejecutar.called
        args = mock_ejecutar.call_args[0]
        assert "PROPIEDADES" in args[0]
        assert "PROPIETARIOS" in args[0]
        assert result == ([], 0)

def test_obtener_reporte_contratos_arrendamiento_llama_paginacion():
    repo = RepositorioReportes()
    with patch.object(repo, '_ejecutar_query_paginada', return_value=([], 0)) as mock_ejecutar:
        result = repo.obtener_reporte_contratos_arrendamiento(busqueda="Pedro", page=1, limit=20)
        assert mock_ejecutar.called
        args = mock_ejecutar.call_args[0]
        assert "ARRENDATARIOS" in args[0]
        assert "CODEUDORES" in args[0]
        assert result == ([], 0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/infraestructura/test_repositorio_reportes_contratos.py -v`
Expected: FAIL with "AttributeError: 'RepositorioReportes' object has no attribute 'obtener_reporte_contratos_mandato'"

- [ ] **Step 3: Write minimal implementation**

Modify `src/infraestructura/persistencia/repositorio_reportes.py` to add the two new methods inside `RepositorioReportes` class:

```python
    def obtener_reporte_contratos_mandato(
        self, busqueda: Optional[str] = None, page: int = 1, limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        query = """
            SELECT
                cm.ID_CONTRATO_M AS "ID_CONTRATO_M",
                cm.ESTADO_CONTRATO_M AS "ESTADO_CONTRATO_M",
                p.DIRECCION_PROPIEDAD AS "DIRECCION_PROPIEDAD",
                per_prop.NOMBRE_COMPLETO AS "NOMBRE_PROPIETARIO",
                per_ase.NOMBRE_COMPLETO AS "NOMBRE_ASESOR",
                cm.FECHA_INICIO_CONTRATO_M AS "FECHA_INICIO_CONTRATO_M",
                cm.FECHA_FIN_CONTRATO_M AS "FECHA_FIN_CONTRATO_M",
                cm.DURACION_CONTRATO_M AS "DURACION_CONTRATO_M",
                cm.CANON_MANDATO AS "CANON_MANDATO",
                cm.COMISION_PORCENTAJE_CONTRATO_M AS "COMISION_PORCENTAJE_CONTRATO_M",
                cm.ID_PROPIEDAD AS "ID_PROPIEDAD",
                cm.ID_PROPIETARIO AS "ID_PROPIETARIO",
                cm.ID_ASESOR AS "ID_ASESOR"
            FROM CONTRATOS_MANDATOS cm
            INNER JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
            INNER JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
            INNER JOIN PERSONAS per_prop ON prop.ID_PERSONA = per_prop.ID_PERSONA
            INNER JOIN ASESORES a ON cm.ID_ASESOR = a.ID_ASESOR
            INNER JOIN PERSONAS per_ase ON a.ID_PERSONA = per_ase.ID_PERSONA
        """
        conditions = []
        params = []
        if busqueda:
            conditions.append("""(
                p.DIRECCION_PROPIEDAD ILIKE %s OR
                per_prop.NOMBRE_COMPLETO ILIKE %s OR
                per_ase.NOMBRE_COMPLETO ILIKE %s OR
                CAST(cm.ID_CONTRATO_M AS TEXT) ILIKE %s
            )""")
            params.extend([f"%{busqueda}%"] * 4)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY cm.ID_CONTRATO_M DESC"
        return self._ejecutar_query_paginada(query, params, page, limit)

    def obtener_reporte_contratos_arrendamiento(
        self, busqueda: Optional[str] = None, page: int = 1, limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        query = """
            SELECT
                ca.ID_CONTRATO_A AS "ID_CONTRATO_A",
                ca.ESTADO_CONTRATO_A AS "ESTADO_CONTRATO_A",
                p.DIRECCION_PROPIEDAD AS "DIRECCION_PROPIEDAD",
                per_arr.NOMBRE_COMPLETO AS "NOMBRE_ARRENDATARIO",
                COALESCE(arr.NOMBRE_HABITANTE, '') AS "NOMBRE_HABITANTE",
                COALESCE(per_cod.NOMBRE_COMPLETO, 'N/A') AS "NOMBRE_CODEUDOR",
                ca.FECHA_INICIO_CONTRATO_A AS "FECHA_INICIO_CONTRATO_A",
                ca.FECHA_FIN_CONTRATO_A AS "FECHA_FIN_CONTRATO_A",
                ca.DURACION_CONTRATO_A AS "DURACION_CONTRATO_A",
                ca.CANON_ARRENDAMIENTO AS "CANON_ARRENDAMIENTO",
                ca.DEPOSITO AS "DEPOSITO",
                ca.ID_PROPIEDAD AS "ID_PROPIEDAD",
                ca.ID_ARRENDATARIO AS "ID_ARRENDATARIO",
                ca.ID_CODEUDOR AS "ID_CODEUDOR"
            FROM CONTRATOS_ARRENDAMIENTOS ca
            INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            INNER JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
            INNER JOIN PERSONAS per_arr ON arr.ID_PERSONA = per_arr.ID_PERSONA
            LEFT JOIN CODEUDORES cod ON ca.ID_CODEUDOR = cod.ID_CODEUDOR
            LEFT JOIN PERSONAS per_cod ON cod.ID_PERSONA = per_cod.ID_PERSONA
        """
        conditions = []
        params = []
        if busqueda:
            conditions.append("""(
                p.DIRECCION_PROPIEDAD ILIKE %s OR
                per_arr.NOMBRE_COMPLETO ILIKE %s OR
                arr.NOMBRE_HABITANTE ILIKE %s OR
                per_cod.NOMBRE_COMPLETO ILIKE %s OR
                CAST(ca.ID_CONTRATO_A AS TEXT) ILIKE %s
            )""")
            params.extend([f"%{busqueda}%"] * 5)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY ca.ID_CONTRATO_A DESC"
        return self._ejecutar_query_paginada(query, params, page, limit)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/infraestructura/test_repositorio_reportes_contratos.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/infraestructura/test_repositorio_reportes_contratos.py src/infraestructura/persistencia/repositorio_reportes.py
git commit -m "feat(infraestructura): agregar consultas enriquecidas para reportes de contratos"
```

---

### Task 2: Capa de Aplicación (Enrutamiento del Servicio)

**Files:**
- Create: `tests/aplicacion/test_servicio_reportes.py`
- Modify: `src/aplicacion/servicios/servicio_reportes.py`

**Interfaces:**
- Consumes: `obtener_reporte_contratos_mandato` y `obtener_reporte_contratos_arrendamiento` del repositorio.

- [ ] **Step 1: Write the failing tests**

```python
# tests/aplicacion/test_servicio_reportes.py
import pytest
from unittest.mock import MagicMock
from src.aplicacion.servicios.servicio_reportes import ServicioReportes

@pytest.mark.asyncio
async def test_obtener_datos_reporte_mandato_enrutado():
    servicio = ServicioReportes()
    servicio.repo_reportes.obtener_reporte_contratos_mandato = MagicMock(return_value=([{"ID_CONTRATO_M": 1}], 1))
    
    data, headers, total = await servicio.obtener_datos_reporte("contratos_mandato", filtros={"busqueda": "Prueba"})
    
    servicio.repo_reportes.obtener_reporte_contratos_mandato.assert_called_once_with(busqueda="Prueba", page=1, limit=20)
    assert total == 1
    assert data == [{"ID_CONTRATO_M": 1}]
    assert headers == ["ID_CONTRATO_M"]

@pytest.mark.asyncio
async def test_obtener_datos_reporte_arrendamiento_enrutado():
    servicio = ServicioReportes()
    servicio.repo_reportes.obtener_reporte_contratos_arrendamiento = MagicMock(return_value=([{"ID_CONTRATO_A": 1}], 1))
    
    data, headers, total = await servicio.obtener_datos_reporte("contratos_arrendamiento", filtros={"busqueda": "Prueba"})
    
    servicio.repo_reportes.obtener_reporte_contratos_arrendamiento.assert_called_once_with(busqueda="Prueba", page=1, limit=20)
    assert total == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/aplicacion/test_servicio_reportes.py -v`
Expected: FAIL due to the service calling `obtener_reporte_generico` instead of the specific mock.

- [ ] **Step 3: Write minimal implementation**

Modify `src/aplicacion/servicios/servicio_reportes.py` in `obtener_datos_reporte`:

1. Under `table_map = { ... }`, remove `"contratos_mandato": "CONTRATOS_MANDATOS"` and `"contratos_arrendamiento": "CONTRATOS_ARRENDAMIENTOS"`.
2. Add a new block before `# 7. Reportes Genéricos`:

```python
        # 6.5 Reportes Enriquecidos de Contratos
        if report_id == "contratos_mandato":
            data, total = self.repo_reportes.obtener_reporte_contratos_mandato(
                busqueda=busqueda, page=pagina, limit=limite
            )
            headers = self._extraer_headers_seguro(data)
            return data, headers, total

        if report_id == "contratos_arrendamiento":
            data, total = self.repo_reportes.obtener_reporte_contratos_arrendamiento(
                busqueda=busqueda, page=pagina, limit=limite
            )
            headers = self._extraer_headers_seguro(data)
            return data, headers, total
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/aplicacion/test_servicio_reportes.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/aplicacion/test_servicio_reportes.py src/aplicacion/servicios/servicio_reportes.py
git commit -m "feat(aplicacion): enrutar reportes de contratos a consultas especializadas"
```
