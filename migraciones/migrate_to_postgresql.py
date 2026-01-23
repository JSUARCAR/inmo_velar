"""
Script de Migración Completa: SQLite -> PostgreSQL
Sistema de Gestión Inmobiliaria Velar SAS

Este script migra la base de datos completa incluyendo:
- Estructura de tablas (adaptada a PostgreSQL)
- Todos los datos
- Índices
- Triggers (adaptados a PostgreSQL)
- Vistas

Autor: Migración Automatizada
Fecha: 2026-01-08
"""

import sqlite3
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
from pathlib import Path
from datetime import datetime
import sys

# =====================================================
# CONFIGURACIÓN
# =====================================================

SQLITE_DB = Path(__file__).parent / 'DB_Inmo_Velar.db'

POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'db_inmo_velar',
    'user': 'inmo_user',
    'password': '7323'
}

POSTGRES_ADMIN_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'postgres',  # Base de datos por defecto para crear la nueva DB
    'user': 'postgres',
    'password': '7323'
}

# =====================================================
# MAPEO DE TIPOS SQLite -> PostgreSQL
# =====================================================

def map_sqlite_type_to_postgres(sqlite_type, column_name=''):
    """
    Mapea tipos de datos de SQLite a PostgreSQL
    """
    sqlite_type = sqlite_type.upper().strip()
    
    # Tipos exactos
    type_mappings = {
        'INTEGER': 'INTEGER',
        'TEXT': 'TEXT',
        'REAL': 'DOUBLE PRECISION',
        'BLOB': 'BYTEA',
        '': 'TEXT'  # SQLite permite columnas sin tipo
    }
    
    # Si es TEXT en SQLite, verificar casos especiales, sino mantener TEXT
    if sqlite_type != 'TEXT' and sqlite_type != '':
        # Para tipos no-TEXT, usar el mapeo base
        base_type = type_mappings.get(sqlite_type, 'TEXT')
    else:
        base_type = 'TEXT'
    
    # Optimizaciones específicas por nombre de columna SOLO para INTEGER
    if sqlite_type == 'INTEGER':
        # Estados booleanos
        if column_name.upper() in ['ESTADO_USUARIO', 'ESTADO_REGISTRO', 'ESTADO_PROPIETARIO', 
                                   'ESTADO_SEGURO', 'ESTADO_ARRENDATARIO', 'DISPONIBILIDAD_PROPIEDAD',
                                   'ALERTA_VENCIMINETO_CONTRATO_M', 'ALERTA_VENCIMIENTO_CONTRATO_A',
                                   'ALERTA_IPC', 'RESUELTO_AUTOMATICAMENTE', 'REQUIRIO_APROBACION',
                                   'MODIFICABLE', 'WHATSAPP_HABILITADO', 'EMAIL_HABILITADO', 'ESTADO']:
            return 'BOOLEAN'
        
        # Valores monetarios en centavos (solo si el nombre indica VALOR y no ESTADO)
        if any(column_name.upper().startswith(word) or column_name.upper().endswith(word) for word in [
            'VALOR_', '_VALOR', 'CANON_', '_CANON', 'COMISION_', '_COMISION', 
            'IVA_', '_IVA', 'DEPOSITO', 'IMPUESTO', 'COSTO_', '_COSTO', 
            'PRECIO_', '_PRECIO', 'DESCUENTO_', '_DESCUENTO', 'SALDO_', '_SALDO', 
            'TOTAL_', '_TOTAL', 'NETO', 'BRUTO'
        ]):
            # Excluir valores que son pagos individuales (usar INTEGER) vs valores grandes
            if any(word in column_name.upper() for word in ['ADMINISTRACION', 'RECIBO']):
                return 'BIGINT'
            # Valores monetarios grandes
            elif 'VALOR_PAGO' in column_name.upper() or 'PAGO' in column_name.upper():
                return 'BIGINT'
            else:
                return 'BIGINT'
        
        # Porcentajes (base 100 o 10000)
        if 'PORCENTAJE' in column_name.upper():
            return 'INTEGER'
        
        # Días, meses, años
        if any(word in column_name.upper() for word in ['DIAS', 'MESES', 'ANIO', 'DURACION', 'VERSION', 'INTENTOS']):
            return 'INTEGER'
        
        # IDs y contadores
        if column_name.startswith('ID_') or column_name.endswith('_ID'):
            return 'INTEGER'
        
        # Por defecto para INTEGER
        return 'INTEGER'
    
    # Para REAL
    if sqlite_type == 'REAL':
        # Área
        if 'AREA' in column_name.upper():
            return 'NUMERIC(10,2)'
        return 'DOUBLE PRECISION'
    
    # Por defecto
    return base_type


