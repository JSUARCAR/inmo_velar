"""
Estado Reflex: PropiedadHorizontal
Gestión de Asambleas y Pagos de Administración.
Refactorizado siguiendo SOLID y Clean Architecture.
"""

import logging
from datetime import datetime, date, time
from typing import Any, Dict, List, Optional

import pydantic
import reflex as rx

logger = logging.getLogger(__name__)

# Modelos centralizados
from src.presentacion_reflex.state.propiedad_horizontal_models import (
    AsistenciaModel,
    AsistenciaCalendarioModel,
    PagoAdminModel,
    CalendarioDiaModel,
)

# Servicios de Aplicación Separados (SRP)
from src.aplicacion.servicios.servicio_asistencias_asambleas import (
    ServicioAsistenciasAsambleas,
)
from src.aplicacion.servicios.servicio_pagos_administracion import (
    ServicioPagosAdministracion,
)
from src.dominio.excepciones.propiedad_horizontal_error import PropiedadHorizontalError

# Infraestructura
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_asistencia_postgres import (
    RepositorioAsistenciaPostgres,
)
from src.infraestructura.persistencia.repositorio_pagos_admin_postgres import (
    RepositorioPagosAdminPostgres,
)
from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
    RepositorioPropiedadPostgres,
)
from src.infraestructura.persistencia.repositorio_asesor_postgres import (
    RepositorioAsesorPostgres,
)


class AsesorModel(pydantic.BaseModel):
    """Estructura para serialización de Asesor en UI."""

    id_asesor: int
    nombre_completo: str


