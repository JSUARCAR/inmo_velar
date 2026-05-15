"""
Script de Auditoría: Comparación de Fechas entre Contratos de Mandato y Arrendamiento.

Compara FECHA_INICIO_CONTRATO_M vs FECHA_INICIO_CONTRATO_A
y FECHA_FIN_CONTRATO_M vs FECHA_FIN_CONTRATO_A para cada propiedad.
"""

import os
import csv
import sys
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

OUTPUT_FILE = "reporte_auditoria_fechas_contratos.csv"


def conectar_bd():
    database_url = os.getenv("DATABASE_URL", "")
    if database_url and database_url.startswith("postgresql"):
        return psycopg2.connect(database_url, sslmode="require")
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        database=os.getenv("DB_NAME", "railway"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        sslmode="require",
    )


def auditar_fechas():
    conn = conectar_bd()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # 1. Mandatos con sus arrendamientos (misma propiedad)
    query_mandato_arriendo = """
        SELECT
            cm.ID_CONTRATO_M,
            cm.ID_PROPIEDAD,
            cm.FECHA_INICIO_CONTRATO_M,
            cm.FECHA_FIN_CONTRATO_M,
            cm.ESTADO_CONTRATO_M,
            ca.ID_CONTRATO_A,
            ca.FECHA_INICIO_CONTRATO_A,
            ca.FECHA_FIN_CONTRATO_A,
            ca.ESTADO_CONTRATO_A,
            p.DIRECCION_PROPIEDAD,
            p.MATRICULA_INMOBILIARIA,
            per_prop.NOMBRE_COMPLETO AS PROPIETARIO,
            per_arr.NOMBRE_COMPLETO AS ARRENDATARIO,
            per_asesor.NOMBRE_COMPLETO AS ASESOR
        FROM CONTRATOS_MANDATOS cm
        JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
        JOIN PERSONAS per_prop ON prop.ID_PERSONA = per_prop.ID_PERSONA
        LEFT JOIN ASESORES am ON cm.ID_ASESOR = am.ID_ASESOR
        LEFT JOIN PERSONAS per_asesor ON am.ID_PERSONA = per_asesor.ID_PERSONA
        LEFT JOIN CONTRATOS_ARRENDAMIENTOS ca ON cm.ID_PROPIEDAD = ca.ID_PROPIEDAD
        LEFT JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
        LEFT JOIN PERSONAS per_arr ON arr.ID_PERSONA = per_arr.ID_PERSONA
        ORDER BY cm.ID_CONTRATO_M, ca.ID_CONTRATO_A
    """

    print("Ejecutando consulta de mandatos con arrendamientos...")
    cursor.execute(query_mandato_arriendo)
    rows = cursor.fetchall()

    # 2. Mandatos SIN ningún arrendamiento
    query_mandato_solo = """
        SELECT
            cm.ID_CONTRATO_M,
            cm.ID_PROPIEDAD,
            cm.FECHA_INICIO_CONTRATO_M,
            cm.FECHA_FIN_CONTRATO_M,
            cm.ESTADO_CONTRATO_M,
            p.DIRECCION_PROPIEDAD,
            p.MATRICULA_INMOBILIARIA,
            per_prop.NOMBRE_COMPLETO AS PROPIETARIO,
            per_asesor.NOMBRE_COMPLETO AS ASESOR
        FROM CONTRATOS_MANDATOS cm
        JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
        JOIN PERSONAS per_prop ON prop.ID_PERSONA = per_prop.ID_PERSONA
        LEFT JOIN ASESORES am ON cm.ID_ASESOR = am.ID_ASESOR
        LEFT JOIN PERSONAS per_asesor ON am.ID_PERSONA = per_asesor.ID_PERSONA
        WHERE NOT EXISTS (
            SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca
            WHERE ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
        )
        ORDER BY cm.ID_CONTRATO_M
    """

    print("Ejecutando consulta de mandatos sin arrendamiento...")
    cursor.execute(query_mandato_solo)
    rows_solo = cursor.fetchall()

    cursor.close()
    conn.close()

    report = []

    for r in rows:
        inicio_m = r["fecha_inicio_contrato_m"]
        fin_m = r["fecha_fin_contrato_m"]
        inicio_a = r["fecha_inicio_contrato_a"]
        fin_a = r["fecha_fin_contrato_a"]

        coincide_inicio = (inicio_m == inicio_a) if (inicio_m and inicio_a) else None
        coincide_fin = (fin_m == fin_a) if (fin_m and fin_a) else None

        if coincide_inicio is True and coincide_fin is True:
            clasificacion = "COINCIDEN"
        elif coincide_inicio is False or coincide_fin is False:
            partes = []
            if coincide_inicio is False:
                partes.append("INICIO_DIFIERE")
            if coincide_fin is False:
                partes.append("FIN_DIFIERE")
            clasificacion = " + ".join(partes)
        else:
            clasificacion = "N/A"

        report.append(
            {
                "ID_CONTRATO_M": r["id_contrato_m"],
                "ID_CONTRATO_A": r["id_contrato_a"],
                "ID_PROPIEDAD": r["id_propiedad"],
                "DIRECCION": r["direccion_propiedad"],
                "MATRICULA": r["matricula_inmobiliaria"],
                "PROPIETARIO": r["propietario"],
                "ARRENDATARIO": r["arrendatario"],
                "ASESOR": r["asesor"],
                "ESTADO_MANDATO": r["estado_contrato_m"],
                "ESTADO_ARRENDAMIENTO": r["estado_contrato_a"],
                "FECHA_INICIO_M": inicio_m,
                "FECHA_FIN_M": fin_m,
                "FECHA_INICIO_A": inicio_a,
                "FECHA_FIN_A": fin_a,
                "COINCIDEN_INICIO": "SI"
                if coincide_inicio is True
                else ("NO" if coincide_inicio is False else "N/A"),
                "COINCIDEN_FIN": "SI"
                if coincide_fin is True
                else ("NO" if coincide_fin is False else "N/A"),
                "CLASIFICACION": clasificacion,
            }
        )

    for r in rows_solo:
        report.append(
            {
                "ID_CONTRATO_M": r["id_contrato_m"],
                "ID_CONTRATO_A": None,
                "ID_PROPIEDAD": r["id_propiedad"],
                "DIRECCION": r["direccion_propiedad"],
                "MATRICULA": r["matricula_inmobiliaria"],
                "PROPIETARIO": r["propietario"],
                "ARRENDATARIO": None,
                "ASESOR": r["asesor"],
                "ESTADO_MANDATO": r["estado_contrato_m"],
                "ESTADO_ARRENDAMIENTO": None,
                "FECHA_INICIO_M": r["fecha_inicio_contrato_m"],
                "FECHA_FIN_M": r["fecha_fin_contrato_m"],
                "FECHA_INICIO_A": None,
                "FECHA_FIN_A": None,
                "COINCIDEN_INICIO": "N/A",
                "COINCIDEN_FIN": "N/A",
                "CLASIFICACION": "SIN_ARRENDAMIENTO",
            }
        )

    # Escribir CSV
    fieldnames = [
        "ID_CONTRATO_M",
        "ID_CONTRATO_A",
        "ID_PROPIEDAD",
        "DIRECCION",
        "MATRICULA",
        "PROPIETARIO",
        "ARRENDATARIO",
        "ASESOR",
        "ESTADO_MANDATO",
        "ESTADO_ARRENDAMIENTO",
        "FECHA_INICIO_M",
        "FECHA_FIN_M",
        "FECHA_INICIO_A",
        "FECHA_FIN_A",
        "COINCIDEN_INICIO",
        "COINCIDEN_FIN",
        "CLASIFICACION",
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report)

    # Resumen
    total = len(report)
    total_con_arriendo = sum(1 for r in report if r["ID_CONTRATO_A"] is not None)
    total_sin_arriendo = sum(
        1 for r in report if r["CLASIFICACION"] == "SIN_ARRENDAMIENTO"
    )
    coinciden = sum(1 for r in report if r["CLASIFICACION"] == "COINCIDEN")
    no_coinciden = sum(
        1
        for r in report
        if r["CLASIFICACION"] != "COINCIDEN"
        and r["CLASIFICACION"] != "SIN_ARRENDAMIENTO"
        and r["CLASIFICACION"] != "N/A"
    )

    print(f"\n{'=' * 70}")
    print(f"  REPORTE DE AUDITORIA - FECHAS CONTRATOS")
    print(f"{'=' * 70}")
    print(f"  Total registros analizados:        {total}")
    print(f"  Mandatos con arrendamiento:         {total_con_arriendo}")
    print(f"  Mandatos SIN arrendamiento:         {total_sin_arriendo}")
    print(f"  Pares con fechas COINCIDENTES:      {coinciden}")
    print(f"  Pares con fechas NO COINCIDENTES:   {no_coinciden}")
    print(f"{'=' * 70}")
    print(f"  Reporte exportado a: {OUTPUT_FILE}")
    print(f"{'=' * 70}\n")

    # Detalle de no coincidencias
    if no_coinciden > 0:
        print("  DETALLE DE NO COINCIDENCIAS:")
        print(
            f"  {'ID_M':>6} | {'ID_A':>6} | {'PROPIEDAD':>6} | {'INICIO_M':>12} | {'INICIO_A':>12} | {'FIN_M':>12} | {'FIN_A':>12} | {'MOTIVO'}"
        )
        print(
            f"  {'-' * 6} | {'-' * 6} | {'-' * 8} | {'-' * 12} | {'-' * 12} | {'-' * 12} | {'-' * 12} | {'-' * 30}"
        )
        for r in report:
            if r["CLASIFICACION"] not in ("COINCIDEN", "SIN_ARRENDAMIENTO", "N/A"):
                inicio_m = r["FECHA_INICIO_M"] or "N/A"
                inicio_a = r["FECHA_INICIO_A"] or "N/A"
                fin_m = r["FECHA_FIN_M"] or "N/A"
                fin_a = r["FECHA_FIN_A"] or "N/A"
                print(
                    f"  {r['ID_CONTRATO_M']:>6} | {r['ID_CONTRATO_A']:>6} | {r['ID_PROPIEDAD']:>8} | {inicio_m:>12} | {inicio_a:>12} | {fin_m:>12} | {fin_a:>12} | {r['CLASIFICACION']}"
                )

    return report


if __name__ == "__main__":
    try:
        auditar_fechas()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
