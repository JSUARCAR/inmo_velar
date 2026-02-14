from typing import Any, Dict, List

import reflex as rx
from pydantic import BaseModel

from src.aplicacion.servicios.servicio_permisos import ServicioPermisos
from src.aplicacion.servicios.servicio_usuarios import ServicioUsuarios
from src.infraestructura.persistencia.database import db_manager
from src.presentacion_reflex.state.auth_state import AuthState


class PermissionModel(BaseModel):
    """Modelo para un permiso individual en la UI."""

    id_permiso: int
    modulo: str
    ruta: str
    accion: str
    descripcion: str
    categoria: str


class PermissionModule(BaseModel):
    """Modelo para un módulo con sus permisos."""

    name: str
    permissions: List[PermissionModel]


class PermissionCategory(BaseModel):
    """Modelo para una categoría de permisos."""

    category: str
    modules: List[PermissionModule]


class UsuarioDisplayModel(BaseModel):
    """Modelo para visualización de usuarios en la UI using Pydantic/Reflex."""

    id_usuario: int
    nombre_usuario: str
    rol: str
    estado_usuario: bool
    estado_label: str
    ultimo_acceso: str


class UsuariosState(rx.State):
    """Estado para la gestión de usuarios."""

    # Datos
    usuarios: List[UsuarioDisplayModel] = []

    # Filtros
    filter_role: str = "Todos"
    filter_status: str = "Todos"
    search_text: str = ""

    # Modal Form
    show_form_modal: bool = False
    is_editing: bool = False
    form_data: Dict[str, Any] = {
        "id_usuario": None,
        "nombre_usuario": "",
        "contrasena": "",
        "rol": "Asesor",
        "estado_usuario": True,
    }

    # UI State
    is_loading: bool = False
    error_message: str = ""

    # === PERMISOS STATE ===
    show_permissions_modal: bool = False
    selected_role_for_permissions: str = ""
    # Structure: List of PermissionCategory objects
    permissions_hierarchy: List[PermissionCategory] = []

    all_permissions: List[Dict[str, Any]] = []
    role_permissions_ids: List[int] = []  # IDs de permisos asignados al rol
    is_loading_permissions: bool = False
    permissions_error: str = ""

    @rx.event(background=True)
    async def load_users(self):
        """Carga la lista de usuarios."""
        async with self:
            self.is_loading = True

        try:
            servicio = ServicioUsuarios(db_manager)
            users_list = servicio.listar_usuarios()

            # Formatear para tabla
            formatted = []
            for u in users_list:
                item = UsuarioDisplayModel(
                    id_usuario=u.id_usuario,
                    nombre_usuario=u.nombre_usuario,
                    rol=u.rol,
                    estado_usuario=u.es_activo(),
                    estado_label="Activo" if u.es_activo() else "Inactivo",
                    ultimo_acceso=u.ultimo_acceso or "Nunca",
                )

                # Filtros en memoria
                pass_filter = True
                if self.filter_role != "Todos" and item.rol != self.filter_role:
                    pass_filter = False
                if self.filter_status != "Todos":
                    is_active = item.estado_usuario
                    if self.filter_status == "Activo" and not is_active:
                        pass_filter = False
                    if self.filter_status == "Inactivo" and is_active:
                        pass_filter = False
                if (
                    self.search_text
                    and self.search_text.lower() not in item.nombre_usuario.lower()
                ):
                    pass_filter = False

                if pass_filter:
                    formatted.append(item)

            async with self:
                self.usuarios = formatted
                self.is_loading = False

        except Exception as e:
            error_msg = str(e)
            async with self:
                self.error_message = error_msg
                self.is_loading = False

            # Mostrar toast de error solo si hay usuarios esperados
            pass  # print(f"Error al cargar usuarios: {error_msg}") [OpSec Removed]

    # --- ACTIONS ---

    def open_create_modal(self):
        self.is_editing = False
        self.form_data = {
            "id_usuario": None,
            "nombre_usuario": "",
            "contrasena": "",  # Required for new
            "rol": "Asesor",
            "estado_usuario": True,
        }
        self.show_form_modal = True

    def open_edit_modal(self, user: UsuarioDisplayModel):
        self.is_editing = True
        self.form_data = {
            "id_usuario": user.id_usuario,
            "nombre_usuario": user.nombre_usuario,
            "contrasena": "",  # Optional for edit (reset)
            "rol": user.rol,
            "estado_usuario": user.estado_usuario,
        }
        self.show_form_modal = True

    def close_modal(self):
        self.show_form_modal = False
        self.error_message = ""

    def handle_form_open_change(self, is_open: bool):
        if not is_open:
            self.close_modal()

    def set_form_field(self, field: str, value: Any):
        self.form_data[field] = value

    @rx.event(background=True)
    async def save_user(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            current_admin = await self.get_state(AuthState)
            admin_user = current_admin.user_info["nombre_usuario"] if current_admin.user_info else "sistema"

        try:
            servicio = ServicioUsuarios(db_manager)
            datos = self.form_data

            # Validaciones del lado del cliente
            if not datos["nombre_usuario"] or not datos["nombre_usuario"].strip():
                raise ValueError("El nombre de usuario es requerido.")

            if self.is_editing:
                # Update logic
                servicio.actualizar_usuario(datos["id_usuario"], datos, admin_user)

                # Update password if provided
                if datos["contrasena"]:
                    if len(datos["contrasena"]) < 6:
                        raise ValueError("La contraseña debe tener al menos 6 caracteres.")
                    servicio.restablecer_contrasena(
                        datos["id_usuario"], datos["contrasena"], admin_user
                    )

                # Mostrar toast de éxito
                yield rx.toast.success(
                    f"Usuario '{datos['nombre_usuario']}' actualizado exitosamente",
                    position="top-right",
                    duration=3000,
                )
            else:
                # Create logic
                if not datos["contrasena"]:
                    raise ValueError("La contraseña es requerida para nuevos usuarios.")

                if len(datos["contrasena"]) < 6:
                    raise ValueError("La contraseña debe tener al menos 6 caracteres.")

                servicio.crear_usuario(
                    datos["nombre_usuario"], datos["contrasena"], datos["rol"], admin_user
                )

                # Mostrar toast de éxito
                yield rx.toast.success(
                    f"Usuario '{datos['nombre_usuario']}' creado exitosamente",
                    position="top-right",
                    duration=3000,
                )

            async with self:
                self.show_form_modal = False
                self.is_loading = False

            yield UsuariosState.load_users

        except ValueError as e:
            # Errores de validación
            async with self:
                self.error_message = str(e)
                self.is_loading = False

            yield rx.toast.error(str(e), position="top-right", duration=4000)
        except Exception as e:
            # Otros errores
            error_msg = str(e)

            # Traducir errores comunes de PostgreSQL
            if "duplicate key" in error_msg.lower() or "already exists" in error_msg.lower():
                error_msg = f"El usuario '{datos['nombre_usuario']}' ya existe en el sistema."
            elif "foreign key" in error_msg.lower():
                error_msg = "Error de integridad de datos. Verifique las relaciones."
            else:
                error_msg = f"Error al guardar usuario: {error_msg}"

            async with self:
                self.error_message = error_msg
                self.is_loading = False

            yield rx.toast.error(error_msg, position="top-right", duration=5000)

    @rx.event(background=True)
    async def toggle_status(self, id_usuario: int, current_status: bool):
        """Alterna el estado activo/inactivo."""
        async with self:
            current_admin = await self.get_state(AuthState)
            admin_user = current_admin.user_info["nombre_usuario"] if current_admin.user_info else "sistema"

        try:
            servicio = ServicioUsuarios(db_manager)
            new_status = not current_status
            servicio.cambiar_estado(id_usuario, new_status, admin_user)

            # Mostrar toast de éxito
            status_text = "activado" if new_status else "desactivado"
            yield rx.toast.success(
                f"Usuario {status_text} exitosamente", position="top-right", duration=2500
            )

            yield UsuariosState.load_users
        except Exception as e:
            # Mostrar toast de error
            yield rx.toast.error(
                f"Error al cambiar estado: {str(e)}", position="top-right", duration=4000
            )

    # Setters filters
    def set_search(self, val: str):
        self.search_text = val
        return UsuariosState.load_users

    def set_filter_role(self, val: str):
        self.filter_role = val
        return UsuariosState.load_users

    def set_filter_status(self, val: str):
        self.filter_status = val
        return UsuariosState.load_users

    # === PERMISOS METHODS ===

    def open_permissions_modal(self, rol: str):
        """Abre el modal de gestión de permisos para un rol."""
        if rol == "Administrador":
            # No permitir editar permisos de Administrador
            return

        self.selected_role_for_permissions = rol
        self.show_permissions_modal = True
        self.permissions_error = ""
        return UsuariosState.load_permissions_data

    def close_permissions_modal(self):
        """Cierra el modal de permisos."""
        self.show_permissions_modal = False
        self.selected_role_for_permissions = ""
        self.permissions_error = ""

    @rx.event(background=True)
    async def load_permissions_data(self):
        """Carga todos los permisos y los permisos del rol seleccionado."""
        async with self:
            self.is_loading_permissions = True

        try:
            servicio = ServicioPermisos(db_manager)

            # 1. Obtener todos los permisos agrupados por categoría
            permisos_agrupados = servicio.obtener_permisos_agrupados_por_categoria()

            # 2. Construir jerarquía para la UI (Categoría -> Módulos -> Permisos)
            hierarchy = []
            all_formatted = []

            for categoria, permisos_list in permisos_agrupados.items():
                # Agrupar por módulo dentro de la categoría
                modulos_map = {}

                for p in permisos_list:
                    # Crear objeto PermissionModel
                    perm_model = PermissionModel(
                        id_permiso=p.id_permiso,
                        modulo=p.modulo,
                        ruta=p.ruta,
                        accion=p.accion,
                        descripcion=p.descripcion or "",
                        categoria=p.categoria or "General",
                    )

                    # Guardar para all_permissions (formato dict para compatibilidad)
                    perm_dict = {
                        "id_permiso": p.id_permiso,
                        "modulo": p.modulo,
                        "ruta": p.ruta,
                        "accion": p.accion,
                        "descripcion": p.descripcion,
                        "categoria": p.categoria,
                    }
                    all_formatted.append(perm_dict)

                    if p.modulo not in modulos_map:
                        modulos_map[p.modulo] = []
                    modulos_map[p.modulo].append(perm_model)

                # Crear lista de módulos para esta categoría
                modules_list = []
                for mod_name, mod_perms in modulos_map.items():
                    modules_list.append(PermissionModule(name=mod_name, permissions=mod_perms))

                # Agregar a la jerarquía
                hierarchy.append(PermissionCategory(category=categoria, modules=modules_list))

            # 3. Obtener IDs de permisos actuales del rol
            ids_rol = servicio.obtener_ids_permisos_rol(self.selected_role_for_permissions)

            async with self:
                self.all_permissions = all_formatted
                self.permissions_hierarchy = hierarchy
                self.role_permissions_ids = ids_rol
                self.is_loading_permissions = False

        except Exception as e:
            async with self:
                self.permissions_error = f"Error al cargar permisos: {str(e)}"
                self.is_loading_permissions = False

    def toggle_permission(self, id_permiso: int):
        """Toggle un permiso individual."""
        if id_permiso in self.role_permissions_ids:
            self.role_permissions_ids = [
                pid for pid in self.role_permissions_ids if pid != id_permiso
            ]
        else:
            self.role_permissions_ids = self.role_permissions_ids + [id_permiso]

    def toggle_all_module_permissions(self, modulo: str):
        """Toggle todos los permisos de un módulo."""
        # Obtener IDs de todos los permisos del módulo
        module_permission_ids = [
            p["id_permiso"] for p in self.all_permissions if p["modulo"] == modulo
        ]

        # Verificar si todos están seleccionados
        all_selected = all(pid in self.role_permissions_ids for pid in module_permission_ids)

        if all_selected:
            # Deseleccionar todos
            self.role_permissions_ids = [
                pid for pid in self.role_permissions_ids if pid not in module_permission_ids
            ]
        else:
            # Seleccionar todos
            new_ids = set(self.role_permissions_ids + module_permission_ids)
            self.role_permissions_ids = list(new_ids)

    @rx.event(background=True)
    async def save_permissions(self):
        """Guarda los permisos del rol."""
        async with self:
            self.is_loading_permissions = True
            self.permissions_error = ""
            current_admin = await self.get_state(AuthState)
            admin_user = current_admin.user_info["nombre_usuario"] if current_admin.user_info else "sistema"

        try:
            servicio = ServicioPermisos(db_manager)

            # Actualizar permisos del rol
            servicio.actualizar_permisos_rol(
                self.selected_role_for_permissions, self.role_permissions_ids, admin_user
            )

            # Mostrar toast de éxito
            yield rx.toast.success(
                f"Permisos actualizados para rol '{self.selected_role_for_permissions}'",
                position="top-right",
                duration=3000,
            )

            async with self:
                self.show_permissions_modal = False
                self.is_loading_permissions = False

        except ValueError as e:
            async with self:
                self.permissions_error = str(e)
                self.is_loading_permissions = False

            yield rx.toast.error(str(e), position="top-right", duration=4000)
        except Exception as e:
            error_msg = f"Error al guardar permisos: {str(e)}"
            async with self:
                self.permissions_error = error_msg
                self.is_loading_permissions = False

            yield rx.toast.error(error_msg, position="top-right", duration=5000)

    @rx.event(background=True)
    async def apply_preset(self, preset_name: str):
        """Aplica un preset de permisos predefinido."""
        async with self:
            self.is_loading_permissions = True
            current_admin = await self.get_state(AuthState)
            admin_user = current_admin.user_info["nombre_usuario"] if current_admin.user_info else "sistema"

        try:
            servicio = ServicioPermisos(db_manager)

            if preset_name == "asesor":
                servicio.aplicar_preset_asesor(admin_user)
            elif preset_name == "operativo":
                servicio.aplicar_preset_operativo(admin_user)
            elif preset_name == "solo_lectura":
                servicio.aplicar_preset_solo_lectura(self.selected_role_for_permissions, admin_user)

            yield rx.toast.success(
                f"Preset '{preset_name}' aplicado exitosamente", position="top-right", duration=3000
            )

            # Recargar permisos para mostrar los cambios
            yield UsuariosState.load_permissions_data

        except Exception as e:
            yield rx.toast.error(
                f"Error al aplicar preset: {str(e)}", position="top-right", duration=4000
            )

            async with self:
                self.is_loading_permissions = False
