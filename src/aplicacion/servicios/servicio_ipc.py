from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.ipc import IPC
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite


class ServicioIPC:

    def __init__(self, db_manager: DatabaseManager):
        self.repo = RepositorioIPCSQLite(db_manager)

    def listar_todos(self) -> List[IPC]:
        """Retorna todos los registros de IPC ordenados por año."""
        return self.repo.listar_todos()

    def obtener_por_anio(self, anio: int) -> Optional[IPC]:
        return self.repo.obtener_por_anio(anio)

    def crear_ipc(self, anio: int, valor: float, usuario: str) -> IPC:
        """
        Registra un nuevo IPC.
        Valida que no exista ya registro para ese año.
        """
        if not anio or anio < 2000 or anio > 2100:
            raise ValueError("Año inválido")

        if valor is None or valor < 0:
            raise ValueError("Valor de IPC inválido")

        existente = self.repo.obtener_por_anio(anio)
        if existente:
            raise ValueError(f"Ya existe un registro de IPC para el año {anio}")

        ipc = IPC(
            anio=anio,
            valor_ipc=valor,  # Guardamos tal cual (ej: 5.5 o 5)
            fecha_publicacion=datetime.now().strftime("%Y-%m-%d"),
            estado_registro=1,
            created_by=usuario,
        )

        return self.repo.crear(ipc, usuario)

    def actualizar_ipc(self, id_ipc: int, valor: float, usuario: str) -> IPC:
        """
        Actualiza el valor de un IPC existente.
        """
        ipc = self.repo.obtener_por_id(id_ipc)
        if not ipc:
            raise ValueError("Registro IPC no encontrado")

        ipc.valor_ipc = valor
        ipc.fecha_publicacion = datetime.now().strftime("%Y-%m-%d")  # Actualizamos fecha referencia

        self.repo.actualizar(ipc, usuario)
        return ipc
