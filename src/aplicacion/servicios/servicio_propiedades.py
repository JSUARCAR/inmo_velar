"""
Servicio de Aplicación: Gestión de Propiedades
Orquesta operaciones CRUD de Propiedad con filtros avanzados.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from src.dominio.entidades.propiedad import Propiedad
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite

# Integración Fase 3: CacheManager
from src.infraestructura.cache.cache_manager import cache_manager


class ServicioPropiedades:
    """
    Servicio de aplicación para gestión integral de Propiedades.
    Implementa lógica de negocio para CRUD con filtros avanzados.
    """
    
    TIPOS_PROPIEDAD = [
        "Casa",
        "Apartamento",
        "Local Comercial",
        "Bodega",
        "Oficina",
        "Lote"
    ]
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.repo = RepositorioPropiedadSQLite(db_manager)
    
    @cache_manager.cached('propiedades:list', level=1)
    def listar_propiedades(
        self,
        filtro_tipo: Optional[str] = None,
        filtro_disponibilidad: Optional[int] = None,
        filtro_municipio: Optional[int] = None,
        solo_activas: bool = True,
        busqueda: Optional[str] = None
    ) -> List[Propiedad]:
        """
        Lista propiedades con filtros aplicados.
        
        Args:
            filtro_tipo: Filtrar por tipo específico (Casa, Apartamento, etc.)
            filtro_disponibilidad: 1 = Disponible, 0 = Ocupada, None = Todas
            filtro_municipio: ID del municipio para filtrar
            solo_activas: Si True, solo ESTADO_REGISTRO = 1
            busqueda: Texto para buscar en matrícula o dirección
        
        Returns:
            Lista de Propiedad
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            # Query base
            query = """
                SELECT DISTINCT p.*
                FROM PROPIEDADES p
            """
            
            conditions = []
            params = []
            
            # Filtro por tipo
            if filtro_tipo and filtro_tipo != "Todos":
                conditions.append(f"p.TIPO_PROPIEDAD = {placeholder}")
                params.append(filtro_tipo)
            
            # Filtro por disponibilidad
            if filtro_disponibilidad is not None:
                conditions.append(f"p.DISPONIBILIDAD_PROPIEDAD = {placeholder}")
                params.append(bool(filtro_disponibilidad))
            
            # Filtro por municipio
            if filtro_municipio:
                conditions.append(f"p.ID_MUNICIPIO = {placeholder}")
                params.append(filtro_municipio)
            
            # Filtro de activas
            if solo_activas:
                conditions.append("p.ESTADO_REGISTRO = TRUE")
            
            # Búsqueda de texto
            if busqueda:
                conditions.append(f"(p.MATRICULA_INMOBILIARIA LIKE {placeholder} OR p.DIRECCION_PROPIEDAD LIKE {placeholder})")
                busqueda_param = f"%{busqueda}%"
                params.extend([busqueda_param, busqueda_param])
            
            # Construir WHERE
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY p.MATRICULA_INMOBILIARIA"
            
            # Ejecutar query
            cursor.execute(query, params)
            propiedades_data = cursor.fetchall()
            
            # Convertir a objetos
            propiedades = [self.repo._row_to_entity(p) for p in propiedades_data]
            
            return propiedades

    @cache_manager.cached('propiedades:list_paginated', level=1, ttl=300)
    def listar_propiedades_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        filtro_tipo: Optional[str] = None,
        filtro_disponibilidad: Optional[int] = None,
        filtro_municipio: Optional[int] = None,
        solo_activas: bool = True,
        busqueda: Optional[str] = None
    ):
        """
        Lista propiedades con filtros y paginación.
        
        Returns:
            PaginatedResult[Propiedad]
        """
        from src.dominio.modelos.pagination import PaginationParams, PaginatedResult
        
        # Validar params
        params = PaginationParams(page=page, page_size=page_size)
        
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            # 1. Construir condiciones comunes
            conditions = []
            query_params = []
            
            if filtro_tipo and filtro_tipo != "Todos":
                conditions.append(f"p.TIPO_PROPIEDAD = {placeholder}")
                query_params.append(filtro_tipo)
            
            if filtro_disponibilidad is not None:
                conditions.append(f"p.DISPONIBILIDAD_PROPIEDAD = {placeholder}")
                # Convertir a compatible con Postgres (bool)
                query_params.append(bool(filtro_disponibilidad))
            
            if filtro_municipio:
                conditions.append(f"p.ID_MUNICIPIO = {placeholder}")
                query_params.append(filtro_municipio)
                
            if solo_activas:
                # Use parameterized query for boolean compatibility
                conditions.append(f"p.ESTADO_REGISTRO = {placeholder}")
                query_params.append(True)
                
            if busqueda:
                conditions.append(f"(p.MATRICULA_INMOBILIARIA LIKE {placeholder} OR p.DIRECCION_PROPIEDAD LIKE {placeholder})")
                busqueda_param = f"%{busqueda}%"
                query_params.extend([busqueda_param, busqueda_param])
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            
            # 2. Contar total
            count_query = f"SELECT COUNT(*) as total FROM PROPIEDADES p {where_clause}"
            cursor.execute(count_query, query_params)
            
            # Handle dictionary result for count
            row = cursor.fetchone()
            total = row['total'] if row and 'total' in row else 0
            if isinstance(row, tuple): # Fallback if cursor didn't behave as Dict
                 total = row[0]

            
            # 3. Obtener items paginados
            # Subquery para obtener la primera imagen (fotos)
            # Asume tabla DOCUMENTOS con columnas ENTIDAD_TIPO, ENTIDAD_ID, TIPO_DOCUMENTO/MIME_TYPE
            query = f"""
                SELECT p.*,
                (SELECT ID FROM DOCUMENTOS d 
                 WHERE d.ENTIDAD_TIPO = 'PROPIEDAD' 
                 AND d.ENTIDAD_ID = CAST(p.ID_PROPIEDAD AS TEXT) 
                 AND d.MIME_TYPE LIKE 'image/%%' 
                 AND d.ES_VIGENTE = '1' 
                 ORDER BY d.ID ASC LIMIT 1) as IMAGEN_PRINCIPAL_ID
                FROM PROPIEDADES p
                {where_clause}
                ORDER BY p.MATRICULA_INMOBILIARIA
                LIMIT {placeholder} OFFSET {placeholder}
            """
            
            # Agregar params de paginación
            final_params = query_params + [params.page_size, params.offset]
            
            cursor.execute(query, final_params)
            rows = cursor.fetchall()
            
            # Use Repository's mapper which handles keys correctly
            items = []
            for row in rows:
                p = self.repo._row_to_entity(row)
                # Populate transient field for UI
                # Check for both upper and lower case key depending on driver
                img_id = row.get('IMAGEN_PRINCIPAL_ID') or row.get('imagen_principal_id')
                if img_id:
                    p.imagen_principal_id = img_id
                items.append(p)
            
            return PaginatedResult(
                items=items,
                total=total,
                page=params.page,
                page_size=params.page_size
            )
    
    def obtener_propiedad(self, id_propiedad: int) -> Optional[Propiedad]:
        """
        Obtiene una propiedad por su ID.
        
        Args:
            id_propiedad: ID de la propiedad
        
        Returns:
            Propiedad o None si no existe
        """
        return self.repo.obtener_por_id(id_propiedad)
    
    def buscar_por_matricula(self, matricula: str) -> Optional[Propiedad]:
        """
        Busca una propiedad por su matrícula inmobiliaria.
        
        Args:
            matricula: Matrícula inmobiliaria
        
        Returns:
            Propiedad o None
        """
        return self.repo.obtener_por_matricula(matricula)
    
    def crear_propiedad(
        self,
        datos: Dict,
        usuario_sistema: str = "sistema"
    ) -> Propiedad:
        """
        Crea una nueva propiedad.
        
        Args:
            datos: Diccionario con datos de la propiedad
            usuario_sistema: Usuario que ejecuta la operación
        
        Returns:
            Propiedad creada
        
        Raises:
            ValueError: Si la matrícula ya existe o datos inválidos
        """
        # Validar matrícula única
        if self.repo.obtener_por_matricula(datos["matricula_inmobiliaria"]):
            raise ValueError(f"Ya existe una propiedad con matrícula {datos['matricula_inmobiliaria']}")
        
        # Validar tipo de propiedad
        if datos.get("tipo_propiedad") not in self.TIPOS_PROPIEDAD:
            raise ValueError(f"Tipo de propiedad inválido. Debe ser uno de: {', '.join(self.TIPOS_PROPIEDAD)}")
        
        # Validar área positiva
        if datos.get("area_m2", 0) <= 0:
            raise ValueError("El área debe ser mayor a 0")
        
        # Validar estrato si existe
        if datos.get("estrato") and not (1 <= datos["estrato"] <= 6):
            raise ValueError("El estrato debe estar entre 1 y 6")
        
        # Crear la propiedad
        propiedad = Propiedad(
            matricula_inmobiliaria=datos["matricula_inmobiliaria"],
            id_municipio=datos["id_municipio"],
            direccion_propiedad=datos["direccion_propiedad"],
            tipo_propiedad=datos["tipo_propiedad"],
            disponibilidad_propiedad=datos.get("disponibilidad_propiedad", 1),
            area_m2=datos["area_m2"],
            habitaciones=datos.get("habitaciones"),
            bano=datos.get("bano"),
            parqueadero=datos.get("parqueadero"),
            estrato=datos.get("estrato"),
            valor_administracion=datos.get("valor_administracion"),
            canon_arrendamiento_estimado=datos.get("canon_arrendamiento_estimado"),
            valor_venta_propiedad=datos.get("valor_venta_propiedad"),
            comision_venta_propiedad=datos.get("comision_venta_propiedad"),
            observaciones_propiedad=datos.get("observaciones_propiedad"),
            codigo_energia=datos.get("codigo_energia"),
            codigo_agua=datos.get("codigo_agua"),
            codigo_gas=datos.get("codigo_gas"),
            telefono_administracion=datos.get("telefono_administracion"),
            tipo_cuenta_administracion=datos.get("tipo_cuenta_administracion"),
            numero_cuenta_administracion=datos.get("numero_cuenta_administracion"),
            fecha_ingreso_propiedad=datos.get("fecha_ingreso_propiedad", datetime.now().date().isoformat()),
            created_at=datetime.now().isoformat(),
            created_by=usuario_sistema
        )
        
        result = self.repo.crear(propiedad, usuario_sistema)
        cache_manager.invalidate('propiedades')
        return result
    
    def actualizar_propiedad(
        self,
        id_propiedad: int,
        datos: Dict,
        usuario_sistema: str = "sistema"
    ) -> Propiedad:
        """
        Actualiza los datos de una propiedad existente.
        
        Args:
            id_propiedad: ID de la propiedad
            datos: Diccionario con campos a actualizar
            usuario_sistema: Usuario que ejecuta la operación
        
        Returns:
            Propiedad actualizada
        
        Raises:
            ValueError: Si la propiedad no existe
        """
        propiedad = self.repo.obtener_por_id(id_propiedad)
        if not propiedad:
            raise ValueError(f"No existe propiedad con ID {id_propiedad}")
        
        # Validar tipo de propiedad si se actualiza
        if "tipo_propiedad" in datos and datos["tipo_propiedad"] not in self.TIPOS_PROPIEDAD:
            raise ValueError(f"Tipo de propiedad inválido. Debe ser uno de: {', '.join(self.TIPOS_PROPIEDAD)}")
        
        # Validar área si se actualiza
        if "area_m2" in datos and datos["area_m2"] <= 0:
            raise ValueError("El área debe ser mayor a 0")
        
        # Validar estrato si se actualiza
        if "estrato" in datos and datos["estrato"] and not (1 <= datos["estrato"] <= 6):
            raise ValueError("El estrato debe estar entre 1 y 6")
        
        # Actualizar campos
        if "matricula_inmobiliaria" in datos:
            propiedad.matricula_inmobiliaria = datos["matricula_inmobiliaria"]
        if "id_municipio" in datos:
            propiedad.id_municipio = datos["id_municipio"]
        if "direccion_propiedad" in datos:
            propiedad.direccion_propiedad = datos["direccion_propiedad"]
        if "tipo_propiedad" in datos:
            propiedad.tipo_propiedad = datos["tipo_propiedad"]
        if "disponibilidad_propiedad" in datos:
            propiedad.disponibilidad_propiedad = datos["disponibilidad_propiedad"]
        if "area_m2" in datos:
            propiedad.area_m2 = datos["area_m2"]
        if "habitaciones" in datos:
            propiedad.habitaciones = datos["habitaciones"]
        if "bano" in datos:
            propiedad.bano = datos["bano"]
        if "parqueadero" in datos:
            propiedad.parqueadero = datos["parqueadero"]
        if "estrato" in datos:
            propiedad.estrato = datos["estrato"]
        if "valor_administracion" in datos:
            propiedad.valor_administracion = datos["valor_administracion"]
        if "canon_arrendamiento_estimado" in datos:
            propiedad.canon_arrendamiento_estimado = datos["canon_arrendamiento_estimado"]
        if "valor_venta_propiedad" in datos:
            propiedad.valor_venta_propiedad = datos["valor_venta_propiedad"]
        if "comision_venta_propiedad" in datos:
            propiedad.comision_venta_propiedad = datos["comision_venta_propiedad"]
        if "observaciones_propiedad" in datos:
            propiedad.observaciones_propiedad = datos["observaciones_propiedad"]
        
        # Códigos CIU (Servicios Públicos)
        if "codigo_energia" in datos:
            propiedad.codigo_energia = datos["codigo_energia"]
        if "codigo_agua" in datos:
            propiedad.codigo_agua = datos["codigo_agua"]
        if "codigo_gas" in datos:
            propiedad.codigo_gas = datos["codigo_gas"]
        
        # Campos de Administración
        if "telefono_administracion" in datos:
            propiedad.telefono_administracion = datos["telefono_administracion"]
        if "tipo_cuenta_administracion" in datos:
            propiedad.tipo_cuenta_administracion = datos["tipo_cuenta_administracion"]
        if "numero_cuenta_administracion" in datos:
            propiedad.numero_cuenta_administracion = datos["numero_cuenta_administracion"]
        
        propiedad.updated_at = datetime.now().isoformat()
        propiedad.updated_by = usuario_sistema
        
        self.repo.actualizar(propiedad, usuario_sistema)
        cache_manager.invalidate('propiedades')
        
        return propiedad
    
    def cambiar_disponibilidad(
        self,
        id_propiedad: int,
        nueva_disponibilidad: int,
        usuario_sistema: str = "sistema"
    ) -> bool:
        """
        Cambia la disponibilidad de una propiedad.
        
        Args:
            id_propiedad: ID de la propiedad
            nueva_disponibilidad: 1 = Disponible, 0 = Ocupada
            usuario_sistema: Usuario que ejecuta la operación
        
        Returns:
            True si se actualizó correctamente
        """
        propiedad = self.repo.obtener_por_id(id_propiedad)
        if not propiedad:
            return False
        
        propiedad.disponibilidad_propiedad = nueva_disponibilidad
        propiedad.updated_at = datetime.now().isoformat()
        propiedad.updated_by = usuario_sistema
        
        result = self.repo.actualizar(propiedad, usuario_sistema)
        if result:
            cache_manager.invalidate('propiedades')
        return result
    
    def desactivar_propiedad(
        self,
        id_propiedad: int,
        motivo: str = "Desactivado por usuario",
        usuario_sistema: str = "sistema"
    ) -> bool:
        """
        Inactiva una propiedad (soft delete).
        
        Args:
            id_propiedad: ID de la propiedad
            motivo: Motivo de la inactivación
            usuario_sistema: Usuario que ejecuta la operación
        
        Returns:
            True si se inactivó correctamente
        """
        propiedad = self.repo.obtener_por_id(id_propiedad)
        if not propiedad:
            return False
        
        propiedad.estado_registro = 0
        propiedad.motivo_inactivacion = motivo
        propiedad.updated_at = datetime.now().isoformat()
        propiedad.updated_by = usuario_sistema
        
        return self.repo.actualizar(propiedad, usuario_sistema)
    
    def activar_propiedad(
        self,
        id_propiedad: int,
        usuario_sistema: str = "sistema"
    ) -> bool:
        """
        Reactiva una propiedad inactiva.
        
        Args:
            id_propiedad: ID de la propiedad
            usuario_sistema: Usuario que ejecuta la operación
        
        Returns:
            True si se activó correctamente
        """
        propiedad = self.repo.obtener_por_id(id_propiedad)
        if not propiedad:
            return False
        
        propiedad.estado_registro = 1
        propiedad.motivo_inactivacion = None
        propiedad.updated_at = datetime.now().isoformat()
        propiedad.updated_by = usuario_sistema
        
        return self.repo.actualizar(propiedad, usuario_sistema)
    
    def obtener_municipios_disponibles(self) -> List[Dict]:
        """
        Retorna lista de municipios para dropdown.
        
        Returns:
            Lista de diccionarios con {id, nombre}
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(
                "SELECT ID_MUNICIPIO, NOMBRE_MUNICIPIO FROM MUNICIPIOS ORDER BY NOMBRE_MUNICIPIO"
            )
            return [{"id": row['ID_MUNICIPIO'], "nombre": row['NOMBRE_MUNICIPIO']} for row in cursor.fetchall()]
    
    def obtener_tipos_propiedad(self) -> List[str]:
        """
        Retorna catálogo de tipos de propiedad.
        
        Returns:
            Lista de tipos de propiedad
        """
        return self.TIPOS_PROPIEDAD.copy()
    
    # --- Métodos Privados ---
    
    def _row_to_propiedad(self, row: tuple) -> Propiedad:
        """Convierte tupla SQL a entidad Propiedad."""
        return Propiedad(
            id_propiedad=row[0],
            matricula_inmobiliaria=row[1],
            id_municipio=row[2],
            direccion_propiedad=row[3],
            tipo_propiedad=row[4],
            disponibilidad_propiedad=row[5],
            area_m2=row[6],
            habitaciones=row[7],
            bano=row[8],
            parqueadero=row[9],
            estrato=row[10],
            valor_administracion=row[11],
            canon_arrendamiento_estimado=row[12],
            valor_venta_propiedad=row[13],
            comision_venta_propiedad=row[14],
            observaciones_propiedad=row[15],
            fecha_ingreso_propiedad=row[16],
            estado_registro=row[17],
            motivo_inactivacion=row[18],
            created_at=row[19],
            created_by=row[20],
            updated_at=row[21],
            updated_by=row[22],
            codigo_energia=row[23] if len(row) > 23 else None,
            codigo_agua=row[24] if len(row) > 24 else None,
            codigo_gas=row[25] if len(row) > 25 else None,
            telefono_administracion=row[26] if len(row) > 26 else None,
            tipo_cuenta_administracion=row[27] if len(row) > 27 else None,
            numero_cuenta_administracion=row[28] if len(row) > 28 else None
        )

    def exportar_propiedades_csv(
        self,
        filtro_tipo: Optional[str] = None,
        filtro_disponibilidad: Optional[int] = None,
        filtro_municipio: Optional[int] = None,
        solo_activas: bool = True,
        busqueda: Optional[str] = None
    ) -> str:
        """Genera un CSV con las propiedades filtradas."""
        import io
        import csv

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            # Query base con JOIN a MUNICIPIOS
            query = """
                SELECT p.*, m.NOMBRE_MUNICIPIO
                FROM PROPIEDADES p
                LEFT JOIN MUNICIPIOS m ON p.ID_MUNICIPIO = m.ID_MUNICIPIO
            """
            
            conditions = []
            params = []
            
            # Reutilizar lógica de filtros
            if filtro_tipo and filtro_tipo != "Todos":
                conditions.append(f"p.TIPO_PROPIEDAD = {placeholder}")
                params.append(filtro_tipo)
            
            if filtro_disponibilidad is not None:
                conditions.append(f"p.DISPONIBILIDAD_PROPIEDAD = {placeholder}")
                params.append(bool(filtro_disponibilidad))
            
            if filtro_municipio:
                conditions.append(f"p.ID_MUNICIPIO = {placeholder}")
                params.append(filtro_municipio)
            
            if solo_activas:
                conditions.append(f"p.ESTADO_REGISTRO = {placeholder}")
                params.append(True)
            
            if busqueda:
                conditions.append(f"(p.MATRICULA_INMOBILIARIA LIKE {placeholder} OR p.DIRECCION_PROPIEDAD LIKE {placeholder})")
                busqueda_param = f"%{busqueda}%"
                params.extend([busqueda_param, busqueda_param])
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY p.MATRICULA_INMOBILIARIA"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Generar CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Cabeceras
            writer.writerow([
                "Matrícula", 
                "Tipo", 
                "Municipio", 
                "Dirección", 
                "Canon", 
                "Area (m2)", 
                "Habitaciones", 
                "Baños", 
                "Parqueaderos", 
                "Estrato", 
                "Disponibilidad"
            ])
            
            for row in rows:
                p = self._row_to_propiedad(list(row.values())[:29]) # Usar helper existente para la parte de propiedad
                # Nota: _row_to_propiedad espera tupla ordenada, pero aquí estamos con dict cursor o values.
                # Mejor accedemos directo al row dict que es más seguro
                
                disponibilidad = "Disponible" if row.get('DISPONIBILIDAD_PROPIEDAD') else "Ocupada"
                
                writer.writerow([
                    row.get('MATRICULA_INMOBILIARIA', ''),
                    row.get('TIPO_PROPIEDAD', ''),
                    row.get('NOMBRE_MUNICIPIO', 'N/A'),
                    row.get('DIRECCION_PROPIEDAD', ''),
                    f"${row.get('CANON_ARRENDAMIENTO_ESTIMADO', 0):,.0f}",
                    row.get('AREA_M2', 0),
                    row.get('HABITACIONES', 0),
                    row.get('BANO', 0),
                    row.get('PARQUEADERO', 0),
                    row.get('ESTRATO', ''),
                    disponibilidad
                ])
                
            return output.getvalue()
