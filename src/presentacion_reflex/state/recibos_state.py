
import reflex as rx
from typing import List, Dict, Optional, Any
from datetime import datetime, date

from src.aplicacion.servicios.servicio_recibos_publicos import ServicioRecibosPublicos
from src.aplicacion.servicios.servicio_propiedades import ServicioPropiedades
from src.infraestructura.persistencia.database import DatabaseManager, db_manager
from src.infraestructura.repositorios.repositorio_recibo_publico_sqlite import RepositorioReciboPublicoSQLite
from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite

class RecibosState(rx.State):
    """Estado para la gestión de Recibos Públicos."""
    
    # Datos Principales
    recibos: List[Dict] = []
    total_items: int = 0
    is_loading: bool = False
    error_message: str = ""
    
    # Filtros
    filter_propiedad: str = "" # ID en string para buscar
    filter_periodo_inicio: str = ""
    filter_periodo_fin: str = ""
    filter_servicio: str = "Todos"
    filter_estado: str = "Todos"
    search_text: str = ""
    
    # Paginación
    current_page: int = 1
    page_size: int = 10
    
    # Formulario (Crear/Editar)
    show_form_modal: bool = False
    is_editing: bool = False
    form_data: Dict[str, Any] = {
        "id_recibo": None,
        "id_propiedad": "",
        "periodo_recibo": "",
        "tipo_servicio": "",
        "valor_recibo": 0,
        "fecha_vencimiento": "",
        "observaciones": ""
    }
    
    # Modal Pago
    show_payment_modal: bool = False
    payment_data: Dict[str, Any] = {
        "id_recibo": None,
        "fecha_pago": date.today().isoformat(),
        "comprobante": ""
    }
    
    # Datos Auxiliares
    propiedades_disponibles: List[Dict] = [] # Para selects: {label: "Calle 123", value: "1"}
    
    @rx.event(background=True)
    async def on_load(self):
        """Carga inicial de datos."""
        yield RecibosState.load_propiedades_options
        yield RecibosState.load_data

    @rx.event(background=True)
    async def load_propiedades_options(self):
        """Carga opciones de propiedades para selects."""
        try:
            repo_prop = RepositorioPropiedadSQLite(db_manager)
            servicio_prop = ServicioPropiedades(db_manager)
            props = servicio_prop.listar_propiedades()
            
            options = [
                {"label": f"{p.direccion_propiedad} ({p.matricula_inmobiliaria})", "value": str(p.id_propiedad)}
                for p in props
            ]
            async with self:
                self.propiedades_disponibles = options
        except Exception as e:
            print(f"Error cargando propiedades: {e}")

    @rx.event(background=True)
    async def load_data(self):
        """Carga la lista de recibos con filtros."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            
        try:
            repo_recibo = RepositorioReciboPublicoSQLite(db_manager)
            repo_prop = RepositorioPropiedadSQLite(db_manager)
            servicio = ServicioRecibosPublicos(repo_recibo, repo_prop)
            
            # Preparar filtros
            id_prop = int(self.filter_propiedad) if self.filter_propiedad and self.filter_propiedad != "Todos" else None
            tipo = self.filter_servicio if self.filter_servicio != "Todos" else None
            estado = self.filter_estado if self.filter_estado != "Todos" else None
            p_ini = self.filter_periodo_inicio if self.filter_periodo_inicio else None
            p_fin = self.filter_periodo_fin if self.filter_periodo_fin else None
            
            # Obtener datos
            resultados = servicio.listar_con_filtros(
                id_propiedad=id_prop,
                periodo_inicio=p_ini,
                periodo_fin=p_fin,
                tipo_servicio=tipo,
                estado=estado
            )
            
            # Enriquecer datos para UI (Propiedad nombre, etc)
            recibos_ui = []
            for r in resultados:
                prop_nombre = "Desconocida"
                # Optimización: Podríamos hacer un join en repo, pero por ahora buscamos en lista cargada o repo
                # Buscar en self.propiedades_disponibles es más rápido si ya se cargaron
                prop_item = next((p for p in self.propiedades_disponibles if p["value"] == str(r.id_propiedad)), None)
                if prop_item:
                    prop_nombre = prop_item["label"]
                
                recibos_ui.append({
                    "id_recibo_publico": r.id_recibo_publico,
                    "id_propiedad": r.id_propiedad,
                    "propiedad_nombre": prop_nombre,
                    "periodo_recibo": r.periodo_recibo,
                    "tipo_servicio": r.tipo_servicio,
                    "valor_recibo": r.valor_recibo,
                    "valor_formato": f"${r.valor_recibo:,.0f}",
                    "fecha_vencimiento": r.fecha_vencimiento,
                    "fecha_pago": r.fecha_pago,
                    "comprobante": r.comprobante,
                    "estado": r.estado,
                    "esta_vencido": r.esta_vencido,
                    "fecha_desde": r.fecha_desde,
                    "fecha_hasta": r.fecha_hasta,
                    "dias_facturados": r.dias_facturados,
                    "clase_estado": "red" if r.esta_vencido and r.estado != "Pagado" else ("green" if r.estado == "Pagado" else "yellow")
                })
            
            # Filtrado texto en memoria (si aplica)
            if self.search_text:
                st = self.search_text.lower()
                recibos_ui = [
                    r for r in recibos_ui 
                    if st in r["propiedad_nombre"].lower() or st in r["comprobante"].lower()
                ]

            async with self:
                self.recibos = recibos_ui
                self.total_items = len(recibos_ui)
                self.is_loading = False
                
        except Exception as e:
            async with self:
                self.error_message = f"Error cargando datos: {str(e)}"
                self.is_loading = False

    # --- CRUD ACTIONS ---
    
    def open_create_modal(self):
        self.is_editing = False
        self.form_data = {
            "id_recibo": None,
            "id_propiedad": "",
            "periodo_recibo": date.today().strftime("%Y-%m"),
            "tipo_servicio": "Agua",
            "valor_recibo": 0,
            "fecha_vencimiento": date.today().isoformat(),
            "fecha_desde": date.today().isoformat(),
            "fecha_hasta": date.today().isoformat(),
            "dias_facturados": 0,
        }
        self.show_form_modal = True

    def open_edit_modal(self, recibo: Dict):
        if recibo["estado"] == "Pagado":
            return # No editar pagados
            
        self.is_editing = True
        self.form_data = {
            "id_recibo": recibo["id_recibo_publico"],
            "id_propiedad": str(recibo["id_propiedad"]),
            "periodo_recibo": recibo["periodo_recibo"],
            "tipo_servicio": recibo["tipo_servicio"],
            "valor_recibo": recibo["valor_recibo"],
            "fecha_vencimiento": recibo["fecha_vencimiento"],
            "fecha_desde": recibo.get("fecha_desde", ""),
            "fecha_hasta": recibo.get("fecha_hasta", ""),
            "dias_facturados": recibo.get("dias_facturados", 0),
        }
        self.show_form_modal = True
        
        self.show_form_modal = True

    def handle_form_open_change(self, is_open: bool):
        if not is_open:
            self.show_form_modal = False
        
    def calculate_days(self):
        """Calcula diferencia de días en el form."""
        f_desde = self.form_data.get("fecha_desde")
        f_hasta = self.form_data.get("fecha_hasta")
        
        if f_desde and f_hasta:
            try:
                d1 = date.fromisoformat(f_desde)
                d2 = date.fromisoformat(f_hasta)
                diff = (d2 - d1).days
                self.form_data["dias_facturados"] = diff
            except:
                self.form_data["dias_facturados"] = 0
                
    def set_form_field(self, field: str, value: Any):
        self.form_data[field] = value
        if field in ["fecha_desde", "fecha_hasta"]:
            self.calculate_days()
        
    @rx.event(background=True)
    async def save_recibo(self):
        """Guarda o actualiza el recibo."""
        async with self:
            self.is_loading = True
            
        try:
            repo_recibo = RepositorioReciboPublicoSQLite(db_manager)
            repo_prop = RepositorioPropiedadSQLite(db_manager)
            servicio = ServicioRecibosPublicos(repo_recibo, repo_prop)
            
            datos = self.form_data.copy()
            usuario = "admin" # TODO
            
            # Convertir tipos
            if not datos["id_propiedad"]:
                raise ValueError("Seleccione una propiedad")
            datos["id_propiedad"] = int(datos["id_propiedad"])
            try:
                datos["valor_recibo"] = int(datos["valor_recibo"])
            except:
                raise ValueError("Valor inválido")

            if self.is_editing:
                servicio.actualizar_recibo(datos["id_recibo"], datos, usuario)
            else:
                servicio.registrar_recibo(datos, usuario)
            
            async with self:
                self.show_form_modal = False
                self.is_loading = False
            
            yield RecibosState.load_data
            
        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False

    # --- PAYMENT ACTIONS ---
    
    def open_payment_modal(self, recibo: Dict):
        self.payment_data = {
            "id_recibo": recibo["id_recibo_publico"],
            "fecha_pago": date.today().isoformat(),
            "comprobante": ""
        }
        self.show_payment_modal = True

    def handle_payment_open_change(self, is_open: bool):
        if not is_open:
            self.show_payment_modal = False

    def set_payment_field(self, field: str, value: Any):
        self.payment_data[field] = value

    @rx.event(background=True)
    async def register_payment(self):
        async with self:
            self.is_loading = True
            
        try:
            repo_recibo = RepositorioReciboPublicoSQLite(db_manager)
            repo_prop = RepositorioPropiedadSQLite(db_manager)
            servicio = ServicioRecibosPublicos(repo_recibo, repo_prop)
            
            servicio.marcar_como_pagado(
                self.payment_data["id_recibo"],
                self.payment_data["fecha_pago"],
                self.payment_data["comprobante"],
                "admin"
            )
            
            async with self:
                self.show_payment_modal = False
                self.is_loading = False
            yield RecibosState.load_data
            
        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False

    # --- DETAIL & DELETE ACTIONS ---
    
    show_detail_modal: bool = False
    detail_data: Dict[str, Any] = {}
    
    def open_detail_modal(self, recibo: Dict):
        self.detail_data = recibo
        self.show_detail_modal = True
        
    def handle_detail_open_change(self, is_open: bool):
        if not is_open:
            self.show_detail_modal = False

    @rx.event(background=True)
    async def delete_recibo(self, id_recibo: int):
        """Elimina un recibo dado su ID."""
        async with self:
            self.is_loading = True
            
        try:
            repo_recibo = RepositorioReciboPublicoSQLite(db_manager)
            repo_prop = RepositorioPropiedadSQLite(db_manager)
            servicio = ServicioRecibosPublicos(repo_recibo, repo_prop)
            
            servicio.eliminar_recibo(id_recibo)
            
            async with self:
                self.is_loading = False
                rx.toast.success("Recibo eliminado correctamente")
            
            yield RecibosState.load_data
            
        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False
                rx.toast.error(f"Error al eliminar: {str(e)}")

    # --- FILTERS ---
    
    def set_filter_propiedad(self, value: str):
        self.filter_propiedad = value
        
    def set_filter_servicio(self, value: str):
        self.filter_servicio = value

    def set_filter_estado(self, value: str):
        self.filter_estado = value
        
    def set_search(self, value: str):
        self.search_text = value
        
