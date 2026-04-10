from datetime import date, datetime
from typing import List, Optional

import pydantic
import reflex as rx


class AsistenciaModel(pydantic.BaseModel):
    """Estructura para serialización de Asistencia en UI."""

    id_asistencia: int
    id_propiedad: int
    direccion_propiedad: str
    fecha_asistencia: str
    hora_asistencia: str
    tipo_reunion: str
    tipo_asistente: str
    nombre_asistente: str
    costo_asistente: float
    direccion_asistencia: str
    estado_asistencia: str
    color_tipo: str
    tooltip_asistencia: str = ""


class AsistenciaCalendarioModel(AsistenciaModel):
    """Modelo extendido para vista calendario."""

    fecha_date: Optional[date] = None
    color_estado: str = "gray"
    indicador_fecha: str = ""
    es_hoy: bool = False
    es_pasado: bool = False

    @pydantic.model_validator(mode="before")
    @classmethod
    def calcular_campos_calendario(cls, values):
        fecha_str = values.get("fecha_asistencia", "")
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, "%d/%m/%Y").date()
                values["fecha_date"] = fecha
                values["es_hoy"] = fecha == date.today()
                values["es_pasado"] = fecha < date.today()

                estado = values.get("estado_asistencia", "Programada")
                color_map = {
                    "Programada": "blue",
                    "Realizada": "green",
                    "Cancelada": "red",
                }
                values["color_estado"] = color_map.get(estado, "gray")
            except (ValueError, TypeError):
                values["fecha_date"] = None
                values["es_hoy"] = False
                values["es_pasado"] = True
                values["color_estado"] = "gray"
        return values


class CalendarioDiaModel(pydantic.BaseModel):
    """Modelo para representar un día en el calendario UI."""

    dia: int = 0
    es_vacio: bool = False
    eventos: List[AsistenciaCalendarioModel] = []
    tiene_eventos: bool = False


class PagoAdminModel(pydantic.BaseModel):
    """Estructura para serialización de PagoAdministración en UI."""

    id_pago_admin: int
    id_propiedad: int
    nombre_propietario: str
    direccion_propiedad: str
    valor_administracion: float
    valor_formateado: str
    fecha_pago: int
    link_pago: str
    periodo_pago: str
    estado_pago: str
    color_estado: str
    tooltip_pago: str = ""
