from typing import Dict, List, Optional, TypedDict

import reflex as rx

from src.aplicacion.servicios.servicio_personas import ServicioPersonas
from src.infraestructura.persistencia.database import db_manager
from src.presentacion_reflex.state.auth_state import AuthState


class PersonaDict(TypedDict):
    """Estructura tipada para serialización de Persona en Reflex."""

    id: int
    nombre: str
    documento: str
    tipo_documento: str
    numero_documento: str
    contacto: str
    telefono: Optional[str]
    correo: str
    direccion: str
    roles: List[str]
    estado: str
    fecha_creacion: str


class PersonasState(rx.State):
    """Estado para la gestión de Personas."""

    # --- Datos de la Tabla ---
    personas: List[PersonaDict] = []
    total_items: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 1

    # --- Filtros ---
    search_query: str = ""
    filtro_rol: str = "Todos"
    fecha_inicio: str = ""
    fecha_fin: str = ""

    # --- UI State ---
    is_loading: bool = False

    # --- Modal State ---
    show_modal: bool = False
    is_editing: bool = False
    current_persona_id: Optional[int] = None

    # --- Form State ---
    form_data: Dict[str, str] = {}
    error_message: str = ""

    # --- Role Management ---
    selected_roles: List[str] = []  # Changed from single string to List
    available_roles: List[str] = ["Propietario", "Arrendatario", "Codeudor", "Asesor", "Proveedor"]

    # --- Elite UX Features ---
    view_mode: str = "table"  # "table" or "cards"
    modal_step: int = 1  # Wizard step (1, 2, 3)
    form_validation_errors: Dict[str, str] = {}  # Field-level validation errors

    def load_personas(self):
        """Carga la lista de personas aplicando filtros y paginación."""
        self.is_loading = True
        try:
            from src.infraestructura.persistencia.repositorio_persona_sqlite import (
                RepositorioPersonaSQLite,
            )
            from src.infraestructura.persistencia.repositorio_propietario_sqlite import (
                RepositorioPropietarioSQLite,
            )
            from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import (
                RepositorioArrendatarioSQLite,
            )
            from src.infraestructura.persistencia.repositorio_codeudor_sqlite import (
                RepositorioCodeudorSQLite,
            )
            from src.infraestructura.persistencia.repositorio_asesor_sqlite import (
                RepositorioAsesorSQLite,
            )
            from src.infraestructura.persistencia.repositorio_proveedores_sqlite import (
                RepositorioProveedoresSQLite,
            )

            repo_persona = RepositorioPersonaSQLite(db_manager)
            repo_propietario = RepositorioPropietarioSQLite(db_manager)
            repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
            repo_codeudor = RepositorioCodeudorSQLite(db_manager)
            repo_asesor = RepositorioAsesorSQLite(db_manager)
            repo_proveedor = RepositorioProveedoresSQLite(db_manager)

            servicio = ServicioPersonas(
                repo_persona=repo_persona,
                repo_propietario=repo_propietario,
                repo_arrendatario=repo_arrendatario,
                repo_codeudor=repo_codeudor,
                repo_asesor=repo_asesor,
                repo_proveedor=repo_proveedor,
            )

            # Mapear filtro "Todos" a None
            rol_filter = self.filtro_rol if self.filtro_rol != "Todos" else None

            # Obtener resultado paginado
            resultado = servicio.listar_personas_paginado(
                page=self.page,
                page_size=self.page_size,
                filtro_rol=rol_filter,
                busqueda=self.search_query if self.search_query else None,
                fecha_inicio=self.fecha_inicio if self.fecha_inicio else None,
                fecha_fin=self.fecha_fin if self.fecha_fin else None,
            )

            self.total_items = resultado.total

            # Convertir objetos a diccionarios para serialización Reflex
            self.personas = [
                {
                    "id": p.persona.id_persona,
                    "nombre": p.nombre_completo,
                    "documento": f"{p.persona.tipo_documento} {p.numero_documento}",
                    "tipo_documento": p.persona.tipo_documento,
                    "numero_documento": p.persona.numero_documento,
                    "contacto": p.telefono_principal or "N/A",
                    "telefono": p.persona.telefono_principal,
                    "correo": p.correo_principal or "",
                    "direccion": p.persona.direccion_principal or "",
                    "roles": p.roles,
                    "estado": "Activo" if p.esta_activa else "Inactivo",
                    "fecha_creacion": p.persona.created_at[:10] if p.persona.created_at else "N/A",
                }
                for p in resultado.items
            ]

            # Calcular total páginas
            self.total_pages = (self.total_items + self.page_size - 1) // self.page_size
            if self.total_pages < 1:
                self.total_pages = 1

        except Exception:
            pass  # print(f"Error cargando personas: {e}") [OpSec Removed]
            self.personas = []
        finally:
            self.is_loading = False

    def set_search(self, query: str):
        """Actualiza búsqueda y recarga."""
        self.search_query = query
        self.page = 1
        self.load_personas()

    def set_filtro_rol(self, rol: str):
        """Actualiza filtro de rol."""
        self.filtro_rol = rol
        self.page = 1
        self.load_personas()

    def set_fecha_inicio(self, fecha: str):
        """Actualiza fecha inicio y recarga."""
        self.fecha_inicio = fecha
        self.page = 1
        self.load_personas()

    def set_fecha_fin(self, fecha: str):
        """Actualiza fecha fin y recarga."""
        self.fecha_fin = fecha
        self.page = 1
        self.load_personas()

    def exportar_csv(self):
        """Exporta los datos filtrados a CSV y descarga el archivo."""
        pass  # print("[DEBUG_EXPORT] Iniciando proceso de exportación CSV") [OpSec Removed]
        try:
            yield rx.toast.info("Generando archivo...", position="bottom-right")

            from src.infraestructura.persistencia.repositorio_persona_sqlite import (
                RepositorioPersonaSQLite,
            )
            from src.infraestructura.persistencia.repositorio_propietario_sqlite import (
                RepositorioPropietarioSQLite,
            )
            from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import (
                RepositorioArrendatarioSQLite,
            )
            from src.infraestructura.persistencia.repositorio_codeudor_sqlite import (
                RepositorioCodeudorSQLite,
            )
            from src.infraestructura.persistencia.repositorio_asesor_sqlite import (
                RepositorioAsesorSQLite,
            )
            from src.infraestructura.persistencia.repositorio_proveedores_sqlite import (
                RepositorioProveedoresSQLite,
            )

            repo_persona = RepositorioPersonaSQLite(db_manager)
            repo_propietario = RepositorioPropietarioSQLite(db_manager)
            repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
            repo_codeudor = RepositorioCodeudorSQLite(db_manager)
            repo_asesor = RepositorioAsesorSQLite(db_manager)
            repo_proveedor = RepositorioProveedoresSQLite(db_manager)

            servicio = ServicioPersonas(
                repo_persona=repo_persona,
                repo_propietario=repo_propietario,
                repo_arrendatario=repo_arrendatario,
                repo_codeudor=repo_codeudor,
                repo_asesor=repo_asesor,
                repo_proveedor=repo_proveedor,
            )
            rol_filter = self.filtro_rol if self.filtro_rol != "Todos" else None

            pass  # print(f"[DEBUG_EXPORT] Filtros - Rol: {rol_filter}, Busqueda: {self.search_query}") [OpSec Removed]

            # Obtener datos CSV
            csv_data = servicio.exportar_personas_csv(
                filtro_rol=rol_filter,
                busqueda=self.search_query if self.search_query else None,
                fecha_inicio=self.fecha_inicio if self.fecha_inicio else None,
                fecha_fin=self.fecha_fin if self.fecha_fin else None,
            )

            data_len = len(csv_data)
            pass  # print(f"[DEBUG_EXPORT] Datos CSV generados. Longitud: {data_len} bytes") [OpSec Removed]

            if (
                data_len < 10
            ):  # Simple check for empty or header-only file issues (less likely with stringio but good to print)
                pass  # print("[DEBUG_EXPORT] ADVERTENCIA: El archivo CSV parece muy pequeño.") [OpSec Removed]

            # Use direct data download to avoid static file serving issues
            # We skip writing to disk completely to prevent 404/HTML errors

            # Encode to bytes with BOM for Excel compatibility if it's a string
            if isinstance(csv_data, str):
                data_bytes = csv_data.encode("utf-8-sig")
            else:
                data_bytes = csv_data

            data_len = len(data_bytes)
            pass  # print(f"[DEBUG_EXPORT] Iniciando descarga directa ({data_len} bytes)") [OpSec Removed]

            if data_len < 10:
                pass  # print("[DEBUG_EXPORT] ADVERTENCIA: El archivo a descargar parece vacio.") [OpSec Removed]

            # Usar rx.download con DATA para enviar el contenido directamente
            # Esto evita depender de la carpeta .web/public o assets

            import time

            timestamp = int(time.time())
            filename = f"personas_export_{timestamp}.csv"

            yield rx.download(data=data_bytes, filename=filename)

            yield rx.toast.success("Descarga iniciada", position="bottom-right")

        except Exception as e:
            pass  # print(f"[DEBUG_EXPORT] ERROR: {e}") [OpSec Removed]
            import traceback

            traceback.print_exc()
            yield rx.toast.error(f"Error al exportar: {str(e)}", position="bottom-right")

    def next_page(self):
        if self.page < self.total_pages:
            self.page += 1
            self.load_personas()

    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.load_personas()

    # --- Role Management Logic ---

    def toggle_rol(self, rol: str, checked: bool):
        """Toggles a role in the selected_roles list."""
        pass  # print(f"🔄 Toggle Rol: {rol} -> {checked}") [OpSec Removed]
        if checked:
            if rol not in self.selected_roles:
                self.selected_roles.append(rol)
        else:
            if rol in self.selected_roles:
                self.selected_roles.remove(rol)
        pass  # print(f"✅ Current roles: {self.selected_roles}") [OpSec Removed]

    def is_rol_selected(self, rol: str) -> bool:
        """Helper for UI to check if role is selected."""
        return rol in self.selected_roles

    # --- Computed vars for role checking (for UI conditional rendering) ---

    @rx.var
    def is_propietario_selected(self) -> bool:
        """Check if Propietario role is selected."""
        return "Propietario" in self.selected_roles

    @rx.var
    def is_arrendatario_selected(self) -> bool:
        """Check if Arrendatario role is selected."""
        return "Arrendatario" in self.selected_roles

    @rx.var
    def is_asesor_selected(self) -> bool:
        """Check if Asesor role is selected."""
        return "Asesor" in self.selected_roles

    @rx.var
    def is_proveedor_selected(self) -> bool:
        """Check if Proveedor role is selected."""
        return "Proveedor" in self.selected_roles

    # --- Elite UX Methods ---

    def toggle_view_mode(self):
        """Toggle between table and cards view."""
        self.view_mode = "cards" if self.view_mode == "table" else "table"

    def next_modal_step(self):
        """Advance to next wizard step."""
        if self.modal_step < 3:
            self.modal_step += 1

    def handle_form_submit(self, form_data: dict):
        """Handle form submission for all wizard steps."""
        pass  # print(f"📝 Form submitted at step {self.modal_step}") [OpSec Removed]
        pass  # print(f"Received form data: {form_data}") [OpSec Removed]

        # Merge new form data with existing data
        self.form_data.update(form_data)
        pass  # print(f"Updated form_data: {self.form_data}") [OpSec Removed]

        # Decide what to do based on current step
        if self.modal_step < 3:
            # Steps 1-2: Save data and advance to next step
            self.modal_step += 1
            pass  # print(f"✅ Advanced to step {self.modal_step}") [OpSec Removed]
        else:
            # Step 3: Final save to database (background task requires yield)
            pass  # print("💾 Calling save_persona for final save") [OpSec Removed]
            yield PersonasState.save_persona(self.form_data)

    def prev_modal_step(self):
        """Go back to previous wizard step."""
        if self.modal_step > 1:
            self.modal_step -= 1

    def reset_wizard(self):
        """Reset wizard to step 1."""
        self.modal_step = 1
        self.form_validation_errors = {}

    # --- Input Handling ---

    def set_upper(self, field: str, value: str):
        """Establece el valor del campo en mayúsculas."""
        self.form_data[field] = value.upper()

    # --- Modal Logic ---

    def open_create_modal(self):
        """Abre modal para crear nueva persona."""
        pass  # print("\n🔵 OPEN_CREATE_MODAL called") [OpSec Removed]
        self.is_editing = False
        self.current_persona_id = None
        # Inicializar con claves vacías para evitar errores de binding
        self.form_data = {
            "nombre_completo": "",
            "correo_electronico": "",
            "direccion_principal": "",
            "numero_documento": "",
            "telefono_principal": "",
            "tipo_documento": "CC",
            "consignatario": "",
            "documento_consignatario": "",
        }
        self.error_message = ""
        self.selected_roles = []  # Reset roles
        self.reset_wizard()  # Reset wizard to step 1
        self.show_modal = True
        pass  # print("✅ Modal state set to True") [OpSec Removed]

    def open_edit_modal(self, persona: Dict):
        """Abre modal para editar persona existente con todos sus datos."""
        try:
            self.is_editing = True
            self.current_persona_id = persona["id"]

            # 1. Obtener datos completos desde el servicio (incluyendo roles)
            from src.infraestructura.persistencia.repositorio_persona_sqlite import (
                RepositorioPersonaSQLite,
            )
            from src.infraestructura.persistencia.repositorio_propietario_sqlite import (
                RepositorioPropietarioSQLite,
            )
            from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import (
                RepositorioArrendatarioSQLite,
            )
            from src.infraestructura.persistencia.repositorio_codeudor_sqlite import (
                RepositorioCodeudorSQLite,
            )
            from src.infraestructura.persistencia.repositorio_asesor_sqlite import (
                RepositorioAsesorSQLite,
            )
            from src.infraestructura.persistencia.repositorio_proveedores_sqlite import (
                RepositorioProveedoresSQLite,
            )

            repo_persona = RepositorioPersonaSQLite(db_manager)
            repo_propietario = RepositorioPropietarioSQLite(db_manager)
            repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
            repo_codeudor = RepositorioCodeudorSQLite(db_manager)
            repo_asesor = RepositorioAsesorSQLite(db_manager)
            repo_proveedor = RepositorioProveedoresSQLite(db_manager)

            servicio = ServicioPersonas(
                repo_persona=repo_persona,
                repo_propietario=repo_propietario,
                repo_arrendatario=repo_arrendatario,
                repo_codeudor=repo_codeudor,
                repo_asesor=repo_asesor,
                repo_proveedor=repo_proveedor,
            )
            persona_completa = servicio.obtener_persona_completa(self.current_persona_id)

            if not persona_completa:
                self.error_message = "Error: La persona no se encuentra en la base de datos."
                self.show_modal = True
                return

            p_entidad = persona_completa.persona


            # 2. Cargar datos básicos (con conversion a mayúsculas si aplica)
            self.form_data = {
                "nombre_completo": (p_entidad.nombre_completo or "").upper(),
                "tipo_documento": p_entidad.tipo_documento or "CC",
                "numero_documento": p_entidad.numero_documento,
                "telefono_principal": p_entidad.telefono_principal or "",
                "correo_electronico": (p_entidad.correo_electronico or "").upper(),
                "direccion_principal": (p_entidad.direccion_principal or "").upper(),
            }

            # 3. Cargar roles activos
            self.selected_roles = persona_completa.roles if persona_completa.roles else []
            pass  # print(f"Loaded roles: {self.selected_roles}") [OpSec Removed]

            # Cargar datos de cada rol al form_data
            datos_roles = persona_completa.datos_roles

            if "Propietario" in datos_roles:
                prop = datos_roles["Propietario"]
                self.form_data.update(
                    {
                        "banco_propietario": prop.banco_propietario or "",
                        "numero_cuenta_propietario": prop.numero_cuenta_propietario or "",
                        "tipo_cuenta": prop.tipo_cuenta or "",
                        "observaciones_propietario": prop.observaciones_propietario or "",
                        "consignatario": prop.consignatario or "",
                        "documento_consignatario": prop.documento_consignatario or "",
                    }
                )

            if "Arrendatario" in datos_roles:
                arr = datos_roles["Arrendatario"]
                self.form_data.update(
                    {
                        "codigo_aprobacion_seguro": arr.codigo_aprobacion_seguro or "",
                        "id_seguro": str(arr.id_seguro) if arr.id_seguro else "",
                    }
                )

            if "Asesor" in datos_roles:
                ase = datos_roles["Asesor"]
                self.form_data.update(
                    {
                        "comision_porcentaje_arriendo": str(ase.comision_porcentaje_arriendo),
                        "comision_porcentaje_venta": str(ase.comision_porcentaje_venta),
                        "fecha_vinculacion": ase.fecha_ingreso or "",
                    }
                )

            if "Proveedor" in datos_roles:
                prov = datos_roles["Proveedor"]
                self.form_data.update(
                    {
                        "especialidad": prov.especialidad or "",
                        "calificacion": str(prov.calificacion) if prov.calificacion else "",
                        "observaciones": prov.observaciones or "",
                    }
                )

            self.error_message = ""
            self.show_modal = True

        except Exception as e:
            pass  # print(f"Error opening edit modal: {e}") [OpSec Removed]
            self.error_message = f"Error al cargar datos: {str(e)}"
            self.show_modal = True

    def close_modal(self):
        """Cierra el modal."""
        self.show_modal = False
        self.form_data = {}
        self.selected_roles = []
        self.current_persona_id = None

    def validate_form_data(
        self, form_data: dict, is_editing: bool, selected_roles: List[str]
    ) -> tuple[bool, str]:
        """Validate form data before saving."""
        pass  # print("\n🔍 === VALIDATE_FORM START ===") [OpSec Removed]

        # Required fields for all personas
        if not form_data.get("nombre_completo", "").strip():
            return False, "El nombre completo es obligatorio"

        if not form_data.get("numero_documento", "").strip():
            return False, "El número de documento es obligatorio"

        if not form_data.get("telefono_principal", "").strip():
            return False, "El teléfono principal es obligatorio"

        # Email format validation
        correo = form_data.get("correo_electronico", "")
        if correo and "@" not in correo:
            return False, "El formato del correo electrónico no es válido"

        # Must select at least one role (optional requirement, enforcing for consistency)
        if not selected_roles:
            # It is allowed to have a person without roles in some contexts,
            # but usually via UI we want at least one.
            # Relaxing this constraint if user wants just a contact,
            # but let's enforce 1 for now to match previous logic?
            # For now, let's allow saving without roles if that's the intention,
            # or warn. Let's warn.
            pass

        # Validate specific fields for EACH selected role
        for rol in selected_roles:
            pass  # print(f"ℹ️ Validating for role: {rol}") [OpSec Removed]

            if rol == "Proveedor":
                if not form_data.get("especialidad", "").strip():
                    return False, "La especialidad es obligatoria para Proveedores"

                cal = form_data.get("calificacion", "")
                if cal:
                    try:
                        cal_val = int(cal)
                        if cal_val < 1 or cal_val > 5:
                            return False, "La calificación debe estar entre 1 y 5"
                    except ValueError:
                        return False, "La calificación debe ser un número"

            elif rol == "Asesor":
                try:
                    p_arr = int(form_data.get("comision_porcentaje_arriendo", 0))
                    p_ven = int(form_data.get("comision_porcentaje_venta", 0))
                    if p_arr < 0 or p_arr > 100 or p_ven < 0 or p_ven > 100:
                        return False, "Los porcentajes de comisión deben estar entre 0 y 100"
                except ValueError:
                    return False, "Los porcentajes deben ser números enteros"

        pass  # print("✅ Validation PASSED") [OpSec Removed]
        return True, ""

    @rx.event(background=True)
    async def save_persona(self, form_data: dict):
        """Guarda la persona (Crear o Actualizar) con roles múltiples."""
        pass  # print("\n=== SAVE_PERSONA MULTI-ROLE CALLED ===") [OpSec Removed]

        # CRITICAL: ALL state access must be inside async with self
        async with self:
            self.is_loading = True
            self.error_message = ""
            is_editing = self.is_editing
            current_persona_id = self.current_persona_id
            selected_roles = self.selected_roles

            auth_state = await self.get_state(AuthState)
            user_system = auth_state.user_info["nombre_usuario"] if auth_state.user_info else "sistema"

        # Validate
        is_valid, error_msg = self.validate_form_data(form_data, is_editing, selected_roles)

        if not is_valid:
            async with self:
                self.is_loading = False
                self.error_message = error_msg
            yield rx.toast.error(error_msg, duration=4000)
            return

        try:
            from src.infraestructura.persistencia.repositorio_persona_sqlite import (
                RepositorioPersonaSQLite,
            )
            from src.infraestructura.persistencia.repositorio_propietario_sqlite import (
                RepositorioPropietarioSQLite,
            )
            from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import (
                RepositorioArrendatarioSQLite,
            )
            from src.infraestructura.persistencia.repositorio_codeudor_sqlite import (
                RepositorioCodeudorSQLite,
            )
            from src.infraestructura.persistencia.repositorio_asesor_sqlite import (
                RepositorioAsesorSQLite,
            )
            from src.infraestructura.persistencia.repositorio_proveedores_sqlite import (
                RepositorioProveedoresSQLite,
            )

            repo_persona = RepositorioPersonaSQLite(db_manager)
            repo_propietario = RepositorioPropietarioSQLite(db_manager)
            repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
            repo_codeudor = RepositorioCodeudorSQLite(db_manager)
            repo_asesor = RepositorioAsesorSQLite(db_manager)
            repo_proveedor = RepositorioProveedoresSQLite(db_manager)

            servicio = ServicioPersonas(
                repo_persona=repo_persona,
                repo_propietario=repo_propietario,
                repo_arrendatario=repo_arrendatario,
                repo_codeudor=repo_codeudor,
                repo_asesor=repo_asesor,
                repo_proveedor=repo_proveedor,
            )
            success_message = ""

            # Preparar datos extras para todos los roles seleccionados
            datos_extras_map = {}
            for rol in selected_roles:
                datos_rol = {}
                if rol == "Propietario":
                    datos_rol = {
                        "banco_propietario": form_data.get("banco_propietario", ""),
                        "numero_cuenta_propietario": form_data.get("numero_cuenta_propietario", ""),
                        "tipo_cuenta": form_data.get("tipo_cuenta", ""),
                        "observaciones_propietario": form_data.get("observaciones_propietario", ""),
                        "consignatario": form_data.get("consignatario", ""),
                        "documento_consignatario": form_data.get("documento_consignatario", ""),
                    }
                elif rol == "Arrendatario":
                    datos_rol = {
                        "codigo_aprobacion_seguro": form_data.get("codigo_aprobacion_seguro", ""),
                        # Convertir a entero solo si hay valor
                        "id_seguro": (
                            int(form_data.get("id_seguro")) if form_data.get("id_seguro") else None
                        ),
                    }
                elif rol == "Asesor":
                    datos_rol = {
                        "comision_porcentaje_arriendo": int(
                            form_data.get("comision_porcentaje_arriendo", 0)
                        ),
                        "comision_porcentaje_venta": int(
                            form_data.get("comision_porcentaje_venta", 0)
                        ),
                        "fecha_vinculacion": form_data.get("fecha_vinculacion", ""),
                    }
                elif rol == "Proveedor":
                    datos_rol = {
                        "especialidad": form_data.get("especialidad", ""),
                        "calificacion": (
                            int(form_data.get("calificacion"))
                            if form_data.get("calificacion")
                            else None
                        ),
                        "observaciones": form_data.get("observaciones", ""),
                    }
                datos_extras_map[rol] = datos_rol

            if is_editing:
                pass  # print(f"Updating persona {current_persona_id}") [OpSec Removed]
                servicio.actualizar_persona(
                    id_persona=current_persona_id, datos=form_data, usuario_sistema=user_system
                )

                # Gestión de Roles en Edición
                persona_completa = servicio.obtener_persona_completa(current_persona_id)
                roles_actuales = persona_completa.roles

                # 1. Añadir/Actualizar roles seleccionados
                for rol in selected_roles:
                    datos_extra = datos_extras_map.get(rol, {})

                    if rol in roles_actuales:
                        pass  # print(f"Updating existing role: {rol}") [OpSec Removed]
                        servicio.actualizar_datos_rol(
                            id_persona=current_persona_id,
                            nombre_rol=rol,
                            datos_extra=datos_extra,
                            usuario_sistema=user_system,
                        )
                    else:
                        pass  # print(f"Assigning new role: {rol}") [OpSec Removed]
                        servicio.asignar_rol(
                            id_persona=current_persona_id,
                            nombre_rol=rol,
                            datos_extra=datos_extra,
                            usuario_sistema=user_system,
                        )

                # 2. Remover roles desmarcados
                for rol_existente in roles_actuales:
                    if rol_existente not in selected_roles:
                        pass  # print(f"Removing unselected role: {rol_existente}") [OpSec Removed]
                        try:
                            servicio.remover_rol(current_persona_id, rol_existente)
                        except ValueError:
                            pass  # print(f"Warning removing role: {e}") [OpSec Removed]
                            # Could happen if trying to remove the last role,
                            # but we might want to allow it if logical delete?
                            # Backend says "cannot remove last role".
                            # user might be unchecking everything, which would fail here if processed sequentially.
                            pass

                success_message = "Persona actualizada correctamente"
            else:
                # Crear nueva persona
                pass  # print(f"Creating new persona with roles: {selected_roles}") [OpSec Removed]
                servicio.crear_persona_con_roles(
                    datos_persona=form_data,
                    roles=selected_roles,
                    datos_extras=datos_extras_map,
                    usuario_sistema=user_system,
                )
                success_message = "Persona creada correctamente"

            # Update state on success
            async with self:
                self.show_modal = False
                self.selected_roles = []
                self.is_loading = False

            yield rx.toast.success(success_message, duration=4000)
            yield PersonasState.load_personas

        except ValueError as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False
            yield rx.toast.error(f"Error de validación: {str(e)}", duration=5000)
        except Exception as e:
            pass  # print(f"Error saving persona: {e}") [OpSec Removed]
            import traceback

            traceback.print_exc()
            async with self:
                self.error_message = f"Error inesperado: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(f"Error al guardar: {str(e)}", duration=5000)