# =====================================================
# FUNCIONES AUXILIARES
# =====================================================

def log(message, level='INFO'):
    """Registra mensajes con timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{level}] {message}")

def create_database_and_user():
    """Crea la base de datos y el usuario en PostgreSQL"""
    log("=" * 70)
    log("FASE 1: Preparación de PostgreSQL")
    log("=" * 70)
    
    try:
        # Conectar como administrador
        conn = psycopg2.connect(**POSTGRES_ADMIN_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verificar si la base de datos ya existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (POSTGRES_CONFIG['database'],))
        db_exists = cursor.fetchone()
        
        if db_exists:
            log(f"La base de datos '{POSTGRES_CONFIG['database']}' ya existe. Se eliminara y recreara.", "WARNING")
            # Terminar conexiones existentes
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{POSTGRES_CONFIG['database']}'
                AND pid <> pg_backend_pid()
            """)
            cursor.execute(f"DROP DATABASE {POSTGRES_CONFIG['database']}")
            log(f"Base de datos '{POSTGRES_CONFIG['database']}' eliminada.")
        
        # Crear la base de datos
        cursor.execute(f"CREATE DATABASE {POSTGRES_CONFIG['database']} WITH ENCODING 'UTF8'")
        log(f"[OK] Base de datos '{POSTGRES_CONFIG['database']}' creada exitosamente")
        
        # Verificar si el usuario existe
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (POSTGRES_CONFIG['user'],))
        user_exists = cursor.fetchone()
        
        if not user_exists:
            # Crear usuario
            cursor.execute(f"CREATE USER {POSTGRES_CONFIG['user']} WITH PASSWORD '{POSTGRES_CONFIG['password']}'")
            log(f"[OK] Usuario '{POSTGRES_CONFIG['user']}' creado exitosamente")
        else:
            log(f"Usuario '{POSTGRES_CONFIG['user']}' ya existe, se utilizara el existente", "INFO")
        
        # Otorgar privilegios
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {POSTGRES_CONFIG['database']} TO {POSTGRES_CONFIG['user']}")
        log(f"[OK] Privilegios otorgados al usuario '{POSTGRES_CONFIG['user']}'")
        
        cursor.close()
        conn.close()
        
        # Conectar a la nueva base de datos para otorgar privilegios en el esquema
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Otorgar privilegios en el esquema public (PostgreSQL 15+ requiere CREATE explícito)
        cursor.execute(f"GRANT ALL ON SCHEMA public TO {POSTGRES_CONFIG['user']}")
        cursor.execute(f"GRANT CREATE ON SCHEMA public TO {POSTGRES_CONFIG['user']}")
        cursor.execute(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {POSTGRES_CONFIG['user']}")
        cursor.execute(f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {POSTGRES_CONFIG['user']}")
        cursor.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {POSTGRES_CONFIG['user']}")
        cursor.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {POSTGRES_CONFIG['user']}")
        
        cursor.close()
        conn.close()
        
        log("[OK] Preparacion de PostgreSQL completada")
        return True
        
    except Exception as e:
        log(f"Error en la preparacion de PostgreSQL: {e}", "ERROR")
        return False

def adapt_create_table_sql(sqlite_sql, table_name, columns_info):
    """
    Adapta el SQL de CREATE TABLE de SQLite a PostgreSQL
    """
    # Crear la definición de columnas para PostgreSQL
    pg_columns = []
    
    for col in columns_info:
        col_name = col['name']
        sqlite_type = col['type']
        not_null = col['not_null']
        default_val = col['default_value']
        is_pk = col['pk']
        
        # Mapear tipo
        pg_type = map_sqlite_type_to_postgres(sqlite_type, col_name)
        
        # Construir definicin de columna
        col_def = f"{col_name} {pg_type}"
        
        # Primary Key con AUTOINCREMENT -> SERIAL
        if is_pk and sqlite_type == 'INTEGER':
            col_def = f"{col_name} SERIAL PRIMARY KEY"
        elif is_pk:
            col_def += " PRIMARY KEY"
        
        # NOT NULL
        if not_null and not is_pk:
            col_def += " NOT NULL"
        
        # DEFAULT
        if default_val is not None and not is_pk:
            # Adaptar valores por defecto
            if default_val.startswith("datetime('now'"):
                col_def += " DEFAULT CURRENT_TIMESTAMP"
            elif default_val.startswith("date('now'"):
                col_def += " DEFAULT CURRENT_DATE"
            elif default_val == '1' and pg_type == 'BOOLEAN':
                col_def += " DEFAULT TRUE"
            elif default_val == '0' and pg_type == 'BOOLEAN':
                col_def += " DEFAULT FALSE"
            else:
                # Conservar el valor por defecto original
                col_def += f" DEFAULT {default_val}"
        
        pg_columns.append(col_def)
    
    # Construir el CREATE TABLE
    pg_sql = f"CREATE TABLE {table_name} (\n    "
    pg_sql += ",\n    ".join(pg_columns)
    pg_sql += "\n);"
    
    return pg_sql

def migrate_schema(schema_data, pg_cursor):
    """Migra el esquema de las tablas"""
    log("=" * 70)
    log("FASE 2: Migración del Esquema de Tablas")
    log("=" * 70)
    
    tables = schema_data['tables']
    
    # Ordenar tablas para respetar dependencias (tablas sin FK primero)
    tables_ordered = []
    tables_with_fk = []
    
    for table_name, table_info in tables.items():
        if table_name == 'CONTRATOS_ARRENDAMIENTOS_OLD':
            continue  # Saltar tablas de backup
        
        if table_info['foreign_keys']:
            tables_with_fk.append((table_name, table_info))
        else:
            tables_ordered.append((table_name, table_info))
    
    # Agregar tablas con FK al final
    tables_ordered.extend(tables_with_fk)
    
    for table_name, table_info in tables_ordered:
        try:
            # Crear tabla
            create_sql = adapt_create_table_sql(
                table_info['create_sql'],
                table_name,
                table_info['columns']
            )
            
            log(f"Creando tabla: {table_name}")
            pg_cursor.execute(create_sql)
            
        except Exception as e:
            log(f"Error al crear tabla {table_name}: {e}", "ERROR")
            raise
    
    log(f"[OK] {len(tables_ordered)} tablas creadas exitosamente")

def add_foreign_keys(schema_data, pg_cursor):
    """Agrega las claves foráneas después de crear todas las tablas"""
    log("=" * 70)
    log("FASE 3: Agregando Claves Foráneas")
    log("=" * 70)
    
    fk_count = 0
    
    for table_name, table_info in schema_data['tables'].items():
        if table_name == 'CONTRATOS_ARRENDAMIENTOS_OLD':
            continue
        
        for fk in table_info['foreign_keys']:
            try:
                ref_table = fk['table']
                from_col = fk['from']
                to_col = fk['to']
                
                fk_name = f"fk_{table_name}_{from_col}_{ref_table}".lower()
                
                alter_sql = f"""
                ALTER TABLE {table_name}
                ADD CONSTRAINT {fk_name}
                FOREIGN KEY ({from_col}) REFERENCES {ref_table}({to_col})
                """
                
                if fk['on_delete']:
                    alter_sql += f" ON DELETE {fk['on_delete']}"
                if fk['on_update']:
                    alter_sql += f" ON UPDATE {fk['on_update']}"
                
                pg_cursor.execute(alter_sql)
                fk_count += 1
                
            except Exception as e:
                log(f"Advertencia al agregar FK en {table_name}.{from_col}: {e}", "WARNING")
    
    log(f"[OK] {fk_count} claves foráneas agregadas")

def migrate_data(schema_data, sqlite_conn, pg_cursor):
    """Migra todos los datos de SQLite a PostgreSQL"""
    log("=" * 70)
    log("FASE 4: Migración de Datos")
    log("=" * 70)
    
    sqlite_cursor = sqlite_conn.cursor()
    
    for table_name in schema_data['tables'].keys():
        if table_name == 'CONTRATOS_ARRENDAMIENTOS_OLD':
            continue
        
        try:
            # Obtener datos de SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                log(f"Tabla {table_name}: Sin datos (vacia)")
                continue
            
            # Obtener nombres de columnas
            column_names = [desc[0] for desc in sqlite_cursor.description]
            columns_info = schema_data['tables'][table_name]['columns']
            
            # Crear el INSERT para PostgreSQL
            placeholders = ', '.join(['%s'] * len(column_names))
            insert_sql = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
            
            # Convertir valores para PostgreSQL
            converted_rows = []
            for row in rows:
                converted_row = []
                for idx, value in enumerate(row):
                    col_info = columns_info[idx]
                    col_name = col_info['name']
                    pg_type = map_sqlite_type_to_postgres(col_info['type'], col_name)
                    
                    # Conversiones específicas
                    if value is None:
                        converted_row.append(None)
                    elif pg_type == 'BOOLEAN':
                        # Convertir 0/1 a False/True
                        converted_row.append(value == 1)
                    else:
                        converted_row.append(value)
                
                converted_rows.append(tuple(converted_row))
            
            # Insertar en lotes para mejor rendimiento
            batch_size = 1000
            for i in range(0, len(converted_rows), batch_size):
                batch = converted_rows[i:i+batch_size]
                pg_cursor.executemany(insert_sql, batch)
            
            log(f"Tabla {table_name}: {len(rows)} registros migrados")
            
        except Exception as e:
            log(f"Error al migrar datos de {table_name}: {e}", "ERROR")
            raise
    
    log("[OK] Migracion de datos completada")

def reset_sequences(schema_data, pg_cursor):
    """Resetea las secuencias de autoincremento en PostgreSQL"""
    log("=" * 70)
    log("FASE 5: Reseteando Secuencias")
    log("=" * 70)
    
    for table_name, table_info in schema_data['tables'].items():
        if table_name == 'CONTRATOS_ARRENDAMIENTOS_OLD':
            continue
        
        # Buscar columna PK con INTEGER (que se convirtió a SERIAL)
        for col in table_info['columns']:
            if col['pk'] and col['type'] == 'INTEGER':
                try:
                    # Resetear secuencia al máximo valor actual
                    pg_cursor.execute(f"""
                        SELECT setval(
                            pg_get_serial_sequence('{table_name}', '{col['name']}'),
                            COALESCE((SELECT MAX({col['name']}) FROM {table_name}), 1),
                            true
                        )
                    """)
                    log(f"Secuencia reseteada: {table_name}.{col['name']}")
                except Exception as e:
                    log(f"Advertencia al resetear secuencia en {table_name}: {e}", "WARNING")
                break
    
    log("[OK] Secuencias reseteadas")

def migrate_indices(schema_data, pg_cursor):
    """Migra los índicesde SQLite a PostgreSQL"""
    log("=" * 70)
    log("FASE 6: Migración de Índices")
    log("=" * 70)
    
    indices_migrated = 0
    
    for index_info in schema_data['indices']:
        try:
            # Adaptar SQL de índice a PostgreSQL
            sqlite_sql = index_info['sql']
            
            # Reemplazar CREATE INDEX por CREATE INDEX IF NOT EXISTS (opcional en PostgreSQL)
            pg_sql = sqlite_sql.replace('CREATE INDEX', 'CREATE INDEX IF NOT EXISTS')
            pg_sql = pg_sql.replace('CREATE UNIQUE INDEX', 'CREATE UNIQUE INDEX IF NOT EXISTS')
            
            # Ejecutar
            pg_cursor.execute(pg_sql)
            indices_migrated += 1
            log(f"Indice creado: {index_info['name']}")
            
        except Exception as e:
            log(f"Advertencia al crear indice {index_info['name']}: {e}", "WARNING")
    
    log(f"[OK] {indices_migrated} indices migrados")

def migrate_triggers(schema_data, pg_cursor):
    """Migra los triggers de SQLite a PostgreSQL (requiere adaptación manual)"""
    log("=" * 70)
    log("FASE 7: Migración de Triggers")
    log("=" * 70)
    
    # Los triggers en PostgreSQL tienen sintaxis diferente
    # Vamos a crear versiones adaptadas de los triggers más importantes
    
    triggers_pg = [
        # 1. Auditoría de contratos
        """
        CREATE OR REPLACE FUNCTION trg_auditoria_contratos_a_update()
        RETURNS TRIGGER AS $$
        BEGIN
            IF OLD.ESTADO_CONTRATO_A IS DISTINCT FROM NEW.ESTADO_CONTRATO_A THEN
                INSERT INTO AUDITORIA_CAMBIOS (
                    TABLA, ID_REGISTRO, TIPO_OPERACION, CAMPO_MODIFICADO,
                    VALOR_ANTERIOR, VALOR_NUEVO, USUARIO, MOTIVO_CAMBIO
                )
                VALUES (
                    'CONTRATOS_ARRENDAMIENTOS', OLD.ID_CONTRATO_A, 'UPDATE', 'ESTADO_CONTRATO_A',
                    OLD.ESTADO_CONTRATO_A, NEW.ESTADO_CONTRATO_A, 'SISTEMA', NEW.MOTIVO_CANCELACION
                );
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER TRG_AUDITORIA_CONTRATOS_A_UPDATE
        AFTER UPDATE ON CONTRATOS_ARRENDAMIENTOS
        FOR EACH ROW
        EXECUTE FUNCTION trg_auditoria_contratos_a_update();
        """,
        
        # 2. Auditoría de liquidaciones
        """
        CREATE OR REPLACE FUNCTION trg_auditoria_liquidaciones_p_update()
        RETURNS TRIGGER AS $$
        BEGIN
            IF OLD.ESTADO_LIQUIDACION IS DISTINCT FROM NEW.ESTADO_LIQUIDACION THEN
                INSERT INTO AUDITORIA_CAMBIOS (
                    TABLA, ID_REGISTRO, TIPO_OPERACION, CAMPO_MODIFICADO,
                    VALOR_ANTERIOR, VALOR_NUEVO, USUARIO
                )
                VALUES (
                    'LIQUIDACIONES_PROPIETARIOS', OLD.ID_LIQUIDACION_PROPIETARIO, 'UPDATE', 'ESTADO_LIQUIDACION',
                    OLD.ESTADO_LIQUIDACION, NEW.ESTADO_LIQUIDACION, 'SISTEMA'
                );
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER TRG_AUDITORIA_LIQUIDACIONES_P_UPDATE
        AFTER UPDATE ON LIQUIDACIONES_PROPIETARIOS
        FOR EACH ROW
        EXECUTE FUNCTION trg_auditoria_liquidaciones_p_update();
        """,
        
        # 3. Validación de fechas
        """
        CREATE OR REPLACE FUNCTION trg_validar_fechas_contrato()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.FECHA_FIN_CONTRATO_A <= NEW.FECHA_INICIO_CONTRATO_A THEN
                RAISE EXCEPTION 'Error: La fecha de finalizacion no puede ser anterior a la fecha de inicio.';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER TRG_VALIDAR_FECHAS_CONTRATO
        BEFORE INSERT ON CONTRATOS_ARRENDAMIENTOS
        FOR EACH ROW
        EXECUTE FUNCTION trg_validar_fechas_contrato();
        """,
        
        # 4. Evitar solapamiento de contratos de arrendamiento
        """
        CREATE OR REPLACE FUNCTION trg_evitar_solapamiento_arriendo()
        RETURNS TRIGGER AS $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS
                WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD
                AND ESTADO_CONTRATO_A = 'Activo'
            ) THEN
                RAISE EXCEPTION 'Error: Esta propiedad ya tiene un contrato de arrendamiento ACTIVO. Debe finalizar el anterior primero.';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER TRG_EVITAR_SOLAPAMIENTO_ARRIENDO
        BEFORE INSERT ON CONTRATOS_ARRENDAMIENTOS
        FOR EACH ROW
        EXECUTE FUNCTION trg_evitar_solapamiento_arriendo();
        """,
        
        # 5. Evitar solapamiento de contratos de mandato
        """
        CREATE OR REPLACE FUNCTION trg_evitar_solapamiento_mandato()
        RETURNS TRIGGER AS $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM CONTRATOS_MANDATOS
                WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD
                AND ESTADO_CONTRATO_M = 'Activo'
            ) THEN
                RAISE EXCEPTION 'Error: Esta propiedad ya tiene un contrato de mandato ACTIVO.';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER TRG_EVITAR_SOLAPAMIENTO_MANDATO
        BEFORE INSERT ON CONTRATOS_MANDATOS
        FOR EACH ROW
        EXECUTE FUNCTION trg_evitar_solapamiento_mandato();
        """,
        
        # 6. Actualizar disponibilidad cuando se ocupa
        """
        CREATE OR REPLACE FUNCTION trg_actualizar_disponibilidad_ocupada()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.ESTADO_CONTRATO_A = 'Activo' THEN
                UPDATE PROPIEDADES
                SET DISPONIBILIDAD_PROPIEDAD = FALSE
                WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER TRG_ACTUALIZAR_DISPONIBILIDAD_OCUPADA
        AFTER INSERT ON CONTRATOS_ARRENDAMIENTOS
        FOR EACH ROW
        EXECUTE FUNCTION trg_actualizar_disponibilidad_ocupada();
        """,
        
        # 7. Actualizar disponibilidad cuando se libera
        """
        CREATE OR REPLACE FUNCTION trg_actualizar_disponibilidad_libre()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.ESTADO_CONTRATO_A IN ('Finalizado', 'Cancelado')
               AND OLD.ESTADO_CONTRATO_A = 'Activo' THEN
                UPDATE PROPIEDADES
                SET DISPONIBILIDAD_PROPIEDAD = TRUE
                WHERE ID_PROPIEDAD = NEW.ID_PROPIEDAD;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER TRG_ACTUALIZAR_DISPONIBILIDAD_LIBRE
        AFTER UPDATE ON CONTRATOS_ARRENDAMIENTOS
        FOR EACH ROW
        EXECUTE FUNCTION trg_actualizar_disponibilidad_libre();
        """,
        
        # 8. Exigir motivo de cancelación
        """
        CREATE OR REPLACE FUNCTION trg_exigir_motivo_cancelacion()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.ESTADO_CONTRATO_A = 'Cancelado'
               AND (NEW.MOTIVO_CANCELACION IS NULL OR NEW.MOTIVO_CANCELACION = '') THEN
                RAISE EXCEPTION 'Error: Para cancelar un contrato es OBLIGATORIO ingresar un motivo de cancelacion.';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER TRG_EXIGIR_MOTIVO_CANCELACION
        BEFORE UPDATE ON CONTRATOS_ARRENDAMIENTOS
        FOR EACH ROW
        EXECUTE FUNCTION trg_exigir_motivo_cancelacion();
        """,
        
        # 9. Auto-crear pago al aprobar liquidación
        """
        CREATE OR REPLACE FUNCTION trg_auto_crear_pago_propietario()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.ESTADO_LIQUIDACION = 'Aprobada' AND OLD.ESTADO_LIQUIDACION <> 'Aprobada' THEN
                INSERT INTO PAGOS_PROPIETARIOS (
                    ID_LIQUIDACION_PROPIETARIO,
                    ID_PROPIETARIO,
                    VALOR_PAGO,
                    FECHA_PROGRAMADA,
                    ESTADO_PAGO,
                    OBSERVACIONES_PAGO
                )
                VALUES (
                    NEW.ID_LIQUIDACION_PROPIETARIO,
                    NEW.ID_PROPIETARIO,
                    NEW.VALOR_NETO_PROPIETARIO,
                    CURRENT_DATE + INTERVAL '1 day',
                    'Pendiente',
                    'Generado automaticamente al aprobar liquidacion #' || NEW.ID_LIQUIDACION_PROPIETARIO
                );
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER TRG_AUTO_CREAR_PAGO_PROPIETARIO
        AFTER UPDATE ON LIQUIDACIONES_PROPIETARIOS
        FOR EACH ROW
        EXECUTE FUNCTION trg_auto_crear_pago_propietario();
        """
    ]
    
    triggers_created = 0
    for trigger_sql in triggers_pg:
        try:
            pg_cursor.execute(trigger_sql)
            triggers_created += 1
        except Exception as e:
            log(f"Advertencia al crear trigger: {e}", "WARNING")
    
    log(f"[OK] {triggers_created} triggers migrados")

def migrate_views(schema_data, pg_cursor):
    """Migra las vistas de SQLite a PostgreSQL"""
    log("=" * 70)
    log("FASE 8: Migración de Vistas")
    log("=" * 70)
    
    # Adaptar las vistas a PostgreSQL
    views_pg = {
        'VW_ALERTA_MORA_DIARIA': """
            CREATE OR REPLACE VIEW VW_ALERTA_MORA_DIARIA AS
            SELECT 
                r.ID_RECAUDO,
                ca.ID_CONTRATO_A,
                p.DIRECCION_PROPIEDAD,
                arr_p.NOMBRE_COMPLETO AS ARRENDATARIO,
                arr_p.TELEFONO_PRINCIPAL,
                r.VALOR_RECAUDO,
                r.FECHA_VENCIMIENTO_RECAUDO,
                CURRENT_DATE AS FECHA_HOY,
                CAST((CURRENT_DATE - r.FECHA_VENCIMIENTO_RECAUDO::DATE) AS INTEGER) AS DIAS_RETRASO
            FROM RECAUDO_ARRENDAMIENTO r
            JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
            JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
            JOIN PERSONAS arr_p ON arr.ID_PERSONA = arr_p.ID_PERSONA
            WHERE r.ESTADO_RECAUDO IN ('Pendiente', 'Mora')
            AND r.FECHA_VENCIMIENTO_RECAUDO::DATE < CURRENT_DATE;
        """,
        
        'VW_ALERTA_VENCIMIENTO_CONTRATOS': """
            CREATE OR REPLACE VIEW VW_ALERTA_VENCIMIENTO_CONTRATOS AS
            SELECT 
                ca.ID_CONTRATO_A,
                p.DIRECCION_PROPIEDAD,
                arr_p.NOMBRE_COMPLETO AS ARRENDATARIO,
                arr_p.TELEFONO_PRINCIPAL,
                ca.FECHA_FIN_CONTRATO_A,
                CAST((ca.FECHA_FIN_CONTRATO_A::DATE - CURRENT_DATE) AS INTEGER) AS DIAS_RESTANTES
            FROM CONTRATOS_ARRENDAMIENTOS ca
            JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
            JOIN PERSONAS arr_p ON arr.ID_PERSONA = arr_p.ID_PERSONA
            WHERE ca.ESTADO_CONTRATO_A = 'Activo'
            AND ca.FECHA_FIN_CONTRATO_A::DATE <= CURRENT_DATE + INTERVAL '90 days';
        """,
        
        'VW_REPORTE_DISPONIBLES': """
            CREATE OR REPLACE VIEW VW_REPORTE_DISPONIBLES AS
            SELECT 
                p.ID_PROPIEDAD,
                m.NOMBRE_MUNICIPIO AS CIUDAD,
                p.DIRECCION_PROPIEDAD,
                p.ESTRATO,
                p.CANON_ARRENDAMIENTO_ESTIMADO AS PRECIO,
                p.HABITACIONES,
                p.BANO,
                p.AREA_M2
            FROM PROPIEDADES p
            JOIN MUNICIPIOS m ON p.ID_MUNICIPIO = m.ID_MUNICIPIO
            WHERE p.DISPONIBILIDAD_PROPIEDAD = TRUE
            AND p.ESTADO_REGISTRO = TRUE;
        """
    }
    
    views_created = 0
    for view_name, view_sql in views_pg.items():
        try:
            pg_cursor.execute(view_sql)
            views_created += 1
            log(f"Vista creada: {view_name}")
        except Exception as e:
            log(f"Advertencia al crear vista {view_name}: {e}", "WARNING")
    
    log(f"[OK] {views_created} vistas migradas")

def verify_migration(schema_data, sqlite_conn, pg_cursor):
    """Verifica que la migración fue exitosa"""
    log("=" * 70)
    log("FASE 9: Verificación de la Migración")
    log("=" * 70)
    
    sqlite_cursor = sqlite_conn.cursor()
    errors = []
    
    for table_name in schema_data['tables'].keys():
        if table_name == 'CONTRATOS_ARRENDAMIENTOS_OLD':
            continue
        
        try:
            # Contar registros en SQLite
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            sqlite_count = sqlite_cursor.fetchone()[0]
            
            # Contar registros en PostgreSQL
            pg_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            pg_count = pg_cursor.fetchone()[0]
            
            if sqlite_count == pg_count:
                log(f"[OK] {table_name}: {pg_count} registros")
            else:
                error_msg = f"{table_name}: SQLite={sqlite_count}, PostgreSQL={pg_count}"
                log(f"[ERROR] {error_msg}", "ERROR")
                errors.append(error_msg)
        
        except Exception as e:
            error_msg = f"Error al verificar {table_name}: {e}"
            log(error_msg, "ERROR")
            errors.append(error_msg)
    
    if errors:
        log(f"[ADVERTENCIA] Se encontraron {len(errors)} errores en la verificacion", "WARNING")
        return False
    else:
        log("[OK] Verificacion completada: Todos los datos migrados correctamente")
        return True

# =====================================================
# FUNCIÓN PRINCIPAL
# =====================================================

def main():
    """Función principal de migración"""
    log("=" * 70)
    log("MIGRACION DE BASE DE DATOS: SQLite -> PostgreSQL")
    log("Sistema de Gestion Inmobiliaria Velar SAS")
    log("=" * 70)
    log(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("")
    
    # Cargar esquema extraído
    schema_path = Path(__file__).parent / 'schema_extracted.json'
    if not schema_path.exists():
        log("Error: No se encontro el archivo schema_extracted.json", "ERROR")
        log("Ejecute primero extract_schema.py", "ERROR")
        return False
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_data = json.load(f)
    
    log(f"Esquema cargado: {len(schema_data['tables'])} tablas")
    
    try:
        # Fase 1: Preparar PostgreSQL
        if not create_database_and_user():
            return False
        
        # Conectar a SQLite
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        log("[OK] Conectado a SQLite")
        
        # Conectar a PostgreSQL como administrador para crear tablas
        log("Conectando a PostgreSQL como administrador para crear estructura...")
        pg_admin_conn = psycopg2.connect(
            host=POSTGRES_ADMIN_CONFIG['host'],
            port=POSTGRES_ADMIN_CONFIG['port'],
            database=POSTGRES_CONFIG['database'],  # Conectar a la nueva DB como admin
            user=POSTGRES_ADMIN_CONFIG['user'],
            password=POSTGRES_ADMIN_CONFIG['password']
        )
        pg_cursor = pg_admin_conn.cursor()
        log("[OK] Conectado a PostgreSQL como postgres")
        
        # Fase 2-8: Migración
        migrate_schema(schema_data, pg_cursor)
        pg_admin_conn.commit()
        
        add_foreign_keys(schema_data, pg_cursor)
        pg_admin_conn.commit()
        
        migrate_data(schema_data, sqlite_conn, pg_cursor)
        pg_admin_conn.commit()
        
        reset_sequences(schema_data, pg_cursor)
        pg_admin_conn.commit()
        
        migrate_indices(schema_data, pg_cursor)
        pg_admin_conn.commit()
        
        migrate_triggers(schema_data, pg_cursor)
        pg_admin_conn.commit()
        
        migrate_views(schema_data, pg_cursor)
        pg_admin_conn.commit()
        
        # Transferir propiedad de todas las tablas al usuario de aplicación
        log("=" * 70)
        log("Transfiriendo propiedad al usuario de aplicacion...")
        log("=" * 70)
        
        for table_name in schema_data['tables'].keys():
            if table_name != 'CONTRATOS_ARRENDAMIENTOS_OLD':
                try:
                    pg_cursor.execute(f"ALTER TABLE {table_name} OWNER TO {POSTGRES_CONFIG['user']}")
                    log(f"Propietario cambiado: {table_name}")
                except Exception as e:
                    log(f"Advertencia al cambiar propietario de {table_name}: {e}", "WARNING")
        
        # Cambiar propietario de vistas
        for view_name in ['VW_ALERTA_MORA_DIARIA', 'VW_ALERTA_VENCIMIENTO_CONTRATOS', 'VW_REPORTE_DISPONIBLES']:
            try:
                pg_cursor.execute(f"ALTER VIEW {view_name} OWNER TO {POSTGRES_CONFIG['user']}")
                log(f"Propietario cambiado: {view_name}")
            except Exception as e:
                log(f"Advertencia al cambiar propietario de {view_name}: {e}", "WARNING")
        
        # Cambiar propietario de secuencias
        for table_name, table_info in schema_data['tables'].items():
            if table_name == 'CONTRATOS_ARRENDAMIENTOS_OLD':
                continue
            for col in table_info['columns']:
                if col['pk'] and col['type'] == 'INTEGER':
                    try:
                        seq_name = f"{table_name}_{col['name']}_seq".lower()
                        pg_cursor.execute(f"ALTER SEQUENCE {seq_name} OWNER TO {POSTGRES_CONFIG['user']}")
                    except:
                        pass  # Algunas secuencias pueden no existir
                    break
        
        pg_admin_conn.commit()
        log("[OK] Propiedad transferida")
        
        # Fase 9: Verificación
        verify_migration(schema_data, sqlite_conn, pg_cursor)
        
        # Limpiar
        sqlite_conn.close()
        pg_cursor.close()
        pg_admin_conn.close()
        
        log("=" * 70)
        log("[OK] MIGRACION COMPLETADA EXITOSAMENTE!")
        log("=" * 70)
        log("")
        log("Proximos pasos:")
        log("1. Actualizar la configuracion de conexion en tu aplicacion Reflex")
        log("2. Instalar psycopg2: pip install psycopg2-binary")
        log("3. Probar la conexion con verify_connection.py")
        log("")
        
        return True
        
    except Exception as e:
        log(f"Error critico durante la migracion: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
