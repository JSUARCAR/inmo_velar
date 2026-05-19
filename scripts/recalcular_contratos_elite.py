#!/usr/bin/env python3
"""
Script de Reparación Integral: Recálculo Masivo de Contratos (Élite)

Este script aplica masivamente la lógica de dominio definida en `CalculadoraContratos`
sobre todos los contratos activos en la base de datos (PostgreSQL/SQLite).
Recalcula:
- duracion_meses (Reglas comerciales 30/360)
- fecha_pago (Día operativo)
- grupo_operativo (Para mandatos)

Es idempotente y utiliza un bloque transaccional seguro (todo o nada).
Por defecto se ejecuta en modo --dry-run (Solo lectura). Para confirmar cambios,
se debe pasar la bandera --commit.
"""

import os
import sys
import argparse
import logging
from typing import List, Dict, Any

# Agregar el directorio raíz al path para poder importar src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.dominio.servicios.calculadora_contratos import CalculadoraContratos
from src.infraestructura.persistencia.database import db_manager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("ReparacionContratos")

def procesar_arrendamientos(cursor, mode_commit: bool) -> List[Dict[str, Any]]:
    """Procesa y recalcula todos los contratos de arrendamiento activos."""
    logger.info("=== Procesando Contratos de Arrendamiento ===")
    
    # 1. Extract
    query_select = """
        SELECT ID_CONTRATO_A, FECHA_INICIO_CONTRATO_A, FECHA_FIN_CONTRATO_A, DURACION_CONTRATO_A, FECHA_PAGO, GRUPO_OPERATIVO
        FROM CONTRATOS_ARRENDAMIENTOS
        WHERE ESTADO_CONTRATO_A = 'Activo'
    """
    cursor.execute(query_select)
    arrendamientos = cursor.fetchall()
    
    if not arrendamientos:
        logger.info("No se encontraron contratos de arrendamiento activos.")
        return []

    discrepancias = []
    
    # 2. Transform & Verify
    for arr in arrendamientos:
        id_contrato = arr["ID_CONTRATO_A"]
        fecha_inicio = arr["FECHA_INICIO_CONTRATO_A"]
        fecha_fin = arr["FECHA_FIN_CONTRATO_A"]
        
        # Valores actuales
        dur_actual = arr["DURACION_CONTRATO_A"]
        # En PostgreSQL los campos pueden venir nulos, manejarlos de forma segura
        fp_actual = int(arr["FECHA_PAGO"]) if arr["FECHA_PAGO"] is not None and str(arr["FECHA_PAGO"]).isdigit() else None
        
        # Calcular nuevos valores (Lógica de Dominio)
        nueva_duracion = CalculadoraContratos.calcular_duracion_meses(fecha_inicio, fecha_fin)
        nuevo_dia_pago = CalculadoraContratos.calcular_ciclo_pago_arrendamiento(fecha_inicio)
        nuevo_grupo = 0 # Arrendamientos no usan grupo, o si lo usan, asimilamos a 0 por defecto.
        
        # Comparar
        cambios = {}
        if dur_actual != nueva_duracion:
            cambios["duracion_meses"] = (dur_actual, nueva_duracion)
            
        if fp_actual != nuevo_dia_pago:
            cambios["fecha_pago"] = (fp_actual, nuevo_dia_pago)
            
        # Arrendamientos también tienen la columna grupo_operativo (por consistencia de persistencia), forzamos 0.
        grupo_actual = arr["GRUPO_OPERATIVO"]
        if grupo_actual is None or int(grupo_actual) != nuevo_grupo:
             cambios["grupo_operativo"] = (grupo_actual, nuevo_grupo)

        if cambios:
            discrepancias.append({
                "id": id_contrato,
                "cambios": cambios,
                "nueva_duracion": nueva_duracion,
                "nueva_fecha_pago": str(nuevo_dia_pago),
                "nuevo_grupo": nuevo_grupo
            })
            
            # Loguear diferencia
            str_cambios = ", ".join([f"{k}: {v[0]} -> {v[1]}" for k, v in cambios.items()])
            logger.info(f"[ARRENDAMIENTO {id_contrato}] Discrepancia -> {str_cambios}")

    logger.info(f"Total Arrendamientos Activos: {len(arrendamientos)} | Con discrepancias: {len(discrepancias)}")
    
    # 3. Load
    if mode_commit and discrepancias:
        placeholder = db_manager.get_placeholder()
        query_update = f"""
            UPDATE CONTRATOS_ARRENDAMIENTOS
            SET DURACION_CONTRATO_A = {placeholder},
                FECHA_PAGO = {placeholder},
                GRUPO_OPERATIVO = {placeholder}
            WHERE ID_CONTRATO_A = {placeholder}
        """
        updates = [(d["nueva_duracion"], d["nueva_fecha_pago"], d["nuevo_grupo"], d["id"]) for d in discrepancias]
        cursor.executemany(query_update, updates)
        logger.info(f"✔ Se actualizaron {len(discrepancias)} contratos de arrendamiento.")
        
    return discrepancias

