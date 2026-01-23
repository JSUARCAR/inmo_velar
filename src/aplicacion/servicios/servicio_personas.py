"""
Servicio de Aplicación: Gestión de Personas
Orquesta operaciones CRUD de Persona + Roles múltiples.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

from src.dominio.entidades.persona import Persona
from src.dominio.entidades.asesor import Asesor
from src.dominio.entidades.propietario import Propietario
from src.dominio.entidades.arrendatario import Arrendatario
from src.dominio.entidades.codeudor import Codeudor
from src.dominio.entidades.proveedor import Proveedor
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_persona_sqlite import RepositorioPersonaSQLite
from src.infraestructura.persistencia.repositorio_asesor_sqlite import RepositorioAsesorSQLite
from src.infraestructura.persistencia.repositorio_propietario_sqlite import RepositorioPropietarioSQLite
from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import RepositorioArrendatarioSQLite
from src.infraestructura.persistencia.repositorio_codeudor_sqlite import RepositorioCodeudorSQLite
from src.infraestructura.persistencia.repositorio_proveedores_sqlite import RepositorioProveedoresSQLite

# Integración Fase 3: CacheManager
from src.infraestructura.cache.cache_manager import cache_manager


@dataclass
class PersonaConRoles:
    """
    DTO para representar una Persona con todos sus roles y datos asociados.
    """
    persona: Persona
    datos_roles: Dict[str, Any] = field(default_factory=dict)  # {"Propietario": Propietario(...), ...}
    
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
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.repo_persona = RepositorioPersonaSQLite(db_manager)
        self.repo_asesor = RepositorioAsesorSQLite(db_manager)
        self.repo_propietario = RepositorioPropietarioSQLite(db_manager)
        self.repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
        self.repo_codeudor = RepositorioCodeudorSQLite(db_manager)
        self.repo_proveedor = RepositorioProveedoresSQLite(db_manager)
    
    @cache_manager.cached('personas:list', level=1)
    def listar_personas(
        self, 
        filtro_rol: Optional[str] = None, 
        solo_activos: bool = True,
        busqueda: Optional[str] = None
    ) -> List[PersonaConRoles]:
        """
        Lista personas con sus roles asignados.
        
        Args:
            filtro_rol: Filtrar por rol específico ("Propietario", "Arrendatario", etc.)
            solo_activos: Si True, solo personas con ESTADO_REGISTRO = 1
            busqueda: Texto para buscar en nombre o documento
        
        Returns:
            Lista de PersonaConRoles
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            # Query base
            query = """
                SELECT DISTINCT p.*
                FROM PERSONAS p
            """
            
            conditions = []
            params = []
            
            # Filtro por rol
            if filtro_rol:
                if filtro_rol == "Propietario":
                    query += " INNER JOIN PROPIETARIOS pr ON p.ID_PERSONA = pr.ID_PERSONA"
                elif filtro_rol == "Arrendatario":
                    query += " INNER JOIN ARRENDATARIOS ar ON p.ID_PERSONA = ar.ID_PERSONA"
                elif filtro_rol == "Codeudor":
                    query += " INNER JOIN CODEUDORES co ON p.ID_PERSONA = co.ID_PERSONA"
                elif filtro_rol == "Asesor":
                    query += " INNER JOIN ASESORES ase ON p.ID_PERSONA = ase.ID_PERSONA"
                elif filtro_rol == "Proveedor":
                    query += " INNER JOIN PROVEEDORES prov ON p.ID_PERSONA = prov.ID_PERSONA"
            
            # Filtro de activos
            if solo_activos:
                conditions.append("p.ESTADO_REGISTRO = TRUE")
            
            # Búsqueda de texto
            if busqueda:
                conditions.append(f"(p.NOMBRE_COMPLETO LIKE {placeholder} OR p.NUMERO_DOCUMENTO LIKE {placeholder})")
                busqueda_param = f"%{busqueda}%"
                params.extend([busqueda_param, busqueda_param])
            
            # Construir WHERE
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY p.NOMBRE_COMPLETO"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Retornar PersonaConRoles con datos_roles
        return [
            PersonaConRoles(
                persona=self._row_to_persona(row), 
                datos_roles=self._obtener_datos_roles_persona(row['ID_PERSONA'])
            )
            for row in rows
        ]
    
    def listar_personas_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        filtro_rol: Optional[str] = None,
        solo_activos: bool = True,
        busqueda: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None
    ):
        """Lista personas con paginación y filtros adicionales."""
        from src.dominio.modelos.pagination import PaginationParams, PaginatedResult
        
        params = PaginationParams(page=page, page_size=page_size)
        
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            # Query base con COUNT
            query_count = "SELECT COUNT(DISTINCT p.ID_PERSONA) as total FROM PERSONAS p"
            query_data = "SELECT DISTINCT p.* FROM PERSONAS p"
            
            join_clause = ""
            if filtro_rol:
                if filtro_rol == "Propietario":
                    join_clause = " INNER JOIN PROPIETARIOS pr ON p.ID_PERSONA = pr.ID_PERSONA"
                elif filtro_rol == "Arrendatario":
                    join_clause = " INNER JOIN ARRENDATARIOS ar ON p.ID_PERSONA = ar.ID_PERSONA"
                elif filtro_rol == "Codeudor":
                    join_clause = " INNER JOIN CODEUDORES co ON p.ID_PERSONA = co.ID_PERSONA"
                elif filtro_rol == "Asesor":
                    join_clause = " INNER JOIN ASESORES ase ON p.ID_PERSONA = ase.ID_PERSONA"
                elif filtro_rol == "Proveedor":
                    join_clause = " INNER JOIN PROVEEDORES prov ON p.ID_PERSONA = prov.ID_PERSONA"
            
            query_count += join_clause
            query_data += join_clause
            
            conditions = []
            query_params = []
            
            if solo_activos:
                conditions.append("p.ESTADO_REGISTRO = TRUE")
            
            if busqueda:
                conditions.append(f"(p.NOMBRE_COMPLETO LIKE {placeholder} OR p.NUMERO_DOCUMENTO LIKE {placeholder})")
                busqueda_param = f"%{busqueda}%"
                query_params.extend([busqueda_param, busqueda_param])
            
            # Filtro de Fechas (compatible SQLite/PostgreSQL si se usa ISO8601 YYYY-MM-DD)
            # Asumiendo que CREATED_AT es texto ISO o timestamp
            if fecha_inicio:
                conditions.append(f"DATE(p.CREATED_AT) >= {placeholder}")
                query_params.append(fecha_inicio)
            
            if fecha_fin:
                conditions.append(f"DATE(p.CREATED_AT) <= {placeholder}")
                query_params.append(fecha_fin)
            
            where_clause = ""
            if conditions:
                where_clause = " WHERE " + " AND ".join(conditions)
            
            # Total count
            cursor.execute(query_count + where_clause, query_params)
            
            count_res = cursor.fetchone()
            total = count_res['TOTAL'] if count_res else 0
            
            # Datos paginados
            query_data += where_clause
            query_data += f" ORDER BY p.NOMBRE_COMPLETO LIMIT {placeholder} OFFSET {placeholder}"
            cursor.execute(query_data, query_params + [params.limit, params.offset])
            rows = cursor.fetchall()
            
            items = [
                PersonaConRoles(
                    persona=self._row_to_persona(row),
                    datos_roles=self._obtener_datos_roles_persona(row['ID_PERSONA'])
                )
                for row in rows
            ]
            
            return PaginatedResult(
                items=items,
                total=total,
                page=params.page,
                page_size=params.page_size
            )
    
    def exportar_personas_csv(
        self,
        filtro_rol: Optional[str] = None,
        solo_activos: bool = True,
        busqueda: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None
    ) -> str:
        """Genera un CSV con las personas filtradas."""
        import io
        import csv

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            query = "SELECT DISTINCT p.* FROM PERSONAS p"
            
            # ... Reutilizar lógica de JOIN y WHERE ...
            # Por simplicidad repetimos la construcción (o refactorizar en un método privado _build_query)
            
            join_clause = ""
            if filtro_rol:
                if filtro_rol == "Propietario":
                    join_clause = " INNER JOIN PROPIETARIOS pr ON p.ID_PERSONA = pr.ID_PERSONA"
                elif filtro_rol == "Arrendatario":
                    join_clause = " INNER JOIN ARRENDATARIOS ar ON p.ID_PERSONA = ar.ID_PERSONA"
                elif filtro_rol == "Codeudor":
                    join_clause = " INNER JOIN CODEUDORES co ON p.ID_PERSONA = co.ID_PERSONA"
                elif filtro_rol == "Asesor":
                    join_clause = " INNER JOIN ASESORES ase ON p.ID_PERSONA = ase.ID_PERSONA"
                elif filtro_rol == "Proveedor":
                    join_clause = " INNER JOIN PROVEEDORES prov ON p.ID_PERSONA = prov.ID_PERSONA"
            query += join_clause
            
            conditions = []
            query_params = []
            
            if solo_activos:
                conditions.append("p.ESTADO_REGISTRO = TRUE")
            if busqueda:
                conditions.append(f"(p.NOMBRE_COMPLETO LIKE {placeholder} OR p.NUMERO_DOCUMENTO LIKE {placeholder})")
                busqueda_param = f"%{busqueda}%"
                query_params.extend([busqueda_param, busqueda_param])
            if fecha_inicio:
                conditions.append(f"DATE(p.CREATED_AT) >= {placeholder}")
                query_params.append(fecha_inicio)
            if fecha_fin:
                conditions.append(f"DATE(p.CREATED_AT) <= {placeholder}")
                query_params.append(fecha_fin)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY p.NOMBRE_COMPLETO"
            
            cursor.execute(query, query_params)
            rows = cursor.fetchall()

            # Generar CSV en memoria
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Cabeceras
            writer.writerow(["ID", "Nombre Completo", "Tipo Documento", "Documento", "Telefono", "Correo", "Direccion", "Fecha Creacion", "Estado"])
            
            for row in rows:
                p = self._row_to_persona(row)
                writer.writerow([
                    p.id_persona,
                    p.nombre_completo,
                    p.tipo_documento,
                    p.numero_documento,
                    p.telefono_principal,
                    p.correo_electronico,
                    p.direccion_principal,
                    p.created_at[:10] if p.created_at else "",
                    "Activo" if p.estado_registro else "Inactivo"
                ])
                
            return output.getvalue()
            
            items = [
                PersonaConRoles(
                    persona=self._row_to_persona(row),
                    datos_roles=self._obtener_datos_roles_persona(row['ID_PERSONA'])
                )
                for row in rows
            ]
            
            return PaginatedResult(
                items=items,
                total=total,
                page=params.page,
                page_size=params.page_size
            )
    
    def obtener_persona_completa(self, id_persona: int) -> Optional[PersonaConRoles]:
        """
        Obtiene una persona con todos sus roles y datos detallados.
        
        Args:
            id_persona: ID de la persona
        
        Returns:
            PersonaConRoles o None si no existe
        """
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
        usuario_sistema: str = "sistema"
    ) -> PersonaConRoles:
        """
        Crea una nueva persona y le asigna roles con datos extra.
        
        Args:
            datos_persona: Diccionario con datos de la persona
            roles: Lista de nombres de roles a asignar
            datos_extras: Diccionario mapeando rol -> datos extra (ej: {"Propietario": {"fecha_inicio": "..."}})
            usuario_sistema: Usuario que ejecuta la operación
        
        Returns:
            PersonaConRoles creada
        
        Raises:
            ValueError: Si el documento ya existe o datos inválidos
        """
        # Validar documento único
        if self.repo_persona.obtener_por_documento(datos_persona["numero_documento"]):
            raise ValueError(f"Ya existe una persona con documento {datos_persona['numero_documento']}")
        
        # Validar que haya al menos un rol (OPCIONAL: Ahora permitimos crear sin roles iniciales para casos como Proveedor)
        # if not roles:
        #     raise ValueError("Debe asignar al menos un rol a la persona")
        
        # Crear la persona
        persona = Persona(
            tipo_documento=datos_persona.get("tipo_documento", "CC"),
            numero_documento=datos_persona["numero_documento"],
            nombre_completo=datos_persona["nombre_completo"],
            telefono_principal=datos_persona.get("telefono_principal"),
            correo_electronico=datos_persona.get("correo_electronico"),
            direccion_principal=datos_persona.get("direccion_principal"),
            created_at=datetime.now().isoformat(),
            created_by=usuario_sistema
        )
        
        persona_creada = self.repo_persona.crear(persona, usuario_sistema)
        
       # Asignar roles con datos extra
        datos_extras = datos_extras or {}
        for rol in roles:
            self._asignar_rol_interno(
                persona_creada.id_persona, 
                rol, 
                datos_extras.get(rol, {}), 
                usuario_sistema
            )
        
        # Invalidar cache de personas
        cache_manager.invalidate('personas')
        
        # Retornar objeto completo
        datos_roles = self._obtener_datos_roles_persona(persona_creada.id_persona)
        return PersonaConRoles(persona=persona_creada, datos_roles=datos_roles)
    
    def actualizar_persona(
        self, 
        id_persona: int, 
        datos: Dict,
        usuario_sistema: str = "sistema"
    ) -> PersonaConRoles:
        """
        Actualiza los datos de una persona existente.
        
        Args:
            id_persona: ID de la persona
            datos: Diccionario con campos a actualizar
            usuario_sistema: Usuario que ejecuta la operación
        
        Returns:
            PersonaConRoles actualizada
        
        Raises:
            ValueError: Si la persona no existe
        """
        persona = self.repo_persona.obtener_por_id(id_persona)
        if not persona:
            raise ValueError(f"No existe persona con ID {id_persona}")
        
        # Actualizar campos
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
        
        # Invalidar cache
        cache_manager.invalidate('personas')
        
        datos_roles = self._obtener_datos_roles_persona(id_persona)
        return PersonaConRoles(persona=persona, datos_roles=datos_roles)
    
    def asignar_rol(
        self, 
        id_persona: int, 
        nombre_rol: str,
        datos_extra: Optional[Dict] = None,
        usuario_sistema: str = "sistema"
    ) -> None:
        """
        Asigna un rol a una persona existente.
        
        Args:
            id_persona: ID de la persona
            nombre_rol: Nombre del rol ("Propietario", "Arrendatario", etc.)
            datos_extra: Datos adicionales para el rol
            usuario_sistema: Usuario que ejecuta la operación
        """
        # Verificar que la persona existe
        persona = self.repo_persona.obtener_por_id(id_persona)
        if not persona:
            raise ValueError(f"No existe persona con ID {id_persona}")
        
        # Verificar que no tenga ya el rol
        datos_roles = self._obtener_datos_roles_persona(id_persona)
        if nombre_rol in datos_roles:
            return  # Ya tiene el rol, no hacer nada
        
        self._asignar_rol_interno(id_persona, nombre_rol, datos_extra or {}, usuario_sistema)
    
    def actualizar_datos_rol(
        self,
        id_persona: int,
        nombre_rol: str,
        datos_extra: Dict,
        usuario_sistema: str = "sistema"
    ) -> None:
        """
        Actualiza los datos específicos de un rol asignado a una persona.
        
        Args:
            id_persona: ID de la persona
            nombre_rol: Nombre del rol ("Propietario", "Arrendatario", "Asesor", etc.)
            datos_extra: Nuevos datos para el rol
            usuario_sistema: Usuario que ejecuta la operación
        
        Raises:
            ValueError: Si la persona o el rol no existen
        """
        # Verificar que la persona existe
        persona = self.repo_persona.obtener_por_id(id_persona)
        if not persona:
            raise ValueError(f"No existe persona con ID {id_persona}")
            
        # Obtener rol actual
        datos_roles = self._obtener_datos_roles_persona(id_persona)
        if nombre_rol not in datos_roles:
            raise ValueError(f"La persona no tiene asignado el rol {nombre_rol}")
            
        entidad_rol = datos_roles[nombre_rol]
        
        if nombre_rol == "Asesor":
            # Actualizar Asesor
            asesor = entidad_rol
            
            # Actualizar campos si vienen en datos_extra
            if "fecha_vinculacion" in datos_extra:
                asesor.fecha_ingreso = datos_extra["fecha_vinculacion"]
            
            if "comision_porcentaje_arriendo" in datos_extra:
                try:
                    asesor.comision_porcentaje_arriendo = int(datos_extra["comision_porcentaje_arriendo"])
                except (ValueError, TypeError):
                    pass # Mantener valor anterior si es inválido o manejar error
            
            if "comision_porcentaje_venta" in datos_extra:
                try:
                    asesor.comision_porcentaje_venta = int(datos_extra["comision_porcentaje_venta"])
                except (ValueError, TypeError):
                    pass
            
            asesor.updated_at = datetime.now().isoformat()
            asesor.updated_by = usuario_sistema
            
            self.repo_asesor.actualizar(asesor, usuario_sistema)

        elif nombre_rol == "Propietario":
            # Actualizar Propietario
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
                
            prop.updated_at = datetime.now().isoformat()
            prop.updated_by = usuario_sistema
            self.repo_propietario.actualizar(prop, usuario_sistema)
            
        elif nombre_rol == "Arrendatario":
            # Actualizar Arrendatario
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
            # Actualizar Proveedor
            prov = entidad_rol
            if "especialidad" in datos_extra:
                prov.especialidad = datos_extra["especialidad"]
            if "calificacion" in datos_extra:
                prov.calificacion = datos_extra["calificacion"]
            if "observaciones" in datos_extra:
                prov.observaciones = datos_extra["observaciones"]
            
            prov.updated_at = datetime.now().isoformat()
            self.repo_proveedor.actualizar(prov)
            
        # Codeudor normalmente no tiene datos extra editables complejos, pero se podría agregar

    
    def remover_rol(
        self, 
        id_persona: int, 
        nombre_rol: str
    ) -> None:
        """
        Remueve un rol de una persona.
        
        Args:
            id_persona: ID de la persona
            nombre_rol: Nombre del rol a remover
        
        Raises:
            ValueError: Si es el último rol de la persona
        """
        datos_roles = self._obtener_datos_roles_persona(id_persona)
        
        if len(datos_roles) == 1 and nombre_rol in datos_roles:
            raise ValueError("No se puede remover el último rol de una persona")
        
        # Eliminar rol de la tabla correspondiente
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            if nombre_rol == "Propietario":
                cursor.execute(f"DELETE FROM PROPIETARIOS WHERE ID_PERSONA = {placeholder}", (id_persona,))
            elif nombre_rol == "Arrendatario":
                cursor.execute(f"DELETE FROM ARRENDATARIOS WHERE ID_PERSONA = {placeholder}", (id_persona,))
            elif nombre_rol == "Codeudor":
                cursor.execute(f"DELETE FROM CODEUDORES WHERE ID_PERSONA = {placeholder}", (id_persona,))
            elif nombre_rol == "Asesor":
                cursor.execute(f"DELETE FROM ASESORES WHERE ID_PERSONA = {placeholder}", (id_persona,))
            elif nombre_rol == "Proveedor":
                cursor.execute(f"DELETE FROM PROVEEDORES WHERE ID_PERSONA = {placeholder}", (id_persona,))
            
            conn.commit()
    
    def desactivar_persona(
        self, 
        id_persona: int,
        motivo: str = "Desactivado por usuario",
        usuario_sistema: str = "sistema"
    ) -> bool:
        """
        Inactiva una persona (soft delete).
        
        Args:
            id_persona: ID de la persona
            motivo: Motivo de la inactivación
            usuario_sistema: Usuario que ejecuta la operación
        
        Returns:
            True si se inactivó correctamente
        """
        result = self.repo_persona.inactivar(id_persona, motivo, usuario_sistema)
        if result:
            cache_manager.invalidate('personas')
        return result
    
    def activar_persona(
        self, 
        id_persona: int,
        usuario_sistema: str = "sistema"
    ) -> bool:
        """
        Reactiva una persona inactiva.
        
        Args:
            id_persona: ID de la persona
            usuario_sistema: Usuario que ejecuta la operación
        
        Returns:
            True si se activó correctamente
        """
        persona = self.repo_persona.obtener_por_id(id_persona)
        if not persona:
            return False
        
        persona.estado_registro = 1
        persona.motivo_inactivacion = None
        return self.repo_persona.actualizar(persona, usuario_sistema)
    
    def buscar_por_documento(self, documento: str) -> Optional[PersonaConRoles]:
        """
        Busca una persona por su número de documento.
        
        Args:
            documento: Número de documento
        
        Returns:
            PersonaConRoles o None
        """
        persona = self.repo_persona.obtener_por_documento(documento)
        if not persona:
            return None
        
        datos_roles = self._obtener_datos_roles_persona(persona.id_persona)
        return PersonaConRoles(persona=persona, datos_roles=datos_roles)
    
    # --- Métodos Privados ---
    
    def _obtener_datos_roles_persona(self, id_persona: int) -> Dict[str, Any]:
        """Obtiene diccionario de {nombre_rol: entidad} asignados a una persona."""
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
    
    def _asignar_rol_interno(self, id_persona: int, nombre_rol: str, datos_extra: Dict, usuario_sistema: str):
        """Crea el registro de rol en la tabla correspondiente."""
        created_at = datetime.now().isoformat()
        
        if nombre_rol == "Propietario":
            # Extraer fecha de inicio
            fecha_inicio = datos_extra.get("fecha_inicio_propietario", datetime.now().date().isoformat())
            propietario = Propietario(
                id_persona=id_persona,
                fecha_ingreso_propietario=fecha_inicio,
                banco_propietario=datos_extra.get("banco_propietario"),
                numero_cuenta_propietario=datos_extra.get("numero_cuenta_propietario"),
                tipo_cuenta=datos_extra.get("tipo_cuenta"),
                observaciones_propietario=datos_extra.get("observaciones_propietario"),
                created_at=created_at,
                created_by=usuario_sistema
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
                created_by=usuario_sistema
            )
            self.repo_arrendatario.crear(arrendatario, usuario_sistema)
        
        elif nombre_rol == "Codeudor":
            codeudor = Codeudor(
                id_persona=id_persona,
                fecha_ingreso_codeudor=datetime.now().date().isoformat(),
                created_at=created_at,
                created_by=usuario_sistema
            )
            self.repo_codeudor.crear(codeudor, usuario_sistema)
        
        elif nombre_rol == "Asesor":
            # Extraer fecha vinculación y estado
            fecha_vinculacion = datos_extra.get("fecha_vinculacion", datetime.now().date().isoformat())
            
            # Sanitizar valores numéricos
            try:
                com_arr = int(datos_extra.get("comision_porcentaje_arriendo", 0))
            except (ValueError, TypeError):
                com_arr = 0
                
            try:
                com_venta = int(datos_extra.get("comision_porcentaje_venta", 0))
            except (ValueError, TypeError):
                com_venta = 0

            asesor = Asesor(
                id_persona=id_persona,
                fecha_ingreso=fecha_vinculacion,
                comision_porcentaje_arriendo=com_arr,
                comision_porcentaje_venta=com_venta,
                estado=1,
                created_at=created_at,
                created_by=usuario_sistema
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
                created_by=usuario_sistema
            )
            self.repo_proveedor.guardar(proveedor)
    
    def _row_to_persona(self, row: dict) -> Persona:
        """Convierte diccionario SQL a entidad Persona."""
        return Persona(
            id_persona=row['ID_PERSONA'],
            tipo_documento=row['TIPO_DOCUMENTO'],
            numero_documento=row['NUMERO_DOCUMENTO'],
            nombre_completo=row['NOMBRE_COMPLETO'],
            telefono_principal=row['TELEFONO_PRINCIPAL'],
            correo_electronico=row['CORREO_ELECTRONICO'],
            direccion_principal=row['DIRECCION_PRINCIPAL'],
            estado_registro=row['ESTADO_REGISTRO'],
            motivo_inactivacion=row['MOTIVO_INACTIVACION'],
            created_at=row['CREATED_AT'],
            created_by=row['CREATED_BY'],
            updated_at=row['UPDATED_AT'],
            updated_by=row['UPDATED_BY']
        )
