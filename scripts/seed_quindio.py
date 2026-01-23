
import sys
import os

# Add src to path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def seed():
    print("🌱 Iniciando sembrado de datos del Quindío...")
    
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
        
        # Corregimientos Principales
        ('Barcelona (Calarcá)', 'Quindío'),
        ('La Virginia (Calarcá)', 'Quindío'),
        ('Quebradanegra (Calarcá)', 'Quindío'),
        ('El Caimo (Armenia)', 'Quindío'),
        ('Pueblo Tapao (Montenegro)', 'Quindío'),
        ('La India (Filandia)', 'Quindío'),
        ('La Silva (La Tebaida)', 'Quindío')
    ]
    
    # Construir SQL
    # PostgreSQL permite inserción múltiple, pero para asegurar compatibilidad y control:
    # Usaremos un loop o syntax compatible.
    
    sql_base = "INSERT INTO MUNICIPIOS (NOMBRE_MUNICIPIO, DEPARTAMENTO, ESTADO_REGISTRO) VALUES "
    values_list = []
    
    for nombre, depto in municipios:
        values_list.append(f"('{nombre}', '{depto}', TRUE)")
    
    full_sql = sql_base + ",\n".join(values_list) + ";"
    
    try:
        db_manager.ejecutar_script(full_sql)
        print(f"✅ Se han insertado {len(municipios)} registros correctamente.")
    except Exception as e:
        print(f"❌ Error al insertar datos: {e}")

if __name__ == "__main__":
    seed()