def procesar_mandatos(cursor, mode_commit: bool) -> List[Dict[str, Any]]:
    """Procesa y recalcula todos los contratos de mandato activos."""
    logger.info("=== Procesando Contratos de Mandato ===")
    
    # 1. Extract
    query_select = """
        SELECT ID_CONTRATO_M, FECHA_INICIO_CONTRATO_M, FECHA_FIN_CONTRATO_M, DURACION_CONTRATO_M, FECHA_PAGO, GRUPO_OPERATIVO
        FROM CONTRATOS_MANDATOS
        WHERE ESTADO_CONTRATO_M = 'Activo'
    """
    cursor.execute(query_select)
    mandatos = cursor.fetchall()
    
    if not mandatos:
        logger.info("No se encontraron contratos de mandato activos.")
        return []

    discrepancias = []
    
    # 2. Transform & Verify
    for man in mandatos:
        id_contrato = man["ID_CONTRATO_M"]
        fecha_inicio = man["FECHA_INICIO_CONTRATO_M"]
        fecha_fin = man["FECHA_FIN_CONTRATO_M"]
        
        dur_actual = man["DURACION_CONTRATO_M"]
        fp_actual = int(man["FECHA_PAGO"]) if man["FECHA_PAGO"] is not None and str(man["FECHA_PAGO"]).isdigit() else None
        go_actual = int(man["GRUPO_OPERATIVO"]) if man["GRUPO_OPERATIVO"] is not None else None
        
        # Calcular nuevos valores
        nueva_duracion = CalculadoraContratos.calcular_duracion_meses(fecha_inicio, fecha_fin)
        nuevo_grupo, nuevo_dia_pago = CalculadoraContratos.calcular_ciclo_pago_mandato(fecha_inicio)
        
        # Comparar
        cambios = {}
        if dur_actual != nueva_duracion:
            cambios["duracion_meses"] = (dur_actual, nueva_duracion)
            
        if fp_actual != nuevo_dia_pago:
            cambios["fecha_pago"] = (fp_actual, nuevo_dia_pago)
            
        if go_actual != nuevo_grupo:
            cambios["grupo_operativo"] = (go_actual, nuevo_grupo)

        if cambios:
            discrepancias.append({
                "id": id_contrato,
                "cambios": cambios,
                "nueva_duracion": nueva_duracion,
                "nueva_fecha_pago": str(nuevo_dia_pago),
                "nuevo_grupo": nuevo_grupo
            })
            
            str_cambios = ", ".join([f"{k}: {v[0]} -> {v[1]}" for k, v in cambios.items()])
            logger.info(f"[MANDATO {id_contrato}] Discrepancia -> {str_cambios}")

    logger.info(f"Total Mandatos Activos: {len(mandatos)} | Con discrepancias: {len(discrepancias)}")
    
    # 3. Load
    if mode_commit and discrepancias:
        placeholder = db_manager.get_placeholder()
        query_update = f"""
            UPDATE CONTRATOS_MANDATOS
            SET DURACION_CONTRATO_M = {placeholder},
                FECHA_PAGO = {placeholder},
                GRUPO_OPERATIVO = {placeholder}
            WHERE ID_CONTRATO_M = {placeholder}
        """
        updates = [(d["nueva_duracion"], d["nueva_fecha_pago"], d["nuevo_grupo"], d["id"]) for d in discrepancias]
        cursor.executemany(query_update, updates)
        logger.info(f"✔ Se actualizaron {len(discrepancias)} contratos de mandato.")
        
    return discrepancias

def main():
    parser = argparse.ArgumentParser(description="Script para recalcular contratos masivamente.")
    parser.add_argument("--commit", action="store_true", help="Aplica los cambios en la base de datos (por defecto es dry-run).")
    args = parser.parse_args()

    mode = "COMMIT (Modificando base de datos)" if args.commit else "DRY-RUN (Solo lectura)"
    logger.info(f"Iniciando proceso de recálculo de contratos en modo: {mode}")
    logger.info(f"Base de datos detectada: {db_manager.db_mode}")

    try:
        if args.commit:
            # En modo commit, abrimos una transacción explícita
            with db_manager.transaccion() as conexion:
                cursor = db_manager.get_dict_cursor(conexion)
                arr_diffs = procesar_arrendamientos(cursor, mode_commit=True)
                man_diffs = procesar_mandatos(cursor, mode_commit=True)
            logger.info("=== ✅ Ejecución Completada. Transacción confirmada (COMMIT). ===")
        else:
            # En modo dry-run, usamos una conexión sin hacer commit
            conexion = db_manager.obtener_conexion()
            cursor = db_manager.get_dict_cursor(conexion)
            arr_diffs = procesar_arrendamientos(cursor, mode_commit=False)
            man_diffs = procesar_mandatos(cursor, mode_commit=False)
            logger.info("=== ⚠️ Ejecución en modo Dry-Run finalizada. No se alteró la base de datos. ===")
            
    except Exception as e:
        logger.error(f"Error crítico durante el proceso: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
