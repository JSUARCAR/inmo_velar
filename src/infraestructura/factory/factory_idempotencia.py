from src.dominio.interfaces.repositorio_idempotencia import IRepositorioIdempotencia
from src.infraestructura.persistencia.repositorio_idempotencia_postgres import (
    RepositorioIdempotenciaPostgres,
)


def crear_repo_idempotencia() -> IRepositorioIdempotencia:
    return RepositorioIdempotenciaPostgres()
