
from src.infraestructura.cache.cache_manager import cache_manager

def clear_all():
    try:
        total = cache_manager.clear_all()
        print(f"Caché global limpiado. Total items eliminados: {total}")
    except Exception as e:
        print(f"Error limpiando caché: {e}")

if __name__ == "__main__":
    clear_all()
