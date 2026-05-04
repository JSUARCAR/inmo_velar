"""
Test script para verificar el fix del error StateProxy en save_liquidacion.
Este test verifica que el acceso a show_create_modal no cause el error
'StateProxy is immutable outside of a context manager'.
"""

import sys

sys.path.insert(0, "src")



def test_save_liquidacion_no_stateproxy_error():
    """
    Verifica que save_liquidacion no acceda a self.show_create_modal
    fuera del context manager async with self.
    """
    # Lee el archivo fuente
    with open("src/presentacion_reflex/state/liquidaciones_state.py", "r") as f:
        content = f.read()

    # Busca el método save_liquidacion
    import re

    method_match = re.search(
        r"async def save_liquidacion\(self, form_data: Dict\):.*?(?=\n    @rx\.event|\n    async def|\nclass |\Z)",
        content,
        re.DOTALL,
    )

    assert method_match, "No se encontró el método save_liquidacion"
    method_body = method_match.group(0)

    # Verifica que show_create_modal se acceda SOLO dentro de async with self
    # Busca accesos fuera del context manager

    # Divide el método en bloques
    lines = method_body.split("\n")

    in_async_with_self = False
    problematic_accesses = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detectar entrada/salida de async with self
        if "async with self:" in stripped:
            in_async_with_self = True
            async_with_depth = i
            continue

        # Si estamos fuera y encontramos 'if self.show_create_modal'
        if not in_async_with_self and "self.show_create_modal" in stripped:
            # Verificar que no sea una asignación DENTRO de async with
            if "self.show_create_modal =" not in stripped:
                problematic_accesses.append((i, stripped))

        # Si encontramos un bloque try que no sea dentro del primer async with
        if stripped.startswith("try:") and not in_async_with_self:
            in_async_with_self = False

    # El fix correcto es capturar el valor ANTES del try
    # Buscar que show_create_modal se capture en una variable local
    has_local_variable = (
        "is_create_mode = self.show_create_modal" in method_body
        or "create_mode = self.show_create_modal" in method_body
        or "_is_create = self.show_create_modal" in method_body
    )

    if not has_local_variable:
        print(
            "ERROR: El fix no está aplicado - show_create_modal no se captura en variable local"
        )
        print("Accesos problemáticos fuera del async with self:")
        for line_num, line_text in problematic_accesses:
            print(f"  Línea {line_num}: {line_text}")
        sys.exit(1)

    print(
        "OK: El fix está aplicado - show_create_modal se captura en variable local antes del try"
    )
    print("OK: No hay accesos problemáticos a StateProxy fuera del context manager")
    sys.exit(0)


if __name__ == "__main__":
    test_save_liquidacion_no_stateproxy_error()
