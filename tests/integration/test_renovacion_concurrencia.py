"""
T023 [Transversal]: Concurrencia — supuesto CHK032.

Dos renovaciones concurrentes (o renovación + escrituras en
RECAUDOS/LIQUIDACIONES) sobre el mismo contrato no causan deadlock en
PostgreSQL; la transacción se completa o revierte limpiamente.

Escenarios:
1. Dos renovaciones concurrentes con la misma idempotency_key: una gana el
   lock, la otra espera y obtiene el resultado cached; exactamente 1 fila.
2. Renovación propagando canon mientras otra conexión escribe un RECAUDO del
   mismo contrato: la propagación espera el lock de fila, completa sin
   deadlock (40P01) y el canon se propaga correctamente.
"""

import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import psycopg2
import pytest

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.aplicacion.servicios.servicio_contrato_arrendamiento import (
    ServicioContratoArrendamiento,
)
from src.dominio.entidades.ipc import IPC
from src.infraestructura.persistencia.repositorio_ipc_postgres import (
    RepositorioIPCPostgres,
)
from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
    RepositorioContratoArrendamientoPostgres,
)
from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import (
    RepositorioContratoMandatoPostgres,
)
from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
    RepositorioPropiedadPostgres,
)
from src.infraestructura.persistencia.repositorio_renovacion_postgres import (
    RepositorioRenovacionPostgres,
)
from src.infraestructura.persistencia.repositorio_idempotencia_postgres import (
    RepositorioIdempotenciaPostgres,
)


def _require_db():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        pytest.skip("DATABASE_URL no configurado")
    return DatabaseManager()


def _setup_propiedad(db):
    matricula = f"TEST-T23-{uuid.uuid4().hex[:8]}"
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO MUNICIPIOS (ID_MUNICIPIO, NOMBRE_MUNICIPIO, DEPARTAMENTO, ESTADO_REGISTRO) "
            "VALUES (99996, 'MUN T23', 'DEPTO T23', TRUE) "
            "ON CONFLICT (ID_MUNICIPIO) DO NOTHING"
        )
        conn.commit()
        cursor.execute(
            """INSERT INTO PROPIEDADES (
                MATRICULA_INMOBILIARIA, DIRECCION_PROPIEDAD, ESTADO_REGISTRO,
                ID_MUNICIPIO, TIPO_PROPIEDAD, AREA_M2, ESTRATO,
                DISPONIBILIDAD_PROPIEDAD, CANON_ARRENDAMIENTO_ESTIMADO
            ) VALUES (
                %s, 'Calle T23 Test', TRUE, 99996,
                'Apartamento', 60.0, 3, TRUE, 1000000
            ) RETURNING ID_PROPIEDAD""",
            (matricula,),
        )
        row = cursor.fetchone()
        id_prop = row[0] if isinstance(row, tuple) else row["ID_PROPIEDAD"]
        conn.commit()
    return id_prop


def _setup_arrendatario(db):
    doc = f"DOC-T23-{uuid.uuid4().hex[:8]}"
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO, ESTADO_REGISTRO) "
            "VALUES (%s, 'Test T23 User', TRUE) RETURNING ID_PERSONA",
            (doc,),
        )
        row = cursor.fetchone()
        id_persona = row[0] if isinstance(row, tuple) else row["ID_PERSONA"]
        cursor.execute(
            "INSERT INTO ARRENDATARIOS (ID_PERSONA, ESTADO_ARRENDATARIO) "
            "VALUES (%s, TRUE) RETURNING ID_ARRENDATARIO",
            (id_persona,),
        )
        row2 = cursor.fetchone()
        id_arrendatario = row2[0] if isinstance(row2, tuple) else row2["ID_ARRENDATARIO"]
        conn.commit()
    return id_arrendatario


