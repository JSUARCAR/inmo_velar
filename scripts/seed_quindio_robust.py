
import sys
import os

sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def seed_robust():
    print("🛠️ Iniciando sembrado robusto de Quindío...")
    
    conn = db_manager.obtener_conexion()
    cursor = conn.cursor()
    
    try:
        # 1. Corregir secuencia (si existe)
        # Asumimos convención de nombre de secuencia standard en PG: table_column_seq
        try:
            print("🔧 Sincronizando secuencia de IDs...")
            # Detectar nombre de secuencia si es posible, o probar standard
            sql_fix_seq = "SELECT setval('municipios_id_municipio_seq', COALESCE((SELECT MAX(id_municipio) FROM municipios), 0) + 1, false);"
            cursor.execute(sql_fix_seq)
            conn.commit()
            print("✅ Secuencia sincronizada.")
        except Exception as e:
            print(f"⚠️ No se pudo sincronizar secuencia (puede que no sea SERIAL o nombre distinto): {e}")
            conn.rollback()

        municipios = [
            # Municipios
            ('Armenia', 'Quindío'),
            ('Buenavista', 'Quindío'),
            ('Calarcá', 'Quindío'),
            ('Circasia', 'Quindío'),
            ('Córdoba', 'Quindío'),
            ('Filandia', 'Quindío'),
            ('Génova', 'Quindío'),
            ('La Tebaida', 'Quindío'),
            ('Montenegro', 'Quindío'),
            ('Pijao', 'Quindío'),
            ('Quimbaya', 'Quindío'),
            ('Salento', 'Quindío'),
            
            # Corregimientos
            ('Barcelona (Calarcá)', 'Quindío'),
            ('La Virginia (Calarcá)', 'Quindío'),
            ('Quebradanegra (Calarcá)', 'Quindío'),
            ('El Caimo (Armenia)', 'Quindío'),
            ('Pueblo Tapao (Montenegro)', 'Quindío'),
            ('La India (Filandia)', 'Quindío'),
            ('La Silva (La Tebaida)', 'Quindío')
        ]
        
        insertados = 0
        existentes = 0
        
        for name, depto in municipios:
            # 2. Verificar existencia
            cursor.execute("SELECT 1 FROM MUNICIPIOS WHERE NOMBRE_MUNICIPIO = %s AND DEPARTAMENTO = %s", (name, depto))
            if cursor.fetchone():
                print(f"🔹 {name} ya existe. Saltando.")
                existentes += 1
            else:
                # 3. Insertar
                cursor.execute(
                    "INSERT INTO MUNICIPIOS (NOMBRE_MUNICIPIO, DEPARTAMENTO, ESTADO_REGISTRO) VALUES (%s, %s, TRUE)",
                    (name, depto)
                )
                insertados += 1
                print(f"✅ Insertado: {name}")
        
        conn.commit()
        print(f"\n📊 Resumen: {insertados} insertados, {existentes} ya existían.")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error crítico: {e}")
    finally:
        # No cerramos conexión si es del pool gestionado, pero el script termina asi que ok.
        pass

if __name__ == "__main__":
    seed_robust()
