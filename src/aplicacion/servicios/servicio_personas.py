"""
Servicio de Aplicación: Gestión de Personas
Orquesta operaciones CRUD de Persona + Roles múltiples.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.dominio.entidades.arrendatario import Arrendatario
from src.dominio.entidades.asesor import Asesor
from src.dominio.entidades.codeudor import Codeudor
from src.dominio.entidades.persona import Persona
from src.dominio.entidades.propietario import Propietario
from src.dominio.entidades.proveedor import Proveedor

from src.dominio.interfaces.repositorio_persona import IRepositorioPersona
from src.dominio.interfaces.repositorio_asesor import IRepositorioAsesor
from src.dominio.interfaces.repositorio_propietario import IRepositorioPropietario
from src.dominio.interfaces.repositorio_arrendatario import IRepositorioArrendatario
from src.dominio.interfaces.repositorio_codeudor import IRepositorioCodeudor
from src.dominio.interfaces.repositorio_proveedores import RepositorioProveedores

# Integración Fase 3: CacheManager
from src.infraestructura.cache.cache_manager import cache_manager


@dataclass
class PersonaConRoles:
    """
    DTO para representar una Persona con todos sus roles y datos asociados.
    """

    persona: Persona
    datos_roles: Dict[str, Any] = field(
        default_factory=dict
    )  # {"Propietario": Propietario(...), ...}

    @property
    def roles(self) -> List[str]:
        """Retorna lista de nombres de roles activos."""
        return list(self.datos_roles.keys())

    @property
    def telefono_principal(self) -> Optional[str]:
        return self.persona.telefono_principal

    @property
    def correo_principal(self) -> Optional[str]:
        return self.persona.correo_electronico

    @property
    def nombre_completo(self) -> str:
        return self.persona.nombre_completo

    @property
    def numero_documento(self) -> str:
        return self.persona.numero_documento

    @property
    def esta_activa(self) -> bool:
        return self.persona.estado_registro == 1


class ServicioPersonas:
    """
    Servicio de aplicación para gestión integral de Personas y Roles.
    Implementa lógica de negocio para CRUD multi-rol.
    """

    def __init__(
        self,
        repo_persona: IRepositorioPersona,
        repo_asesor: IRepositorioAsesor,
        repo_propietario: IRepositorioPropietario,
        repo_arrendatario: IRepositorioArrendatario,
        repo_codeudor: IRepositorioCodeudor,
        repo_proveedor: RepositorioProveedores
    ):
        self.repo_persona = repo_persona
        self.repo_asesor = repo_asesor
        self.repo_propietario = repo_propietario
        self.repo_arrendatario = repo_arrendatario
        self.repo_codeudor = repo_codeudor
        self.repo_proveedor = repo_proveedor

    @cache_manager.cached("personas:list", level=1)
    def listar_personas(
        self,
        filtro_rol: Optional[str] = None,
        solo_activos: bool = True,
        busqueda: Optional[str] = None,
    ) -> List[PersonaConRoles]:
        """
        Lista personas con sus roles asignados.
        """
        personas = self.repo_persona.obtener_todos(
            filtro_rol=filtro_rol,
            solo_activos=solo_activos,
            busqueda=busqueda
        )

        return [
            PersonaConRoles(
                persona=p,
                datos_roles=self._obtener_datos_roles_persona(p.id_persona),
            )
            for p in personas
        ]

    def listar_personas_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        filtro_rol: Optional[str] = None,
        solo_activos: bool = True,
        busqueda: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
    ):
        """Lista personas con paginación y filtros adicionales."""
        from src.dominio.modelos.pagination import PaginatedResult, PaginationParams

        params = PaginationParams(page=page, page_size=page_size)

        total = self.repo_persona.contar_todos(
            filtro_rol=filtro_rol,
            solo_activos=solo_activos,
            busqueda=busqueda,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        personas = self.repo_persona.obtener_todos(
            filtro_rol=filtro_rol,
            solo_activos=solo_activos,
            busqueda=busqueda,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            limit=params.limit,
            offset=params.offset
        )

        items = [
            PersonaConRoles(
                persona=p,
                datos_roles=self._obtener_datos_roles_persona(p.id_persona),
            )
            for p in personas
        ]

        return PaginatedResult(
            items=items, total=total, page=params.page, page_size=params.page_size
        )

    def exportar_personas_csv(
        self,
        filtro_rol: Optional[str] = None,
        solo_activos: bool = True,
        busqueda: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
    ) -> str:
        """Genera un CSV con las personas filtradas."""
        import csv
        import io

        personas = self.repo_persona.obtener_todos(
            filtro_rol=filtro_rol,
            solo_activos=solo_activos,
            busqueda=busqueda,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(
            [
                "ID",
                "Nombre Completo",
                "Tipo Documento",
                "Documento",
                "Telefono",
                "Correo",
                "Direccion",
                "Fecha Creacion",
                "Estado",
            ]
        )

        for p in personas:
            writer.writerow(
                [
                    p.id_persona,
                    p.nombre_completo,
                    p.tipo_documento,
                    p.numero_documento,
                    p.telefono_principal,
                    p.correo_electronico,
                    p.direccion_principal,
                    p.created_at[:10] if p.created_at else "",
                    "Activo" if p.estado_registro else "Inactivo",
                ]
            )

        return output.getvalue()

    def obtener_persona_completa(self, id_persona: int) -> Optional[PersonaConRoles]:
        """Obtiene una persona con todos sus roles."""
        persona = self.repo_persona.obtener_por_id(id_persona)
        if not persona:
            return None

        datos_roles = self._obtener_datos_roles_persona(id_persona)
        return PersonaConRoles(persona=persona, datos_roles=datos_roles)

    def crear_persona_con_roles(
        self,
        datos_persona: Dict,
        roles: List[str],
        datos_extras: Optional[Dict[str, Dict]] = None,
        usuario_sistema: str = "sistema",
    ) -> PersonaConRoles:
        """Crea una nueva persona y le asigna roles."""
        if self.repo_persona.obtener_por_documento(datos_persona["numero_documento"]):
            raise ValueError(
                f"Ya existe una persona con documento {datos_persona['numero_documento']}"
            )

        persona = Persona(
            tipo_documento=datos_persona.get("tipo_documento", "CC"),
            numero_documento=datos_persona["numero_documento"],
            nombre_completo=datos_persona["nombre_completo"],
            telefono_principal=datos_persona.get("telefono_principal"),
            correo_electronico=datos_persona.get("correo_electronico"),
            direccion_principal=datos_persona.get("direccion_principal"),
            created_at=datetime.now().isoformat(),
            created_by=usuario_sistema,
        )

        persona_creada = self.repo_persona.crear(persona, usuario_sistema)

        datos_extras = datos_extras or {}
        for rol in roles:
            self._asignar_rol_interno(
                persona_creada.id_persona, rol, datos_extras.get(rol, {}), usuario_sistema
            )

        cache_manager.invalidate("personas")

        datos_roles = self._obtener_datos_roles_persona(persona_creada.id_persona)
        return PersonaConRoles(persona=persona_creada, datos_roles=datos_roles)

    def actualizar_persona(
        self, id_persona: int, datos: Dict, usuario_sistema: str = "sistema"
    ) -> PersonaConRoles:
        """Actualiza los datos de una persona."""
        persona = self.repo_persona.obtener_por_id(id_persona)
        if not persona:
            raise ValueError(f"No existe persona con ID {id_persona}")

        if "numero_documento" in datos:
            persona.numero_documento = datos["numero_documento"]
        if "nombre_completo" in datos:
            persona.nombre_completo = datos["nombre_completo"]
        if "telefono_principal" in datos:
            persona.telefono_principal = datos["telefono_principal"]
        if "correo_electronico" in datos:
            persona.correo_electronico = datos["correo_electronico"]
        if "direccion_principal" in datos:
            persona.direccion_principal = datos["direccion_principal"]
        if "tipo_documento" in datos:
            persona.tipo_documento = datos["tipo_documento"]

        persona.updated_at = datetime.now().isoformat()
        persona.updated_by = usuario_sistema

        self.repo_persona.actualizar(persona, usuario_sistema)
        cache_manager.invalidate("personas")

        datos_roles = self._obtener_datos_roles_persona(id_persona)
        return PersonaConRoles(persona=persona, datos_roles=datos_roles)

    def asignar_rol(
        self,
        id_persona: int,
        nombre_rol: str,
        datos_extra: Optional[Dict] = None,
        usuario_sistema: str = "sistema",
    ) -> None:
        """Asigna un rol a una persona existente."""
        persona = self.repo_persona.obtener_por_id(id_persona)
        if not persona:
            raise ValueError(f"No existe persona con ID {id_persona}")

        datos_roles = self._obtener_datos_roles_persona(id_persona)
        if nombre_rol in datos_roles:
            return 

        self._asignar_rol_interno(id_persona, nombre_rol, datos_extra or {}, usuario_sistema)

    def actualizar_datos_rol(
        self, id_persona: int, nombre_rol: str, datos_extra: Dict, usuario_sistema: str = "sistema"
    ) -> None:
        """Actualiza los datos específicos de un rol."""
        persona = self.repo_persona.obtener_por_id(id_persona)
        if not persona:
            raise ValueError(f"No existe persona con ID {id_persona}")

        datos_roles = self._obtener_datos_roles_persona(id_persona)
        if nombre_rol not in datos_roles:
            raise ValueError(f"La persona no tiene asignado el rol {nombre_rol}")

        entidad_rol = datos_roles[nombre_rol]

        if nombre_rol == "Asesor":
            asesor = entidad_rol
            if "fecha_vinculacion" in datos_extra:
                asesor.fecha_ingreso = datos_extra["fecha_vinculacion"]
            if "comision_porcentaje_arriendo" in datos_extra:
                try:
                    asesor.comision_porcentaje_arriendo = int(datos_extra["comision_porcentaje_arriendo"])
                except (ValueError, TypeError): pass
            if "comision_porcentaje_venta" in datos_extra:
                try:
                    asesor.comision_porcentaje_venta = int(datos_extra["comision_porcentaje_venta"])
                except (ValueError, TypeError): pass
            asesor.updated_at = datetime.now().isoformat()
            asesor.updated_by = usuario_sistema
            self.repo_asesor.actualizar(asesor, usuario_sistema)

        elif nombre_rol == "Propietario":
            prop = entidad_rol
            if "fecha_inicio_propietario" in datos_extra:
                prop.fecha_ingreso_propietario = datos_extra["fecha_inicio_propietario"]
            if "banco_propietario" in datos_extra:
                prop.banco_propietario = datos_extra["banco_propietario"]
            if "numero_cuenta_propietario" in datos_extra:
                prop.numero_cuenta_propietario = datos_extra["numero_cuenta_propietario"]
            if "tipo_cuenta" in datos_extra:
                prop.tipo_cuenta = datos_extra["tipo_cuenta"]
            if "observaciones_propietario" in datos_extra:
                prop.observaciones_propietario = datos_extra["observaciones_propietario"]
            if "consignatario" in datos_extra:
                prop.consignatario = datos_extra["consignatario"]
            prop.updated_at = datetime.now().isoformat()
            prop.updated_by = usuario_sistema
            self.repo_propietario.actualizar(prop, usuario_sistema)

        elif nombre_rol == "Arrendatario":
            arr = entidad_rol
            if "direccion_referencia" in datos_extra:
                arr.direccion_referencia = datos_extra["direccion_referencia"]
            if "id_seguro" in datos_extra:
                arr.id_seguro = datos_extra["id_seguro"]
            if "codigo_aprobacion_seguro" in datos_extra:
                arr.codigo_aprobacion_seguro = datos_extra["codigo_aprobacion_seguro"]
            arr.updated_at = datetime.now().isoformat()
            arr.updated_by = usuario_sistema
            self.repo_arrendatario.actualizar(arr, usuario_sistema)

        elif nombre_rol == "Proveedor":
            prov = entidad_rol
            if "especialidad" in datos_extra:
                prov.especialidad = datos_extra["especialidad"]
            if "calificacion" in datos_extra:
                prov.calificacion = datos_extra["calificacion"]
            if "observaciones" in datos_extra:
                prov.observaciones = datos_extra["observaciones"]
            prov.updated_at = datetime.now().isoformat()
            self.repo_proveedor.actualizar(prov)

    def remover_rol(self, id_persona: int, nombre_rol: str) -> None:
        """Remueve un rol de una persona."""
        datos_roles = self._obtener_datos_roles_persona(id_persona)
        if len(datos_roles) == 1 and nombre_rol in datos_roles:
            raise ValueError("No se puede remover el último rol de una persona")

        if nombre_rol == "Propietario":
            self.repo_propietario.eliminar_por_persona(id_persona)
        elif nombre_rol == "Arrendatario":
            self.repo_arrendatario.eliminar_por_persona(id_persona)
        elif nombre_rol == "Codeudor":
            self.repo_codeudor.eliminar_por_persona(id_persona)
        elif nombre_rol == "Asesor":
            self.repo_asesor.eliminar_por_persona(id_persona)
        elif nombre_rol == "Proveedor":
            self.repo_proveedor.eliminar_por_persona(id_persona)

    def desactivar_persona(
        self,
        id_persona: int,
        motivo: str = "Desactivado por usuario",
        usuario_sistema: str = "sistema",
    ) -> bool:
        """Inactiva una persona (soft delete)."""
        result = self.repo_persona.inactivar(id_persona, motivo, usuario_sistema)
        if result:
            cache_manager.invalidate("personas")
        return result

    def activar_persona(self, id_persona: int, usuario_sistema: str = "sistema") -> bool:
        """Reactiva una persona inactiva."""
        persona = self.repo_persona.obtener_por_id(id_persona)
        if not persona:
            return False

        persona.estado_registro = 1
        persona.motivo_inactivacion = None
        return self.repo_persona.actualizar(persona, usuario_sistema)

    def buscar_por_documento(self, documento: str) -> Optional[PersonaConRoles]:
        """Busca una persona por su número de documento."""
        persona = self.repo_persona.obtener_por_documento(documento)
        if not persona:
            return None

        datos_roles = self._obtener_datos_roles_persona(persona.id_persona)
        return PersonaConRoles(persona=persona, datos_roles=datos_roles)

    # --- Métodos Privados ---

    def _obtener_datos_roles_persona(self, id_persona: int) -> Dict[str, Any]:
        """Obtiene entidades asignadas a una persona."""
        datos = {}
        if prop := self.repo_propietario.obtener_por_persona(id_persona):
            datos["Propietario"] = prop
        if arr := self.repo_arrendatario.obtener_por_persona(id_persona):
            datos["Arrendatario"] = arr
        if cod := self.repo_codeudor.obtener_por_persona(id_persona):
            datos["Codeudor"] = cod
        if ase := self.repo_asesor.obtener_por_persona(id_persona):
            datos["Asesor"] = ase
        if prov := self.repo_proveedor.obtener_por_persona_id(id_persona):
            datos["Proveedor"] = prov
        return datos

    def _asignar_rol_interno(
        self, id_persona: int, nombre_rol: str, datos_extra: Dict, usuario_sistema: str
    ):
        """Crea el registro de rol."""
        created_at = datetime.now().isoformat()

        if nombre_rol == "Propietario":
            fecha_inicio = datos_extra.get("fecha_inicio_propietario", datetime.now().date().isoformat())
            propietario = Propietario(
                id_persona=id_persona,
                fecha_ingreso_propietario=fecha_inicio,
                banco_propietario=datos_extra.get("banco_propietario"),
                numero_cuenta_propietario=datos_extra.get("numero_cuenta_propietario"),
                tipo_cuenta=datos_extra.get("tipo_cuenta"),
                observaciones_propietario=datos_extra.get("observaciones_propietario"),
                consignatario=datos_extra.get("consignatario"),
                created_at=created_at,
                created_by=usuario_sistema,
            )
            self.repo_propietario.crear(propietario, usuario_sistema)

        elif nombre_rol == "Arrendatario":
            arrendatario = Arrendatario(
                id_persona=id_persona,
                direccion_referencia=datos_extra.get("direccion_referencia"),
                codigo_aprobacion_seguro=datos_extra.get("codigo_aprobacion_seguro"),
                id_seguro=datos_extra.get("id_seguro"),
                fecha_ingreso_arrendatario=datetime.now().date().isoformat(),
                created_at=created_at,
                created_by=usuario_sistema,
            )
            self.repo_arrendatario.crear(arrendatario, usuario_sistema)

        elif nombre_rol == "Codeudor":
            codeudor = Codeudor(
                id_persona=id_persona,
                fecha_ingreso_codeudor=datetime.now().date().isoformat(),
                created_at=created_at,
                created_by=usuario_sistema,
            )
            self.repo_codeudor.crear(codeudor, usuario_sistema)

        elif nombre_rol == "Asesor":
            fecha_vinculacion = datos_extra.get("fecha_vinculacion", datetime.now().date().isoformat())
            try: com_arr = int(datos_extra.get("comision_porcentaje_arriendo", 0))
            except: com_arr = 0
            try: com_venta = int(datos_extra.get("comision_porcentaje_venta", 0))
            except: com_venta = 0

            asesor = Asesor(
                id_persona=id_persona,
                fecha_ingreso=fecha_vinculacion,
                comision_porcentaje_arriendo=com_arr,
                comision_porcentaje_venta=com_venta,
                estado=1,
                created_at=created_at,
                created_by=usuario_sistema,
            )
            self.repo_asesor.crear(asesor, usuario_sistema)

        elif nombre_rol == "Proveedor":
            proveedor = Proveedor(
                id_persona=id_persona,
                especialidad=datos_extra.get("especialidad", ""),
                calificacion=datos_extra.get("calificacion", ""),
                observaciones=datos_extra.get("observaciones", ""),
                estado_registro=True,
                created_at=created_at,
                created_by=usuario_sistema,
            )
            self.repo_proveedor.guardar(proveedor)
