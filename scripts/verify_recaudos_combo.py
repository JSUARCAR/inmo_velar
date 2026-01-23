
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos

def verify():
    print("=== VERIFICACIÓN DE COMBOBOX RECAUDOS ===")
    
    # 1. Inicializar DB y Servicio
    try:
        db = DatabaseManager()
        servicio = ServicioContratos(db)
        print("✅ ServicioContratos inicializado.")
    except Exception as e:
        print(f"❌ Error al inicializar servicio: {e}")
        return

    # 2. Llamar al nuevo método
    try:
        contratos = servicio.listar_arrendamientos_activos()
        print(f"✅ Método listar_arrendamientos_activos ejecutado correctamente.")
        print(f"📊 Se encontraron {len(contratos)} contratos activos.")
    except AttributeError:
        print("❌ Error: El método listar_arrendamientos_activos no existe en ServicioContratos.")
        return
    except Exception as e:
        print(f"❌ Error al ejecutar método: {e}")
        return
        
    # 3. Mostrar resultados
    if not contratos:
        print("⚠️ Advertencia: No hay contratos activos para mostrar. El combobox aparecerá vacío pero sin error.")
    else:
        print("\n📝 Resultados:")
        for c in contratos:
            print(f" - ID: {c['id']}, Texto: '{c['texto']}', Canon: ${c['canon']:,}")

    print("\n=== FIN DE VERIFICACIÓN ===")

if __name__ == "__main__":
    verify()
