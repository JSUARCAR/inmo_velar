import reflex as rx

from src.aplicacion.servicios.servicio_incidentes import ServicioIncidentes
from src.infraestructura.persistencia.database import db_manager


class IncidentesEventHandlers:
    """Event handlers para carga de datos de incidentes."""

    @rx.event(background=True)
    async def on_load(self):
        """Carga inicial."""
        async with self:
            self.is_loading = True

        try:
            yield IncidentesState.load_incidentes()
            yield IncidentesState.load_propiedades()
            yield IncidentesState.load_proveedores()
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def load_propiedades(self):
        """Carga lista de propiedades para el formulario."""
        async with self:
            self.is_loading = True

        try:
            from src.aplicacion.servicios.servicio_propiedad import ServicioPropiedad

            servicio = ServicioPropiedad(db_manager)
            propiedades = servicio.listar_propiedades()

            opciones = []
            for prop in propiedades:
                direccion = (
                    prop.direccion_propiedad
                    if hasattr(prop, "direccion_propiedad")
                    else str(prop)
                )
                opciones.append(
                    {
                        "id": prop.id_propiedad,
                        "texto": f"{prop.id_propiedad} - {direccion}",
                    }
                )

            async with self:
                self.propiedades_options = opciones
        except Exception as e:
            async with self:
                self.error_message = f"Error cargando propiedades: {str(e)}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def load_incidentes(self):
        """Carga lista de incidentes con soporte de filtros y paginacion."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = ServicioIncidentes(db_manager)

            filtros = {}
            if self.filter_estado != "Todos":
                filtros["estado"] = self.filter_estado
            if self.filter_prioridad != "Todas":
                filtros["prioridad"] = self.filter_prioridad
            if self.search_text:
                filtros["busqueda"] = self.search_text

            filtros["page"] = self.page
            filtros["page_size"] = self.items_per_page

            resultado = servicio.listar_con_filtros(**filtros)
            items = resultado.get("items", [])
            total_items = resultado.get("total", 0)

            incidents_data = []
            for inc in items:
                prop = getattr(inc, "id_propiedad", 0)
                desc = getattr(inc, "descripcion_incidente", "")
                estado = getattr(inc, "estado", "Reportado")
                prioridad = getattr(inc, "prioridad", "Media")
                fecha = getattr(inc, "fecha_incidente", datetime.now())
                if hasattr(fecha, "strftime"):
                    fecha_str = fecha.strftime("%Y-%m-%d")
                else:
                    fecha_str = str(fecha)

                incidents_data.append(
                    {
                        "id": inc.id_incidente,
                        "descripcion": desc[:80] + "..." if len(desc) > 80 else desc,
                        "estado": estado,
                        "prioridad": prioridad,
                        "fecha": fecha_str,
                        "id_propiedad": prop,
                        "direccion_propiedad": f"#{prop}",
                        "id_proveedor": inc.id_proveedor_asignado,
                        "origen": getattr(inc, "origen_reporte", "Inquilino"),
                    }
                )

            kanban_grouped = {
                "Reportado": [],
                "Cotizado": [],
                "Aprobado": [],
                "En Reparacion": [],
                "Finalizado": [],
            }

            for item in incidents_data:
                estado_incidente = item["estado"]
                for col_name, status_list in self.kanban_columns.items():
                    if estado_incidente in status_list:
                        kanban_grouped[col_name].append(item)
                        break

            async with self:
                self.incidentes = items
                self.incidentes_kanban = kanban_grouped

                import math

                self.total_pages = math.ceil(total_items / self.items_per_page)
                if self.total_pages < 1:
                    self.total_pages = 1
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar incidentes: {str(e)}"
        finally:
            async with self:
                self.is_loading = False


from datetime import datetime
