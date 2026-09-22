#!/usr/bin/env python3
"""
CLI de Auditoría y Remediación Integral de Grupos de Pago (V4 - Élite).

Audita la totalidad de contratos ACTIVOS (Mandatos y Arrendamientos) contra la regla
unificada V2 de dominio sobre la fecha efectiva del período vigente.

Modos de ejecución:
- Solo Lectura (default): Genera reporte de discrepancias sin tocar datos.
- Con --commit: Aplica corrección atómica en una única transacción mediante compare-and-set.

Spec: specs/075-fix-grupo-pago-renovacion/
Contracts: specs/075-fix-grupo-pago-renovacion/contracts/cli-remediacion.md
"""

import os
import sys
import csv
import argparse
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Asegurar que el directorio raíz esté en sys.path para importar src
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(ROOT_DIR, ".env"))

from src.dominio.servicios.calculadora_contratos import (  # noqa: E402
    CalculadoraContratos,
)
from src.infraestructura.persistencia.database import db_manager  # noqa: E402

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("RemediacionGruposPagoV4")


def resolver_fecha_efectiva(
    tipo_contrato: str,
    fecha_inicio_contrato: str,
    fecha_inicio_renovacion_propia: Optional[str] = None,
    fecha_inicio_renovacion_arriendo: Optional[str] = None,
) -> str:
    """
    Resuelve la fecha efectiva del período vigente según la regla de dominio (FR-001, R2).

    Reglas:
    1. Si el contrato tiene renovaciones propias -> fecha_inicio_renovacion más reciente.
    2. Si es Mandato sin renovaciones propias y su arriendo activo tiene renovaciones -> hereda
       la fecha_inicio_renovacion más reciente de ese arrendamiento (FR-001, FR-005, R2).
    3. En cualquier otro caso -> fecha_inicio_contrato original.

    Args:
        tipo_contrato: "Mandato" o "Arrendamiento".
        fecha_inicio_contrato: Fecha de inicio original (YYYY-MM-DD).
        fecha_inicio_renovacion_propia: Fecha inicio de la última renovación propia o None.
        fecha_inicio_renovacion_arriendo: Fecha inicio de la última renovación del arriendo o None.

    Returns:
        str: Fecha ISO (YYYY-MM-DD) que actúa como base para grupo y día de pago.
    """
    if fecha_inicio_renovacion_propia and str(fecha_inicio_renovacion_propia).strip():
        return str(fecha_inicio_renovacion_propia).strip()[:10]

    if (
        tipo_contrato == "Mandato"
        and fecha_inicio_renovacion_arriendo
        and str(fecha_inicio_renovacion_arriendo).strip()
    ):
        return str(fecha_inicio_renovacion_arriendo).strip()[:10]

    if fecha_inicio_contrato and str(fecha_inicio_contrato).strip():
        return str(fecha_inicio_contrato).strip()[:10]

    return "2026-01-01"


