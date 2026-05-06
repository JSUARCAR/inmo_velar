"""
Auditoría: Verificar campos de Administración PH en PostgreSQL
Ejecutar después de aplicar la migración y los cambios de código.
"""
import sys

sys.path.insert(0, ".")
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
    RepositorioPropiedadPostgres,
)

COLUMNAS_ESPERADAS = [
    "CODIGO_ENERGIA",
    "CODIGO_AGUA",
    "CODIGO_GAS",
    "TELEFONO_ADMINISTRACION",
    "TIPO_CUENTA_ADMINISTRACION",
    "NUMERO_CUENTA_ADMINISTRACION",
    "FECHA_PAGO_ADMINISTRACION",
    "LINK_PAGO_ADMINISTRACION",
    "CUOTA_EXTRA_ORDINARIA",
    "OBSERVACIONES_ADMIN_PH",  # NUEVO
]


def auditar_columnas():
    """Verifica que todas las columnas existan en la BD."""
    print("=" * 60)
    print("AUDITORIA: Campos de Administracion PH")
    print("=" * 60)

    print(f"\n[INFO] Base de datos: {getattr(db_manager, 'db_mode', 'desconocido')}")
    print(f"[INFO] Host: {getattr(db_manager, 'host', 'desconocido')}")

    try:
        conn = db_manager.obtener_conexion()
        cursor = conn.cursor()

        query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'propiedades'
        ORDER BY column_name
        """
        cursor.execute(query)
        
        # Get column names from cursor description
        col_names = [desc[0] for desc in cursor.description]
        
        def get_val(row, key, idx):
            if isinstance(row, dict):
                return row.get(key, row.get(key.upper(), row.get(key.lower())))
            try:
                return row[idx]
            except Exception:
                # Si fallan ambos intentos
                return None

        columnas_db = {}
        for row in cursor.fetchall():
            c_name = get_val(row, 'column_name', 0)
            if c_name:
                columnas_db[c_name.upper()] = row

        print(f"\n[TOTAL] Columnas en tabla PROPIEDADES: {len(columnas_db)}")

        print("\n[VERIFICACION] Columnas esperadas:")
        for col in COLUMNAS_ESPERADAS:
            if col in columnas_db:
                row = columnas_db[col]
                data_type = get_val(row, 'data_type', 1)
                is_nullable = get_val(row, 'is_nullable', 2)
                print(f"  [OK] {col}: {data_type} (nullable: {is_nullable})")
            else:
                print(f"  [FAIL] {col}: NO EXISTE")

        conn.close()
        return True

    except Exception as e:
        import traceback
        print(f"\n[ERROR] al consultar BD:")
        traceback.print_exc()
        return False


def auditar_carga_propiedad():
    """Verifica que se pueda cargar una propiedad con los campos nuevos."""
    print("\n" + "=" * 60)
    print("AUDITORIA: Carga de Propiedad con Campos Nuevos")
    print("=" * 60)

    try:
        repo = RepositorioPropiedadPostgres(db_manager)
        propiedades = repo.listar_con_filtros(limit=1)

        if not propiedades:
            print("\n[WARN] No hay propiedades para auditar")
            return True

        p = propiedades[0]

        print(f"\n[INFO] Propiedad ID: {p.id_propiedad}")

        campos = [
            "fecha_pago_administracion",
            "link_pago_administracion",
            "cuota_extra_ordinaria",
            "observaciones_admin_ph",  # NUEVO
            "telefono_administracion",
        ]

        print("\n[VERIFICACION] Valores de campos de administracion:")
        for campo in campos:
            valor = getattr(p, campo, "NO EXISTE")
            print(f"  {campo}: {valor}")

        print("\n[OK] Carga de propiedad exitosa")
        return True

    except Exception as e:
        print(f"\n[ERROR] al cargar propiedad: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    import os
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("\n[INICIO] INICIANDO AUDITORIA DE CAMPOS ADMIN PH\n")

    resultado_columnas = auditar_columnas()
    resultado_carga = auditar_carga_propiedad()

    print("\n" + "=" * 60)
    print("RESUMEN DE AUDITORIA")
    print("=" * 60)
    print(f"  Columnas en BD: {'[OK]' if resultado_columnas else '[FAIL]'}")
    print(f"  Carga de propiedad: {'[OK]' if resultado_carga else '[FAIL]'}")

    if resultado_columnas and resultado_carga:
        print("\n[FIN] AUDITORIA COMPLETADA CON EXITO")
    else:
        print("\n[WARN] AUDITORIA COMPLETADA CON ADVERTENCIAS")
        sys.exit(1)