def _setup_ipc(db, valor_ipc=5.0):
    repo_ipc = RepositorioIPCPostgres(db)
    ipc = IPC(anio=2096, valor_ipc=valor_ipc, fecha_publicacion="2096-01-01")
    try:
        repo_ipc.crear(ipc, "test_t23")
    except Exception:
        pass
    vigente = repo_ipc.obtener_ultimo()
    return vigente.valor_ipc if vigente else 0.0


def _crear_contrato(servicio, db, id_prop, id_arrend, usuario="test_t23"):
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE CONTRATOS_ARRENDAMIENTOS SET ESTADO_CONTRATO_A = 'CANCELADO', "
            "MOTIVO_CANCELACION = 'test t23 reset' WHERE ID_PROPIEDAD = %s "
            "AND ESTADO_CONTRATO_A = 'ACTIVO'",
            (id_prop,),
        )
        conn.commit()
    return servicio.crear_arrendamiento(
        {
            "id_propiedad": id_prop,
            "id_arrendatario": id_arrend,
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-12-31",
            "duracion_meses": 12,
            "canon": 1000000,
            "deposito": 0,
        },
        usuario,
    )


def _servicio_renovacion(db, usuario_id=8):
    servicio = ServicioContratoArrendamiento(
        RepositorioContratoArrendamientoPostgres(db),
        RepositorioPropiedadPostgres(db),
        RepositorioRenovacionPostgres(db),
        RepositorioIPCPostgres(db),
        RepositorioContratoMandatoPostgres(db),
        RepositorioIdempotenciaPostgres(),
    )
    servicio.usuario_id = usuario_id
    return servicio


def _query(db, sql, params):
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return row[0] if isinstance(row, tuple) else next(iter(row.values()))


def test_T023_dos_renovaciones_concurrentes_misma_key_sin_deadlock():
    """CHK032: dos renovaciones concurrentes del mismo contrato con la misma
    idempotency_key — una gana el lock, la otra obtiene el resultado cached;
    sin deadlock y exactamente 1 fila de RENOVACIONES_CONTRATOS."""
    db = _require_db()
    servicio = ServicioContratos(db)
    id_prop = _setup_propiedad(db)
    id_arrend = _setup_arrendatario(db)
    valor_ipc = _setup_ipc(db, valor_ipc=5.0)
    contrato = _crear_contrato(servicio, db, id_prop, id_arrend)

    servicio_renov = _servicio_renovacion(db)
    canon_esperado = int(1000000 * (1 + valor_ipc / 100))

    def renovar():
        return servicio_renov.renovar_arrendamiento(
            contrato.id_contrato_a, "test_t23", "2025-12-31"
        )

    resultados = []
    errores = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futuros = [pool.submit(renovar), pool.submit(renovar)]
        for futuro in futuros:
            try:
                resultados.append(futuro.result(timeout=60))
            except Exception as ex:  # noqa: BLE001
                errores.append(ex)

    # Ninguna excepción (en particular, sin DeadlockDetected / lock timeout)
    assert not errores, f"Errores en renovaciones concurrentes: {errores}"
    assert len(resultados) == 2, f"Ambas renovaciones deben retornar; obtuvo {len(resultados)}"

    n_filas = _query(
        db,
        "SELECT COUNT(*) FROM RENOVACIONES_CONTRATOS WHERE ID_CONTRATO_A = %s",
        (contrato.id_contrato_a,),
    )
    assert n_filas == 1, (
        f"CHK032: exactamente 1 fila tras dos renovaciones concurrentes "
        f"(idempotencia); obtuvo {n_filas}"
    )

    canon_final = _query(
        db,
        "SELECT CANON_ARRENDAMIENTO FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_CONTRATO_A = %s",
        (contrato.id_contrato_a,),
    )
    assert canon_final == canon_esperado, (
        f"Canon esperado {canon_esperado}; obtuvo {canon_final}"
    )


