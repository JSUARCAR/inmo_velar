
import sys
import os
import typing
from typing import Any, Dict, List, Optional, Union, get_type_hints

# Simular entorno Reflex
try:
    import reflex as rx
    from pydantic import BaseModel
except ImportError:
    print("Error: Reflex or Pydantic not found in venv")
    sys.exit(1)

def typehint_issubclass(possible_subclass, possible_superclass):
    try:
        return issubclass(possible_subclass, possible_superclass)
    except TypeError as e:
        if "TypedDict" in str(e):
            print(f"!!! ENCONTRADO !!!")
            print(f"Subclass: {possible_subclass}")
            print(f"Superclass: {possible_superclass}")
            return False
        raise e

def check_class_hints(cls):
    print(f"\nRevisando clase: {cls.__name__}")
    try:
        hints = get_type_hints(cls)
        for name, hint in hints.items():
            print(f"  Campo: {name} | Hint: {hint}")
            # Reflex suele iterar sobre los argumentos de tipos genéricos
            origin = typing.get_origin(hint)
            args = typing.get_args(hint)
            
            if origin:
                for arg in args:
                    # Reflex a veces hace checks recursivos
                    try:
                        # Simulamos lo que hace Reflex: chequear si el argumento es subclase de rx.Base
                        # o si es un tipo válido para el estado
                        typehint_issubclass(arg, rx.Base)
                    except TypeError:
                        pass
            else:
                try:
                    typehint_issubclass(hint, rx.Base)
                except TypeError:
                    pass
    except Exception as e:
        print(f"  Error al procesar {cls.__name__}: {e}")

# Importar los estados problemáticos
# Agregar el directorio raíz al path para que "from src..." funcione
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.append(current_dir)
# También agregar el directorio src para que los imports relativos funcionen si es necesario
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

try:
    from presentacion_reflex.state.propiedad_horizontal_state import PropiedadHorizontalState, AsistenciaModel, PagoAdminModel
    from presentacion_reflex.state.auth_state import AuthState
    
    check_class_hints(AsistenciaModel)
    check_class_hints(PagoAdminModel)
    check_class_hints(PropiedadHorizontalState)
    check_class_hints(AuthState)
    
except ImportError as e:
    print(f"Error importando estados: {e}")
    import traceback
    traceback.print_exc()

print("\nDiagnóstico completado.")
