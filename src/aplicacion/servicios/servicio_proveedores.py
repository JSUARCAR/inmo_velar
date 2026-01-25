from typing import List, Optional

from src.dominio.entidades.proveedor import Proveedor
from src.dominio.interfaces.repositorio_proveedores import RepositorioProveedores
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_proveedores_sqlite import (
    RepositorioProveedoresSQLite,
)


class ServicioProveedores:
    def __init__(self, db_manager: DatabaseManager):
        self.repo: RepositorioProveedores = RepositorioProveedoresSQLite(db_manager)

    def listar_proveedores(self) -> List[Proveedor]:
        return self.repo.listar()

    def obtener_proveedor(self, id_proveedor: int) -> Optional[Proveedor]:
        return self.repo.obtener_por_id(id_proveedor)

    def obtener_por_persona(self, id_persona: int) -> Optional[Proveedor]:
        return self.repo.obtener_por_persona_id(id_persona)

    def crear_proveedor(self, datos: dict, usuario_actual: str) -> int:
        # Validar si ya existe como proveedor
        id_persona = datos.get("id_persona")
        existe = self.repo.obtener_por_persona_id(id_persona)
        if existe and existe.estado_registro:
            raise ValueError("Esta persona ya está registrada como proveedor activo")

        proveedor = Proveedor(
            id_proveedor=None,
            id_persona=id_persona,
            especialidad=datos.get("especialidad"),
            calificacion=datos.get("calificacion", 0.0),
            observaciones=datos.get("observaciones"),
            estado_registro=1,
            created_by=usuario_actual,
        )
        return self.repo.guardar(proveedor)

    def actualizar_proveedor(self, id_proveedor: int, datos: dict) -> None:
        proveedor = self.repo.obtener_por_id(id_proveedor)
        if not proveedor:
            raise ValueError("Proveedor no encontrado")

        if "especialidad" in datos:
            proveedor.especialidad = datos["especialidad"]
        if "calificacion" in datos:
            proveedor.calificacion = datos["calificacion"]
        if "observaciones" in datos:
            proveedor.observaciones = datos["observaciones"]

        self.repo.actualizar(proveedor)

    def eliminar_proveedor(self, id_proveedor: int) -> None:
        self.repo.eliminar(id_proveedor)
