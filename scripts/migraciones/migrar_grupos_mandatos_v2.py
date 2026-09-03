"""
Script de migración para recalibrar los grupos operativos y días de pago de
los contratos de mandato (Versión 2.0).
Garantiza atomicidad transaccional y validación previa de discrepancias.
"""

import sys
import argparse
import logging
from typing import List, Dict, Any

from src.infraestructura.persistencia.database import db_manager
from src.dominio.servicios.calculadora_contratos import CalculadoraContratos

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def procesar_mandatos(cursor, mode_commit: bool) -> List[Dict[str, Any]]:
    """Procesa y recalcula el grupo_operativo y fecha_pago de los mandatos activos."""
    logger.info("=== Procesando Contratos de Mandato (Migración V2) ===")

    # Extraer contratos activos
    query_select = """
        SELECT ID_CONTRATO_M, FECHA_INICIO_CONTRATO_M, FECHA_PAGO, GRUPO_OPERATIVO
        FROM CONTRATOS_MANDATOS
        WHERE ESTADO_CONTRATO_M = 'ACTIVO'
    """
    cursor.execute(query_select)
    mandatos = cursor.fetchall()

    if not mandatos:
        logger.info("No se encontraron contratos de mandato activos.")
        return []

    discrepancias = []

    for man in mandatos:
        id_contrato = man["ID_CONTRATO_M"]
        fecha_inicio = man["FECHA_INICIO_CONTRATO_M"]

        fp_actual = (
            int(man["FECHA_PAGO"])
            if man["FECHA_PAGO"] is not None and str(man["FECHA_PAGO"]).isdigit()
            else None
        )
        go_actual = (
            int(man["GRUPO_OPERATIVO"]) if man["GRUPO_OPERATIVO"] is not None else None
        )

        # Calcular valores esperados según V2
        nuevo_grupo, nuevo_dia_pago = CalculadoraContratos.calcular_ciclo_pago_mandato(
            fecha_inicio
        )

        cambios = {}
        if fp_actual != nuevo_dia_pago:
            cambios["fecha_pago"] = (fp_actual, nuevo_dia_pago)

        if go_actual != nuevo_grupo:
            cambios["grupo_operativo"] = (go_actual, nuevo_grupo)

        if cambios:
            discrepancias.append(
                {
                    "id": id_contrato,
                    "cambios": cambios,
                    "nueva_fecha_pago": str(nuevo_dia_pago),
                    "nuevo_grupo": nuevo_grupo,
                }
            )

            str_cambios = ", ".join(
                [f"{k}: {v[0]} -> {v[1]}" for k, v in cambios.items()]
            )
            logger.info(f"[MANDATO {id_contrato}] Discrepancia -> {str_cambios}")

    logger.info(
        f"Total Mandatos Activos: {len(mandatos)} | Con discrepancias: {len(discrepancias)}"
    )

    if mode_commit and discrepancias:
        placeholder = db_manager.get_placeholder()
        query_update = f"""
            UPDATE CONTRATOS_MANDATOS
            SET FECHA_PAGO = {placeholder},
                GRUPO_OPERATIVO = {placeholder}
            WHERE ID_CONTRATO_M = {placeholder}
        """
        updates = [
            (d["nueva_fecha_pago"], d["nuevo_grupo"], d["id"]) for d in discrepancias
        ]
        cursor.executemany(query_update, updates)
        logger.info(
            f"Se actualizaron atomicamente {len(discrepancias)} contratos de mandato."
        )

    return discrepancias


def main():
    parser = argparse.ArgumentParser(
        description="Script para recalibrar los grupos de pago de los Contratos de Mandato."
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Aplica los cambios en la BD transaccionalmente (por defecto es dry-run).",
    )
    args = parser.parse_args()

    mode = (
        "COMMIT (Modificando base de datos)"
        if args.commit
        else "DRY-RUN (Solo lectura)"
    )
    logger.info(f"Iniciando proceso de migracion en modo: {mode}")

    try:
        if args.commit:
            with db_manager.transaccion() as conexion:
                cursor = db_manager.get_dict_cursor(conexion)
                procesar_mandatos(cursor, mode_commit=True)
            logger.info(
                "=== Ejecucion Completada. Transaccion confirmada (COMMIT). ==="
            )
        else:
            conexion = db_manager.obtener_conexion()
            cursor = db_manager.get_dict_cursor(conexion)
            procesar_mandatos(cursor, mode_commit=False)
            logger.info(
                "=== Ejecucion en modo Dry-Run finalizada. No se altero la base de datos. ==="
            )

    except Exception as e:
        logger.error(f"Error crítico durante el proceso: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
