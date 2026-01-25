"""
Entidad: ParametroSistema

Mapeo exacto de la tabla PARAMETROS_SISTEMA.
Almacena configuraciones del sistema como comisiones, impuestos, alertas, etc.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class ParametroSistema:
    """
    Entidad: ParametroSistema
    Tabla: PARAMETROS_SISTEMA

    Columnas:
    - ID_PARAMETRO (PK, INTEGER)
    - NOMBRE_PARAMETRO (TEXT, UNIQUE, NOT NULL)
    - VALOR_PARAMETRO (TEXT, NOT NULL)
    - TIPO_DATO (TEXT, CHECK: 'INTEGER', 'TEXT', 'DECIMAL', 'BOOLEAN')
    - DESCRIPCION (TEXT)
    - CATEGORIA (TEXT)
    - MODIFICABLE (INTEGER, CHECK: 0 o 1)
    - CREATED_AT (TEXT)
    - UPDATED_AT (TEXT)
    - UPDATED_BY (TEXT)

    Categorías conocidas:
    - COMISIONES: Porcentajes de comisiones por defecto
    - IMPUESTOS: IVA, 4x1000, etc.
    - VALIDACIONES: Límites de canon, etc.
    - ALERTAS: Días de anticipación para alertas
    - OPERACIONES: Configuración de operaciones diarias
    - NOTIFICACIONES: Habilitar/deshabilitar canales
    - SISTEMA: Configuraciones generales
    """

    id_parametro: Optional[int] = None

    nombre_parametro: str = ""
    valor_parametro: str = ""
    tipo_dato: Optional[str] = "TEXT"  # INTEGER, TEXT, DECIMAL, BOOLEAN

    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    modificable: Optional[int] = 1  # 1 = modificable, 0 = solo lectura

    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None

    def __post_init__(self):
        """Validaciones al crear la entidad."""
        if self.tipo_dato and self.tipo_dato not in ("INTEGER", "TEXT", "DECIMAL", "BOOLEAN"):
            raise ValueError(
                f"Tipo de dato inválido: {self.tipo_dato}. "
                "Valores permitidos: INTEGER, TEXT, DECIMAL, BOOLEAN"
            )

        if self.modificable is not None and self.modificable not in (0, 1):
            raise ValueError("Modificable debe ser 0 o 1")

    @property
    def es_modificable(self) -> bool:
        """Indica si el parámetro puede ser editado."""
        return self.modificable == 1

    @property
    def valor_como_int(self) -> int:
        """Convierte el valor a entero."""
        if self.tipo_dato != "INTEGER":
            raise TypeError(f"El parámetro '{self.nombre_parametro}' no es de tipo INTEGER")
        try:
            return int(self.valor_parametro)
        except ValueError:
            raise ValueError(f"No se puede convertir '{self.valor_parametro}' a entero")

    @property
    def valor_como_decimal(self) -> Decimal:
        """Convierte el valor a Decimal."""
        if self.tipo_dato not in ("DECIMAL", "INTEGER"):
            raise TypeError(
                f"El parámetro '{self.nombre_parametro}' no es de tipo DECIMAL o INTEGER"
            )
        try:
            return Decimal(self.valor_parametro)
        except Exception:
            raise ValueError(f"No se puede convertir '{self.valor_parametro}' a Decimal")

    @property
    def valor_como_bool(self) -> bool:
        """Convierte el valor a booleano."""
        if self.tipo_dato != "BOOLEAN":
            raise TypeError(f"El parámetro '{self.nombre_parametro}' no es de tipo BOOLEAN")
        return self.valor_parametro in ("1", "true", "True", "TRUE", "yes", "Yes", "YES")

    @property
    def valor_como_porcentaje(self) -> Decimal:
        """
        Convierte valores en formato base 100 a porcentaje decimal.
        Ejemplo: 800 -> 8.00%, 1900 -> 19.00%
        """
        if self.tipo_dato != "INTEGER":
            raise TypeError(
                f"El parámetro '{self.nombre_parametro}' debe ser INTEGER para conversión a porcentaje"
            )
        return Decimal(self.valor_parametro) / Decimal("100")

    def actualizar_valor(self, nuevo_valor: str, usuario: str) -> None:
        """
        Actualiza el valor del parámetro.

        Args:
            nuevo_valor: Nuevo valor como string
            usuario: Usuario que realiza el cambio

        Raises:
            PermissionError: Si el parámetro no es modificable
        """
        if not self.es_modificable:
            raise PermissionError(f"El parámetro '{self.nombre_parametro}' no es modificable")

        # Validar tipo de dato
        if self.tipo_dato == "INTEGER":
            try:
                int(nuevo_valor)
            except ValueError:
                raise ValueError("El valor debe ser un número entero válido")
        elif self.tipo_dato == "DECIMAL":
            try:
                Decimal(nuevo_valor)
            except Exception:
                raise ValueError("El valor debe ser un número decimal válido")
        elif self.tipo_dato == "BOOLEAN":
            if nuevo_valor not in ("0", "1", "true", "false", "True", "False"):
                raise ValueError("El valor debe ser un booleano válido: 0, 1, true, false")

        self.valor_parametro = nuevo_valor
        self.updated_at = datetime.now().isoformat()
        self.updated_by = usuario
