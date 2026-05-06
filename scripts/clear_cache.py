
from src.infraestructura.cache.cache_manager import cache_manager

def clear_cache():
    try:
        cache_manager.clear()
        print("Caché global invalidado.")
    except Exception as e:
        print(f"Error invalidando caché: {e}")

if __name__ == "__main__":
    clear_cache()