def test_T023_renovacion_y_escritura_recaudo_concurrentes_sin_deadlock():
    """CHK032: la propagación de canon actualiza un RECAUDO del mismo contrato
    mientras otra conexión lo escribe simultáneamente; la transacción espera
    el lock de fila, se completa sin deadlock y la propagación es correcta."""
    db = _require_db()
    servicio = ServicioContratos(db)
    id_prop = _setup_propiedad(db)
    id_arrend = _setup_arrendatario(db)
    valor_ipc = _setup_ipc(db, valor_ipc=5.0)
    contrato = _crear_contrato(servicio, db, id_prop, id_arrend)
    canon_esperado = int(1000000 * (1 + valor_ipc / 100))

    # Recaudo futuro del contrato (sobre el que la propagación escribe)
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO RECAUDOS (
                ID_CONTRATO_A, FECHA_PAGO, VALOR_TOTAL, ESTADO_RECAUDO, REFERENCIA_BANCARIA, METODO_PAGO
            ) VALUES (%s, '2026-12-01', 1000000, 'Pendiente', %s, 'Transferencia') RETURNING ID_RECAUDO""",
            (contrato.id_contrato_a, f"REF-T23-{uuid.uuid4().hex[:8]}"),
        )
        row = cursor.fetchone()
        id_recaudo = row[0] if isinstance(row, tuple) else row["ID_RECAUDO"]
        cursor.execute(
            """INSERT INTO RECAUDO_CONCEPTOS (
                ID_RECAUDO, TIPO_CONCEPTO, PERIODO, VALOR
            ) VALUES (%s, 'Canon', '2026-12', 1000000)""",
            (id_recaudo,),
        )
        conn.commit()

    servicio_renov = _servicio_renovacion(db)

    def escritor_concurrente():
        """Conexión separada: mantiene el lock del recaudo durante 1.5s y luego
        libera (commit), permitiendo que la propagación continúe."""
        with db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE RECAUDOS SET VALOR_TOTAL = VALOR_TOTAL WHERE ID_RECAUDO = %s",
                (id_recaudo,),
            )
            time.sleep(1.5)
            # Salir del context manager hace commit y libera el lock
            conn.commit()

    errores = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futuro_renov = pool.submit(
            servicio_renov.renovar_arrendamiento,
            contrato.id_contrato_a,
            "test_t23",
            "2025-12-31",
        )
        futuro_escritor = pool.submit(escritor_concurrente)
        try:
            resultado = futuro_renov.result(timeout=60)
        except psycopg2.Error as ex:
            sqlstate = getattr(ex, "pgcode", None)
            assert sqlstate != "40P01", f"DeadlockDetected (40P01): {ex}"
            assert sqlstate != "55P03", f"LockNotAvailable (55P03): {ex}"
            errores.append(ex)
        except Exception as ex:  # noqa: BLE001
            errores.append(ex)
        finally:
            try:
                futuro_escritor.result(timeout=60)
            except Exception as ex:  # noqa: BLE001
                errores.append(ex)

    assert not errores, f"Errores en concurrencia: {errores}"

    # El canon se propagó al recaudo futuro (espera el lock y completa)
    valor_recaudo = _query(
        db,
        "SELECT VALOR_TOTAL FROM RECAUDOS WHERE ID_RECAUDO = %s",
        (id_recaudo,),
    )
    assert valor_recaudo == canon_esperado, (
        f"CHK032: recaudo propagado con canon {canon_esperado}; obtuvo {valor_recaudo}"
    )

    canon_final = _query(
        db,
        "SELECT CANON_ARRENDAMIENTO FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_CONTRATO_A = %s",
        (contrato.id_contrato_a,),
    )
    assert canon_final == canon_esperado

    n_renovaciones = _query(
        db,
        "SELECT COUNT(*) FROM RENOVACIONES_CONTRATOS WHERE ID_CONTRATO_A = %s",
        (contrato.id_contrato_a,),
    )
    assert n_renovaciones == 1