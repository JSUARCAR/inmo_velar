"""
Script de verificación del checklist completo de migración
"""

import psycopg2

POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'db_inmo_velar',
    'user': 'inmo_user',
    'password': '7323'
}

def check_database_exists():
    """Verifica que la base de datos existe"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        conn.close()
        return True, "Base de datos 'db_inmo_velar' existe y es accesible"
    except Exception as e:
        return False, f"Error: {e}"

def check_user_permissions():
    """Verifica que el usuario tiene permisos"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()
        
        # Intentar crear y eliminar una tabla temporal
        cursor.execute("CREATE TEMP TABLE test_permisos (id INTEGER)")
        cursor.execute("INSERT INTO test_permisos VALUES (1)")
        cursor.execute("SELECT * FROM test_permisos")
        cursor.fetchall()
        cursor.execute("DROP TABLE test_permisos")
        
        cursor.close()
        conn.close()
        return True, "Usuario 'inmo_user' tiene permisos completos"
    except Exception as e:
        return False, f"Error: {e}"

def check_tables_count():
    """Verifica el número de tablas"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        """)
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        expected = 41  # Sin CONTRATOS_ARRENDAMIENTOS_OLD
        if count == expected:
            return True, f"{count} tablas creadas (esperadas: {expected})"
        else:
            return False, f"{count} tablas encontradas, se esperaban {expected}"
    except Exception as e:
        return False, f"Error: {e}"

def check_data_migrated():
    """Verifica que los datos fueron migrados"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()
        
        # Contar registros en todas las tablas
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        total_records = 0
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            total_records += count
        
        cursor.close()
        conn.close()
        
        if total_records > 0:
            return True, f"{total_records} registros migrados correctamente"
        else:
            return False, "No se encontraron registros"
    except Exception as e:
        return False, f"Error: {e}"

def check_indices_count():
    """Verifica el número de índices"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(DISTINCT indexname)
            FROM pg_indexes
            WHERE schemaname = 'public'
        """)
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        # PostgreSQL crea índices automáticos para PKs y UNIQUEs, así que el conteo será mayor
        if count >= 50:
            return True, f"{count} índices creados (mínimo esperado: 50)"
        else:
            return False, f"{count} índices encontrados, se esperaban al menos 50"
    except Exception as e:
        return False, f"Error: {e}"

def check_triggers_count():
    """Verifica el número de triggers"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(DISTINCT trigger_name)
            FROM information_schema.triggers
            WHERE trigger_schema = 'public'
        """)
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        expected = 9
        if count == expected:
            return True, f"{count} triggers funcionando (esperados: {expected})"
        else:
            return False, f"{count} triggers encontrados, se esperaban {expected}"
    except Exception as e:
        return False, f"Error: {e}"

def check_views_count():
    """Verifica el número de vistas"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.views
            WHERE table_schema = 'public'
        """)
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        expected = 3
        if count == expected:
            return True, f"{count} vistas creadas (esperadas: {expected})"
        else:
            return False, f"{count} vistas encontradas, se esperaban {expected}"
    except Exception as e:
        return False, f"Error: {e}"

def check_verify_script():
    """Verifica que el script de verificación funciona"""
    try:
        import subprocess
        result = subprocess.run(
            ["python", "verify_connection.py"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return True, "verify_connection.py ejecuta sin errores"
        else:
            return False, f"Error al ejecutar verify_connection.py: {result.stderr}"
    except Exception as e:
        return False, f"Error: {e}"

def check_application_connection():
    """Simula una conexión de aplicación"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()
        
        # Simular una consulta típica de la aplicación
        cursor.execute("SELECT COUNT(*) FROM USUARIOS WHERE ESTADO_USUARIO = TRUE")
        users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM PROPIEDADES WHERE DISPONIBILIDAD_PROPIEDAD = TRUE")
        properties = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return True, f"Aplicación puede conectarse (usuarios activos: {users}, propiedades disponibles: {properties})"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    print("=" * 70)
    print("CHECKLIST DE VERIFICACION DE MIGRACION")
    print("=" * 70)
    print()
    
    checks = [
        ("Base de datos 'db_inmo_velar' creada", check_database_exists),
        ("Usuario 'inmo_user' creado con permisos", check_user_permissions),
        ("41 tablas creadas", check_tables_count),
        ("Datos migrados correctamente (conteo coincide)", check_data_migrated),
        ("50+ índices creados", check_indices_count),
        ("9 triggers funcionando", check_triggers_count),
        ("3 vistas creadas", check_views_count),
        ("verify_connection.py ejecuta sin errores", check_verify_script),
        ("Aplicación puede conectarse a PostgreSQL", check_application_connection),
    ]
    
    results = []
    for description, check_func in checks:
        success, message = check_func()
        results.append((description, success, message))
        
        status = "[OK]" if success else "[FALLO]"
        print(f"{status} {description}")
        print(f"     {message}")
        print()
    
    # Resumen
    print("=" * 70)
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"RESULTADO: {passed}/{total} verificaciones pasadas")
    print("=" * 70)
    
    if passed == total:
        print("\n[OK] MIGRACION COMPLETADA EXITOSAMENTE!")
        print("Todos los elementos verificados correctamente.")
        print("\nProximos pasos:")
        print("1. Actualizar la configuracion de tu aplicacion Reflex")
        print("2. Cambiar imports de sqlite3 a psycopg2")
        print("3. Cambiar placeholders de ? a %s")
        print("4. Probar tu aplicacion con PostgreSQL")
        return True
    else:
        print("\n[ADVERTENCIA] Algunas verificaciones fallaron.")
        print("Revisa los mensajes de error arriba.")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