def evaluar_contrato(
    tipo_contrato: str,
    id_contrato: int,
    id_propiedad: int,
    fecha_inicio_contrato: str,
    grupo_actual: Any,
    dia_pago_actual: Any,
    fecha_inicio_ren_propia: Optional[str] = None,
    fecha_inicio_ren_arriendo: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Evalúa un contrato determinando sus valores esperados y detectando discrepancias.

    Args:
        tipo_contrato: "Mandato" o "Arrendamiento".
        id_contrato: ID del contrato.
        id_propiedad: ID de la propiedad asociada.
        fecha_inicio_contrato: Fecha de inicio original.
        grupo_actual: Valor numérico actual de grupo_operativo (o None).
        dia_pago_actual: Valor actual de fecha_pago (o None).
        fecha_inicio_ren_propia: Última renovación propia (si existe).
        fecha_inicio_ren_arriendo: Última renovación de arriendo asociado (si aplica).

    Returns:
        Dict[str, Any]: Detalle de evaluación con discrepancia y valores esperados.
    """
    fecha_efectiva = resolver_fecha_efectiva(
        tipo_contrato=tipo_contrato,
        fecha_inicio_contrato=fecha_inicio_contrato,
        fecha_inicio_renovacion_propia=fecha_inicio_ren_propia,
        fecha_inicio_renovacion_arriendo=fecha_inicio_ren_arriendo,
    )

    if tipo_contrato == "Mandato":
        grupo_esperado, dia_esperado_int = (
            CalculadoraContratos.calcular_ciclo_pago_mandato(fecha_efectiva)
        )
        dia_pago_esperado = str(dia_esperado_int)
    else:  # Arrendamiento
        grupo_esperado = CalculadoraContratos.calcular_grupo_operativo(fecha_efectiva)
        dia_esperado_int = CalculadoraContratos.calcular_dia_pago_arrendamiento(
            fecha_efectiva
        )
        dia_pago_esperado = str(dia_esperado_int)

    # Sanitizar valores actuales para comparación
    try:
        g_act = int(grupo_actual) if grupo_actual is not None else 0
    except (ValueError, TypeError):
        g_act = 0

    d_act = str(dia_pago_actual).strip() if dia_pago_actual is not None else ""

    discrepancia = (g_act != grupo_esperado) or (d_act != dia_pago_esperado)

    return {
        "tipo": tipo_contrato,
        "id_contrato": id_contrato,
        "id_propiedad": id_propiedad,
        "fecha_efectiva": fecha_efectiva,
        "grupo_actual": g_act,
        "dia_pago_actual": d_act,
        "grupo_esperado": grupo_esperado,
        "dia_pago_esperado": dia_pago_esperado,
        "discrepancia": discrepancia,
        "accion": "Sin cambio",
    }


def auditar_y_remediar_grupos_pago(
    commit: bool = False,
    outputs_dir: str = "outputs",
) -> Dict[str, Any]:
    """
    Orquesta la extracción masiva, cálculo y remediación transaccional con compare-and-set.

    Args:
        commit: True para aplicar cambios en BD; False para solo-lectura.
        outputs_dir: Directorio de destino del reporte CSV.

    Returns:
        Dict[str, Any]: Resumen de la ejecución con totales y código de salida.
    """
    modo_str = "REMEDIACIÓN (--commit)" if commit else "SOLO LECTURA"
    logger.info("Iniciando auditoría de grupos de pago. Modo: %s", modo_str)

    # 1. Verificar conectividad a base de datos
    try:
        with db_manager.obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
    except Exception as ex:
        logger.error("Error crítico de conexión a PostgreSQL: %s", ex)
        return {
            "codigo_salida": 2,
            "error": str(ex),
            "total_evaluados": 0,
            "total_discrepancias": 0,
        }

    # 2. Extracción masiva con resolución determinista de la última renovación (R2/R7)
    sql_mandatos = """
        SELECT 
            cm.ID_CONTRATO_M,
            cm.ID_PROPIEDAD,
            cm.FECHA_INICIO_CONTRATO_M,
            cm.FECHA_PAGO,
            cm.GRUPO_OPERATIVO,
            rm.FECHA_INICIO_RENOVACION AS RENOVACION_PROPIA,
            ra.FECHA_INICIO_RENOVACION AS RENOVACION_ARRIENDO
        FROM CONTRATOS_MANDATOS cm
        LEFT JOIN (
            SELECT ID_CONTRATO_M, FECHA_INICIO_RENOVACION
            FROM (
                SELECT ID_CONTRATO_M, FECHA_INICIO_RENOVACION,
                       ROW_NUMBER() OVER (
                           PARTITION BY ID_CONTRATO_M 
                           ORDER BY NULLIF(FECHA_RENOVACION, '')::date DESC NULLS LAST, ID_RENOVACION DESC
                       ) AS rn
                FROM RENOVACIONES_CONTRATOS
                WHERE ID_CONTRATO_M IS NOT NULL
            ) sub_rm WHERE rn = 1
        ) rm ON cm.ID_CONTRATO_M = rm.ID_CONTRATO_M
        LEFT JOIN (
            SELECT ca.ID_PROPIEDAD, r.FECHA_INICIO_RENOVACION
            FROM CONTRATOS_ARRENDAMIENTOS ca
            JOIN (
                SELECT ID_CONTRATO_A, FECHA_INICIO_RENOVACION,
                       ROW_NUMBER() OVER (
                           PARTITION BY ID_CONTRATO_A 
                           ORDER BY NULLIF(FECHA_RENOVACION, '')::date DESC NULLS LAST, ID_RENOVACION DESC
                       ) AS rn
                FROM RENOVACIONES_CONTRATOS
                WHERE ID_CONTRATO_A IS NOT NULL
            ) r ON ca.ID_CONTRATO_A = r.ID_CONTRATO_A AND r.rn = 1
            WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO'
        ) ra ON cm.ID_PROPIEDAD = ra.ID_PROPIEDAD
        WHERE cm.ESTADO_CONTRATO_M = 'ACTIVO'
        ORDER BY cm.ID_CONTRATO_M ASC
    """

    sql_arriendos = """
        SELECT 
            ca.ID_CONTRATO_A,
            ca.ID_PROPIEDAD,
            ca.FECHA_INICIO_CONTRATO_A,
            ca.FECHA_PAGO,
            ca.GRUPO_OPERATIVO,
            ra.FECHA_INICIO_RENOVACION AS RENOVACION_PROPIA
        FROM CONTRATOS_ARRENDAMIENTOS ca
        LEFT JOIN (
            SELECT ID_CONTRATO_A, FECHA_INICIO_RENOVACION
            FROM (
                SELECT ID_CONTRATO_A, FECHA_INICIO_RENOVACION,
                       ROW_NUMBER() OVER (
                           PARTITION BY ID_CONTRATO_A 
                           ORDER BY NULLIF(FECHA_RENOVACION, '')::date DESC NULLS LAST, ID_RENOVACION DESC
                       ) AS rn
                FROM RENOVACIONES_CONTRATOS
                WHERE ID_CONTRATO_A IS NOT NULL
            ) sub_ra WHERE rn = 1
        ) ra ON ca.ID_CONTRATO_A = ra.ID_CONTRATO_A
        WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO'
        ORDER BY ca.ID_CONTRATO_A ASC
    """

    evaluaciones: List[Dict[str, Any]] = []

    try:
        with db_manager.obtener_conexion() as conn:
            with conn.cursor() as cur:
                # Mandatos
                cur.execute(sql_mandatos)
                filas_m = cur.fetchall()
                for row in filas_m:
                    row_dict = dict(row) if hasattr(row, "keys") else row
                    evaluaciones.append(
                        evaluar_contrato(
                            tipo_contrato="Mandato",
                            id_contrato=(
                                row_dict["id_contrato_m"]
                                if "id_contrato_m" in row_dict
                                else row_dict["ID_CONTRATO_M"]
                            ),
                            id_propiedad=row_dict.get("id_propiedad")
                            or row_dict.get("ID_PROPIEDAD"),
                            fecha_inicio_contrato=row_dict.get(
                                "fecha_inicio_contrato_m"
                            )
                            or row_dict.get("FECHA_INICIO_CONTRATO_M"),
                            grupo_actual=(
                                row_dict.get("grupo_operativo")
                                if "grupo_operativo" in row_dict
                                else row_dict.get("GRUPO_OPERATIVO")
                            ),
                            dia_pago_actual=(
                                row_dict.get("fecha_pago")
                                if "fecha_pago" in row_dict
                                else row_dict.get("FECHA_PAGO")
                            ),
                            fecha_inicio_ren_propia=(
                                row_dict.get("renovacion_propia")
                                if "renovacion_propia" in row_dict
                                else row_dict.get("RENOVACION_PROPIA")
                            ),
                            fecha_inicio_ren_arriendo=(
                                row_dict.get("renovacion_arriendo")
                                if "renovacion_arriendo" in row_dict
                                else row_dict.get("RENOVACION_ARRIENDO")
                            ),
                        )
                    )

                # Arrendamientos
                cur.execute(sql_arriendos)
                filas_a = cur.fetchall()
                for row in filas_a:
                    row_dict = dict(row) if hasattr(row, "keys") else row
                    evaluaciones.append(
                        evaluar_contrato(
                            tipo_contrato="Arrendamiento",
                            id_contrato=(
                                row_dict["id_contrato_a"]
                                if "id_contrato_a" in row_dict
                                else row_dict["ID_CONTRATO_A"]
                            ),
                            id_propiedad=row_dict.get("id_propiedad")
                            or row_dict.get("ID_PROPIEDAD"),
                            fecha_inicio_contrato=row_dict.get(
                                "fecha_inicio_contrato_a"
                            )
                            or row_dict.get("FECHA_INICIO_CONTRATO_A"),
                            grupo_actual=(
                                row_dict.get("grupo_operativo")
                                if "grupo_operativo" in row_dict
                                else row_dict.get("GRUPO_OPERATIVO")
                            ),
                            dia_pago_actual=(
                                row_dict.get("fecha_pago")
                                if "fecha_pago" in row_dict
                                else row_dict.get("FECHA_PAGO")
                            ),
                            fecha_inicio_ren_propia=(
                                row_dict.get("renovacion_propia")
                                if "renovacion_propia" in row_dict
                                else row_dict.get("RENOVACION_PROPIA")
                            ),
                            fecha_inicio_ren_arriendo=None,
                        )
                    )
    except Exception as ex:
        logger.error("Error durante la extracción masiva: %s", ex)
        return {
            "codigo_salida": 1,
            "error": str(ex),
            "total_evaluados": len(evaluaciones),
            "total_discrepancias": 0,
        }

    discrepancias = [e for e in evaluaciones if e["discrepancia"]]
    logger.info(
        "Contratos activos evaluados: %d (Discrepancias encontradas: %d)",
        len(evaluaciones),
        len(discrepancias),
    )

    for d in discrepancias:
        logger.info(
            "[%s %d] fecha_efectiva=%s | grupo: %s -> %s | día: %s -> %s",
            d["tipo"].upper(),
            d["id_contrato"],
            d["fecha_efectiva"],
            d["grupo_actual"],
            d["grupo_esperado"],
            d["dia_pago_actual"],
            d["dia_pago_esperado"],
        )

    # 3. Aplicar remediación si se solicitó --commit (Transacción única + compare-and-set)
    actualizados = 0
    omitidos_concurrencia = 0

    if commit and discrepancias:
        logger.info("Aplicando remediación atómica con compare-and-set...")
        try:
            with db_manager.transaccion():
                with db_manager.obtener_conexion() as conn:
                    with conn.cursor() as cur:
                        for d in discrepancias:
                            if d["tipo"] == "Mandato":
                                sql_upd = """
                                    UPDATE CONTRATOS_MANDATOS
                                    SET GRUPO_OPERATIVO = %s,
                                        FECHA_PAGO = %s,
                                        UPDATED_AT = NOW(),
                                        UPDATED_BY = 'remediacion_v4'
                                    WHERE ID_CONTRATO_M = %s
                                      AND (GRUPO_OPERATIVO = %s OR (GRUPO_OPERATIVO IS NULL AND %s IS NULL))
                                      AND (FECHA_PAGO = %s OR (FECHA_PAGO IS NULL AND %s IS NULL))
                                """
                                cur.execute(
                                    sql_upd,
                                    (
                                        d["grupo_esperado"],
                                        d["dia_pago_esperado"],
                                        d["id_contrato"],
                                        d["grupo_actual"],
                                        d["grupo_actual"],
                                        str(d["dia_pago_actual"]),
                                        str(d["dia_pago_actual"]),
                                    ),
                                )
                            else:  # Arrendamiento
                                sql_upd = """
                                    UPDATE CONTRATOS_ARRENDAMIENTOS
                                    SET GRUPO_OPERATIVO = %s,
                                        FECHA_PAGO = %s,
                                        UPDATED_AT = NOW(),
                                        UPDATED_BY = 'remediacion_v4'
                                    WHERE ID_CONTRATO_A = %s
                                      AND (GRUPO_OPERATIVO = %s OR (GRUPO_OPERATIVO IS NULL AND %s IS NULL))
                                      AND (FECHA_PAGO = %s OR (FECHA_PAGO IS NULL AND %s IS NULL))
                                """
                                cur.execute(
                                    sql_upd,
                                    (
                                        d["grupo_esperado"],
                                        d["dia_pago_esperado"],
                                        d["id_contrato"],
                                        d["grupo_actual"],
                                        d["grupo_actual"],
                                        str(d["dia_pago_actual"]),
                                        str(d["dia_pago_actual"]),
                                    ),
                                )

                            if cur.rowcount > 0:
                                d["accion"] = "Actualizado"
                                actualizados += 1
                            else:
                                d["accion"] = (
                                    "Omitida (modificada durante la remediación)"
                                )
                                omitidos_concurrencia += 1
                                logger.warning(
                                    "Fila modificada concurrentemente: [%s %d] omitida de remediación.",
                                    d["tipo"],
                                    d["id_contrato"],
                                )
            logger.info(
                "Remediación completada: %d actualizados, %d omitidos por concurrencia.",
                actualizados,
                omitidos_concurrencia,
            )
        except Exception as ex:
            logger.error(
                "Error durante la transacción de remediación (rollback aplicado): %s",
                ex,
            )
            return {
                "codigo_salida": 1,
                "error": str(ex),
                "total_evaluados": len(evaluaciones),
                "total_discrepancias": len(discrepancias),
            }
    elif not commit:
        for d in discrepancias:
            d["accion"] = "Sin cambio (dry-run)"
        logger.info(
            "Sin cambios aplicados (dry-run). Ejecute con --commit para aplicar."
        )

    # 4. Generación del reporte CSV
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(outputs_dir, exist_ok=True)
    csv_filename = os.path.join(
        outputs_dir, f"auditoria_grupos_pago_v4_{timestamp_str}.csv"
    )

    try:
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "tipo",
                "id_contrato",
                "id_propiedad",
                "fecha_efectiva",
                "grupo_actual",
                "dia_pago_actual",
                "grupo_esperado",
                "dia_pago_esperado",
                "discrepancia",
                "accion",
                "fecha_reporte",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            fecha_rep = datetime.now().isoformat()
            for item in evaluaciones:
                row_copy = dict(item)
                row_copy["fecha_reporte"] = fecha_rep
                writer.writerow(row_copy)
        logger.info("Reporte exportado exitosamente a: %s", csv_filename)
    except Exception as ex:
        logger.warning("No se pudo escribir el archivo CSV: %s", ex)

    return {
        "codigo_salida": 0,
        "total_evaluados": len(evaluaciones),
        "total_discrepancias": len(discrepancias),
        "actualizados": actualizados,
        "omitidos_concurrencia": omitidos_concurrencia,
        "csv_path": csv_filename,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Auditoría y remediación de grupos de pago para contratos activos (V4)."
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Aplica la remediación en base de datos en una única transacción.",
    )
    parser.add_argument(
        "--outputs-dir",
        default="outputs",
        help="Directorio donde se almacenará el reporte CSV generado (default: outputs/).",
    )
    args = parser.parse_args()

    resultado = auditar_y_remediar_grupos_pago(
        commit=args.commit,
        outputs_dir=args.outputs_dir,
    )

    return resultado.get("codigo_salida", 0)


if __name__ == "__main__":
    sys.exit(main())