class PropiedadHorizontalState(rx.State):
    """Estado centralizado para el módulo de Propiedad Horizontal."""

    is_loading: bool = False
    error_message: str = ""
    success_message: str = ""
    current_tab: str = "asambleas"

    # Datos
    asambleas: list[AsistenciaModel] = []
    asambleas_totales: int = 0
    pagos: list[PagoAdminModel] = []
    pagos_totales: int = 0
    contador_asambleas_proximas: int = 0
    contador_pagos_vencidos: int = 0
    propiedades_elegibles: list[dict] = []
    propiedades_options: list[dict[str, str]] = []
    asesores_activos: list[AsesorModel] = []

    # Búsqueda y Filtros
    busqueda_propiedad: str = ""
    busqueda_pago_propietario: str = ""
    filtro_estado_asistencia: str = "Todos"
    filtro_periodo: str = ""
    filtro_estado_pago: str = "Todos"

    # Modales
    show_modal_crear_asistencia: bool = False
    show_modal_generar_pagos: bool = False

    # Formularios
    form_data: dict = {}

    # Calendario
    vista_asambleas: str = "tabla"
    mes_seleccionado: int = 0
    año_seleccionado: int = 0
    eventos_calendario: dict[str, list[AsistenciaCalendarioModel]] = {}
    dia_seleccionado: Optional[int] = None
    eventos_dia_seleccionado: list[AsistenciaCalendarioModel] = []

    # Constantes UI
    TIPO_REUNION_OPTIONS: List[str] = [
        "Ordinaria",
        "Extraordinaria",
        "SegundaConvocatoria",
    ]
    TIPO_ASISTENTE_OPTIONS: List[str] = ["Propietario", "Inmobiliaria"]
    ESTADO_ASISTENCIA_OPTIONS: List[str] = ["Programada", "Realizada", "Cancelada"]
    ESTADO_PAGO_OPTIONS: List[str] = ["Pendiente", "Pagado", "Vencido"]

    # --- Singleton de Servicios ---
    _servicio_asambleas: ServicioAsistenciasAsambleas | None = None
    _servicio_pagos: ServicioPagosAdministracion | None = None
    _repo_asesor: RepositorioAsesorPostgres | None = None
    _propiedades_por_id: Dict[int, Dict[str, Any]] = {}  # Índice para búsquedas O(1)

    # --- Inyección de Dependencias (Factory Pattern Simplificado) ---

    def _get_servicio_asambleas(self) -> ServicioAsistenciasAsambleas:
        if PropiedadHorizontalState._servicio_asambleas is None:
            repo_asistencia = RepositorioAsistenciaPostgres(db_manager)
            repo_propiedad = RepositorioPropiedadPostgres(db_manager)
            PropiedadHorizontalState._servicio_asambleas = ServicioAsistenciasAsambleas(
                repo_asistencia, repo_propiedad
            )
        return PropiedadHorizontalState._servicio_asambleas

    def _get_servicio_pagos(self) -> ServicioPagosAdministracion:
        if PropiedadHorizontalState._servicio_pagos is None:
            repo_pagos = RepositorioPagosAdminPostgres(db_manager)
            PropiedadHorizontalState._servicio_pagos = ServicioPagosAdministracion(
                repo_pagos
            )
        return PropiedadHorizontalState._servicio_pagos

    def _get_repo_asesor(self) -> RepositorioAsesorPostgres:
        if PropiedadHorizontalState._repo_asesor is None:
            PropiedadHorizontalState._repo_asesor = RepositorioAsesorPostgres(
                db_manager
            )
        return PropiedadHorizontalState._repo_asesor

    # --- Computed Vars ---

    @rx.var
    def pagos_filtrados(self) -> List[PagoAdminModel]:
        if not self.busqueda_pago_propietario:
            return self.pagos
        busqueda = self.busqueda_pago_propietario.lower()
        return [p for p in self.pagos if busqueda in p.nombre_propietario.lower()]

    @rx.var
    def propiedades_filtradas(self) -> List[Dict]:
        if not self.busqueda_propiedad:
            return self.propiedades_options
        busqueda = self.busqueda_propiedad.lower()
        return [p for p in self.propiedades_options if busqueda in p["label"].lower()]

    @rx.var
    def es_asistente_inmobiliaria(self) -> bool:
        return self.form_data.get("tipo_asistente") == "Inmobiliaria"

    @rx.var
    def dias_mes_calendario(self) -> List[CalendarioDiaModel]:
        año = self.año_seleccionado
        mes = self.mes_seleccionado
        if not año or not mes:
            return []
        from calendar import monthrange

        primer_dia_semana, total_dias = monthrange(año, mes)
        dias = []
        dia_offset = primer_dia_semana - 1
        if dia_offset < 0:
            dia_offset = 6
        for i in range(dia_offset):
            dias.append(CalendarioDiaModel(dia=0, es_vacio=True))
        for dia in range(1, total_dias + 1):
            eventos = self.eventos_calendario.get(str(dia), [])
            dias.append(
                CalendarioDiaModel(
                    dia=dia,
                    es_vacio=False,
                    eventos=eventos,
                    tiene_eventos=len(eventos) > 0,
                )
            )
        while len(dias) < 42:
            dias.append(CalendarioDiaModel(dia=0, es_vacio=True))
        return dias[:42]

    # --- Helpers de Formateo (Extraer a Utils si crecen) ---

    def _obtener_color_tipo(self, tipo: str) -> str:
        return {
            "Ordinaria": "blue",
            "Extraordinaria": "red",
            "SegundaConvocatoria": "orange",
        }.get(tipo, "gray")

    def _obtener_color_estado_pago(self, estado: str) -> str:
        return {"Pendiente": "yellow", "Pagado": "green", "Vencido": "red"}.get(
            estado, "gray"
        )

    def _formatear_fecha(self, fecha: Any) -> str:
        if not fecha:
            return "N/A"
        try:
            if isinstance(fecha, (list, dict)):
                logger.error(
                    f"Datos corruptos en fecha (tipo inesperado): {type(fecha).__name__} - {fecha}"
                )
                return "Error Fecha"
            if isinstance(fecha, date):
                return fecha.strftime("%d/%m/%Y")
            if isinstance(fecha, str):
                try:
                    return datetime.fromisoformat(fecha).strftime("%d/%m/%Y")
                except ValueError:
                    return datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
            return str(fecha)
        except Exception as e:
            logger.error(f"Error critico de formateo de fecha: {fecha} - {e}")
            return "Error Fecha"

    def _formatear_hora(self, hora: Any) -> str:
        if not hora:
            return "N/A"
        try:
            if isinstance(hora, (list, dict)):
                logger.error(
                    f"Datos corruptos en hora (tipo inesperado): {type(hora).__name__} - {hora}"
                )
                return "Error Hora"
            if isinstance(hora, time):
                return hora.strftime("%I:%M %p")
            if isinstance(hora, str):
                try:
                    return datetime.strptime(hora, "%H:%M:%S").strftime("%I:%M %p")
                except ValueError:
                    return datetime.strptime(hora, "%H:%M").strftime("%I:%M %p")
            return str(hora)
        except Exception as e:
            logger.error(f"Error critico de formateo de hora: {hora} - {e}")
            return "Error Hora"

    def _formatear_monto(self, monto: Any) -> str:
        try:
            return f"${float(monto):,.0f}" if monto else "$0"
        except Exception as e:
            logger.warning(f"Formato de monto inválido: {monto} - {e}")
            return "$0"

    # --- Contadores de Alertas PH ---

    @rx.event(background=True)
    async def cargar_contadores_alertas(self):
        """
        Carga contadores de alertas para badges en tabs PH.
        Consulta directamente los repositorios para eficiencia.
        """
        try:
            repo_asistencia = RepositorioAsistenciaPostgres(db_manager)
            repo_pagos = RepositorioPagosAdminPostgres(db_manager)

            asambleas_hoy = repo_asistencia.listar_asambleas_hoy()
            asambleas_proximas = repo_asistencia.listar_asambleas_proximas(dias_antelacion=3)
            pagos_vencidos = repo_pagos.listar_pagos_vencidos()

            async with self:
                self.contador_asambleas_proximas = len(asambleas_hoy) + len(asambleas_proximas)
                self.contador_pagos_vencidos = len(pagos_vencidos)
        except Exception as e:
            logger.warning(f"Error cargando contadores alertas PH: {e}")

    # --- Eventos de UI ---

    def set_tab(self, tab: str):
        self.current_tab = tab
        return self.cargar_datos_tab()

    def cargar_datos_tab(self):
        if self.current_tab == "asambleas":
            return PropiedadHorizontalState.cargar_asambleas()
        return PropiedadHorizontalState.cargar_pagos()

    def set_busqueda_pago_propietario(self, valor: str):
        self.busqueda_pago_propietario = valor
        return PropiedadHorizontalState.cargar_pagos()

    def set_filtro_estado_asistencia(self, valor: str):
        self.filtro_estado_asistencia = valor
        return PropiedadHorizontalState.cargar_asambleas()

    def set_filtro_periodo(self, valor: str):
        self.filtro_periodo = valor
        return PropiedadHorizontalState.cargar_pagos()

    def set_filtro_estado_pago(self, valor: str):
        self.filtro_estado_pago = valor
        return PropiedadHorizontalState.cargar_pagos()

    @rx.event(background=True)
    async def load_initial_data(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
        try:
            servicio_pagos = self._get_servicio_pagos()
            repo_asesor = self._get_repo_asesor()

            props = servicio_pagos.obtener_propiedades_elegibles()
            asesores = repo_asesor.listar_activos()

            async with self:
                self.propiedades_elegibles = props
                PropiedadHorizontalState._propiedades_por_id = {
                    p["id_propiedad"]: p for p in props
                }
                self.propiedades_options = [
                    {
                        "value": str(p["id_propiedad"]),
                        "label": f"{p['direccion_propiedad']} - {p['nombre_propietario']}",
                    }
                    for p in props
                ]
                self.asesores_activos = [
                    AsesorModel(
                        id_asesor=a.id_asesor, nombre_completo=a.nombre_completo
                    )
                    for a in asesores
                ]
                self.current_tab = "asambleas"
                self.filtro_periodo = datetime.now().strftime("%Y-%m")
                now = datetime.now()
                self.mes_seleccionado = now.month
                self.año_seleccionado = now.year
        except Exception as e:
            async with self:
                self.error_message = f"Error inicial: {str(e)}"
        finally:
            async with self:
                self.is_loading = False
        yield PropiedadHorizontalState.cargar_asambleas()
        yield PropiedadHorizontalState.cargar_eventos_calendario()
        yield PropiedadHorizontalState.cargar_contadores_alertas()

    @rx.event(background=True)
    async def marcar_realizada(self, id_asistencia: int):
        async with self:
            self.is_loading = True
        try:
            self._get_servicio_asambleas().actualizar_estado(
                id_asistencia, "Realizada", "Administrador"
            )
            async with self:
                self.success_message = "Asamblea finalizada"
        except Exception as e:
            async with self:
                self.error_message = str(e)
        finally:
            async with self:
                self.is_loading = False
        yield PropiedadHorizontalState.cargar_asambleas()

    @rx.event(background=True)
    async def marcar_pagado(self, id_pago: int):
        async with self:
            self.is_loading = True
        try:
            self._get_servicio_pagos().marcar_como_pagado(id_pago, "Administrador")
            async with self:
                self.success_message = "Pago conciliado"
        except Exception as e:
            async with self:
                self.error_message = str(e)
        finally:
            async with self:
                self.is_loading = False
        yield PropiedadHorizontalState.cargar_pagos()

    @rx.event(background=True)
    async def eliminar_asistencia(self, id_asistencia: int):
        async with self:
            self.is_loading = True
        try:
            self._get_servicio_asambleas().eliminar_asistencia(id_asistencia)
            async with self:
                self.success_message = "Registro eliminado"
        except Exception as e:
            async with self:
                self.error_message = str(e)
        finally:
            async with self:
                self.is_loading = False
        yield PropiedadHorizontalState.cargar_asambleas()

    @rx.event
    def set_vista_asambleas(self, vista: str):
        self.vista_asambleas = vista
        if vista == "calendario":
            if not self.año_seleccionado:
                now = datetime.now()
                self.mes_seleccionado = now.month
                self.año_seleccionado = now.year

    # --- Gestión de Modales ---

    @rx.event
    def open_modal_crear_asistencia(self):
        self.show_modal_crear_asistencia = True
        self.form_data = {
            "tipo_asistente": "Propietario",
            "tipo_reunion": "Ordinaria",
            "fecha_asistencia": date.today().isoformat(),
        }
        self.busqueda_propiedad = ""

    @rx.event
    def close_modal_crear_asistencia(self):
        self.show_modal_crear_asistencia = False
        self.form_data = {}
        self.busqueda_propiedad = ""

    @rx.event
    def open_modal_generar_pagos(self):
        self.show_modal_generar_pagos = True

    @rx.event
    def close_modal_generar_pagos(self):
        self.show_modal_generar_pagos = False

    @rx.event
    def open_modal_dia_calendario(self, dia: int):
        self.dia_seleccionado = dia
        eventos = self.eventos_calendario.get(str(dia), [])
        self.eventos_dia_seleccionado = eventos

    @rx.event
    def close_modal_dia_calendario(self):
        self.dia_seleccionado = None
        self.eventos_dia_seleccionado = []

    @rx.event
    def handle_dia_modal_open_change(self, is_open: bool):
        """Maneja el cambio de estado de apertura del modal de día."""
        if not is_open:
            self.dia_seleccionado = None
            self.eventos_dia_seleccionado = []

    # --- Lógica de Formulario ---

    @rx.event
    def on_propiedad_search_change(self, valor: str):
        """Maneja la búsqueda de propiedad y auto-completa info del contrato."""
        self.busqueda_propiedad = valor
        # Buscar correspondencia exacta en etiquetas
        for opt in self.propiedades_options:
            if opt["label"] == valor:
                id_prop = int(opt["value"])
                self.form_data["id_propiedad"] = id_prop

                # Obtener info extendida del caché o servicio
                prop_info = self._propiedades_por_id.get(id_prop)
                if prop_info:
                    self.form_data["nombre_propietario_display"] = prop_info[
                        "nombre_propietario"
                    ]
                    self.form_data["direccion_asistencia"] = prop_info[
                        "direccion_propiedad"
                    ]
                break

    @rx.event
    def set_form_field(self, key: str, value: Any):
        self.form_data[key] = value

    # --- Carga de Datos (Background Events) ---

    @rx.event(background=True)
    async def cargar_asambleas(self):
        """Carga la lista de asambleas con datos completos vía JOIN."""
        async with self:
            self.is_loading = True
            estado = (
                None
                if self.filtro_estado_asistencia == "Todos"
                else self.filtro_estado_asistencia
            )

        try:
            servicio = self._get_servicio_asambleas()
            registros_enriquecidos = servicio.listar_asistencias_enriquecidas(
                filtro_estado=estado
            )

            modelos = []
            for reg in registros_enriquecidos:
                a = reg["entidad"]
                # Nombre del asistente según tipo
                if a.tipo_asistente == "Propietario":
                    nombre = reg["nombre_propietario"]
                else:
                    nombre = reg["nombre_asesor"]

                modelos.append(
                    AsistenciaModel(
                        id_asistencia=a.id_asistencia,
                        id_propiedad=a.id_propiedad,
                        direccion_propiedad=reg["direccion_propiedad"],
                        fecha_asistencia=self._formatear_fecha(a.fecha_asistencia),
                        hora_asistencia=self._formatear_hora(a.hora_asistencia),
                        tipo_reunion=a.tipo_reunion,
                        tipo_asistente=a.tipo_asistente,
                        nombre_asistente=nombre,
                        costo_asistente=float(a.costo_asistente),
                        direccion_asistencia=a.direccion_asistencia,
                        estado_asistencia=a.estado_asistencia,
                        color_tipo=self._obtener_color_tipo(a.tipo_reunion),
                        tooltip_asistencia=f"Asamblea {a.tipo_reunion} en {a.direccion_asistencia}",
                    )
                )

            async with self:
                self.asambleas = modelos
                self.asambleas_totales = len(modelos)
        except Exception as e:
            logger.error(f"Error cargando asambleas: {e}")
            async with self:
                self.error_message = f"Error al cargar asambleas: {str(e)}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def cargar_pagos(self):
        """Carga la lista de pagos de administración."""
        async with self:
            self.is_loading = True
            periodo = self.filtro_periodo
            estado = (
                None if self.filtro_estado_pago == "Todos" else self.filtro_estado_pago
            )
            nombre_busqueda = self.busqueda_pago_propietario or None

        try:
            servicio = self._get_servicio_pagos()
            pagos_ent = servicio.listar_pagos(
                filtro_periodo=periodo,
                filtro_estado=estado,
                filtro_nombre=nombre_busqueda,
            )

            modelos = [
                PagoAdminModel(
                    id_pago_admin=p.id_pago_admin,
                    id_propiedad=p.id_propiedad,
                    nombre_propietario=p.nombre_propietario,
                    direccion_propiedad=p.direccion_propiedad,
                    valor_administracion=float(p.valor_administracion),
                    valor_formateado=self._formatear_monto(p.valor_administracion),
                    fecha_pago=p.fecha_pago,
                    link_pago=p.link_pago or "",
                    periodo_pago=p.periodo_pago,
                    estado_pago=p.estado_pago,
                    color_estado=self._obtener_color_estado_pago(p.estado_pago),
                    tooltip_pago=f"Administración {p.periodo_pago} - {p.direccion_propiedad}",
                )
                for p in pagos_ent
            ]

            async with self:
                self.pagos = modelos
                self.pagos_totales = len(modelos)
        except Exception as e:
            logger.error(f"Error cargando pagos: {e}")
            async with self:
                self.error_message = f"Error al cargar pagos: {str(e)}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def cargar_eventos_calendario(self):
        """Carga eventos para la vista calendario con datos completos vía JOIN."""
        async with self:
            año = self.año_seleccionado
            mes = self.mes_seleccionado
            if not año or not mes:
                return

        try:
            servicio = self._get_servicio_asambleas()
            eventos_dict = servicio.obtener_calendario_mes_enriquecido(año, mes)

            # Mapear a modelos de calendario para cada día
            calendario_procesado = {}
            for día, registros in eventos_dict.items():
                modelos_dia = []
                for reg in registros:
                    a = reg["entidad"]
                    if a.tipo_asistente == "Propietario":
                        nombre = reg["nombre_propietario"]
                    else:
                        nombre = reg["nombre_asesor"]

                    modelos_dia.append(
                        AsistenciaCalendarioModel(
                            id_asistencia=a.id_asistencia,
                            id_propiedad=a.id_propiedad,
                            direccion_propiedad=reg["direccion_propiedad"],
                            fecha_asistencia=self._formatear_fecha(a.fecha_asistencia),
                            hora_asistencia=self._formatear_hora(a.hora_asistencia),
                            tipo_reunion=a.tipo_reunion,
                            tipo_asistente=a.tipo_asistente,
                            nombre_asistente=nombre,
                            costo_asistente=0,
                            direccion_asistencia=a.direccion_asistencia,
                            estado_asistencia=a.estado_asistencia,
                            color_tipo=self._obtener_color_tipo(a.tipo_reunion),
                        )
                    )
                calendario_procesado[str(día)] = modelos_dia

            async with self:
                self.eventos_calendario = calendario_procesado
        except Exception as e:
            logger.error(f"Error calendario: {e}")
            async with self:
                self.error_message = f"Error al cargar calendario: {str(e)}"

    # --- Navegación Calendario ---

    @rx.event(background=True)
    async def navigate_mes_anterior(self):
        async with self:
            if self.mes_seleccionado == 1:
                self.mes_seleccionado = 12
                self.año_seleccionado -= 1
            else:
                self.mes_seleccionado -= 1
        yield PropiedadHorizontalState.cargar_eventos_calendario()

    @rx.event(background=True)
    async def navigate_mes_siguiente(self):
        async with self:
            if self.mes_seleccionado == 12:
                self.mes_seleccionado = 1
                self.año_seleccionado += 1
            else:
                self.mes_seleccionado += 1
        yield PropiedadHorizontalState.cargar_eventos_calendario()

    # --- Acciones de Negocio (Escritura) ---

    @rx.event(background=True)
    async def guardar_asistencia(self):
        """Persiste una nueva asistencia a asamblea."""
        async with self:
            self.is_loading = True
            datos = self.form_data.copy()
            # Asegurar id de asesor si aplica
            if self.es_asistente_inmobiliaria:
                datos["id_asesor_seleccionado"] = self.form_data.get(
                    "id_asesor_seleccionado"
                )

        try:
            servicio = self._get_servicio_asambleas()
            servicio.crear_asistencia(datos, "Administrador")

            async with self:
                self.success_message = "Asistencia programada correctamente"
                self.show_modal_crear_asistencia = False
        except Exception as e:
            async with self:
                self.error_message = str(e)
        finally:
            async with self:
                self.is_loading = False

        yield PropiedadHorizontalState.cargar_asambleas()

    @rx.event(background=True)
    async def generar_pagos_mes(self):
        """Genera masivamente los pagos para el periodo seleccionado."""
        async with self:
            self.is_loading = True
            periodo = self.filtro_periodo

        try:
            servicio = self._get_servicio_pagos()
            resultado = servicio.generar_pagos_mes(periodo, "Administrador")

            async with self:
                self.success_message = f"Generación completada: {resultado['exitosos']} exitosos, {resultado['fallidos']} fallidos."
                self.show_modal_generar_pagos = False
        except Exception as e:
            async with self:
                self.error_message = str(e)
        finally:
            async with self:
                self.is_loading = False

        yield PropiedadHorizontalState.cargar_pagos()
