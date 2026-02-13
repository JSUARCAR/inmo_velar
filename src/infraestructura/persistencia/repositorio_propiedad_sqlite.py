"""
Repositorio SQLite/PostgreSQL para Propiedad.
Implementa mapeo 1:1 estricto con tabla PROPIEDADES.
"""

from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.propiedad import Propiedad
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioPropiedadSQLite:
    """
    Repositorio para la entidad Propiedad.
    Soporta tanto SQLite como PostgreSQL mediante DatabaseManager.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row) -> Propiedad:
        """Convierte una fila SQL a entidad Propiedad."""
        if row is None:
            return None

        # Manejo flexible de diccionarios (RealDictCursor) o objetos Row
        if hasattr(row, "keys"):
            # Convertir a dict para acceso uniforme insensible a mayúsculas si es necesario
            # Pero RealDictCursor ya es un dict.
            # Nota: dependemos de que las columnas se llamen igual que en la BD
            data = dict(row)
        else:
            # Fallback para sqlite3.Row o tuplas (aunque deberíamos usar siempre dict cursor)
            data = dict(row)

        # Helper para obtener valor ignorando mayúsculas/minúsculas si fuera necesario (Postgres devuelve minusculas por defecto con psycopg2 a veces)
        # Para ser seguros, usamos .get probando claves mayúsculas (como en esquema) y minúsculas
        def get_val(key):
            return data.get(key) or data.get(key.upper()) or data.get(key.lower())

        return Propiedad(
            id_propiedad=get_val("ID_PROPIEDAD"),
            matricula_inmobiliaria=get_val("MATRICULA_INMOBILIARIA"),
            id_municipio=get_val("ID_MUNICIPIO"),
            direccion_propiedad=get_val("DIRECCION_PROPIEDAD"),
            tipo_propiedad=get_val("TIPO_PROPIEDAD"),
            disponibilidad_propiedad=get_val("DISPONIBILIDAD_PROPIEDAD"),
            area_m2=get_val("AREA_M2"),
            habitaciones=get_val("HABITACIONES"),
            bano=get_val("BANO"),
            parqueadero=get_val("PARQUEADERO"),
            estrato=get_val("ESTRATO"),
            valor_administracion=get_val("VALOR_ADMINISTRACION"),
            canon_arrendamiento_estimado=get_val("CANON_ARRENDAMIENTO_ESTIMADO"),
            valor_venta_propiedad=get_val("VALOR_VENTA_PROPIEDAD"),
            comision_venta_propiedad=get_val("COMISION_VENTA_PROPIEDAD"),
            observaciones_propiedad=get_val("OBSERVACIONES_PROPIEDAD"),
            codigo_energia=get_val("CODIGO_ENERGIA"),
            codigo_agua=get_val("CODIGO_AGUA"),
            codigo_gas=get_val("CODIGO_GAS"),
            telefono_administracion=get_val("TELEFONO_ADMINISTRACION"),
            tipo_cuenta_administracion=get_val("TIPO_CUENTA_ADMINISTRACION"),
            numero_cuenta_administracion=get_val("NUMERO_CUENTA_ADMINISTRACION"),
            fecha_ingreso_propiedad=get_val("FECHA_INGRESO_PROPIEDAD"),
            estado_registro=get_val("ESTADO_REGISTRO"),
            motivo_inactivacion=get_val("MOTIVO_INACTIVACION"),
            created_at=get_val("CREATED_AT"),
            created_by=get_val("CREATED_BY"),
            updated_at=get_val("UPDATED_AT"),
            updated_by=get_val("UPDATED_BY"),
        )

    def obtener_por_id(self, id_propiedad: int) -> Optional[Propiedad]:
        """Obtiene una propiedad por su ID."""
        conn = self.db.obtener_conexion()
        # CAMBIO: Usar get_dict_cursor para asegurar retorno de diccionario en Postgres
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM PROPIEDADES WHERE ID_PROPIEDAD = {placeholder}", (id_propiedad,)
        )

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_por_matricula(self, matricula: str) -> Optional[Propiedad]:
        """Obtiene una propiedad por su matrícula inmobiliaria."""
        conn = self.db.obtener_conexion()
        # CAMBIO: Usar get_dict_cursor
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM PROPIEDADES WHERE MATRICULA_INMOBILIARIA = {placeholder}", (matricula,)
        )

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def listar_con_filtros(
        self,
        filtro_tipo: Optional[str] = None,
        filtro_disponibilidad: Optional[int] = None,
        filtro_municipio: Optional[int] = None,
        solo_activas: bool = True,
        busqueda: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Propiedad]:
        """Lista propiedades con filtros aplicados."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        query = """
            SELECT p.*,
            (SELECT ID FROM DOCUMENTOS d 
             WHERE d.ENTIDAD_TIPO = 'PROPIEDAD' 
             AND d.ENTIDAD_ID = CAST(p.ID_PROPIEDAD AS TEXT) 
             AND d.MIME_TYPE LIKE 'image/%%' 
             AND d.ES_VIGENTE = '1' 
             ORDER BY d.ID ASC LIMIT 1) as IMAGEN_PRINCIPAL_ID
            FROM PROPIEDADES p
        """

        conditions = []
        params = []

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
            conditions.append(
                f"(p.MATRICULA_INMOBILIARIA LIKE {placeholder} OR p.DIRECCION_PROPIEDAD LIKE {placeholder})"
            )
            busqueda_param = f"%{busqueda}%"
            params.extend([busqueda_param, busqueda_param])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY p.MATRICULA_INMOBILIARIA"

        if limit is not None:
            query += f" LIMIT {placeholder} OFFSET {placeholder}"
            params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        propiedades = []
        for row in rows:
            p = self._row_to_entity(row)
            img_id = row.get("IMAGEN_PRINCIPAL_ID") or row.get("imagen_principal_id")
            if img_id:
                p.imagen_principal_id = img_id
            propiedades.append(p)

        return propiedades

    def contar_con_filtros(
        self,
        filtro_tipo: Optional[str] = None,
        filtro_disponibilidad: Optional[int] = None,
        filtro_municipio: Optional[int] = None,
        solo_activas: bool = True,
        busqueda: Optional[str] = None
    ) -> int:
        """Cuenta total de propiedades con filtros."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        query = "SELECT COUNT(*) as TOTAL FROM PROPIEDADES p"
        conditions = []
        params = []

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
            conditions.append(
                f"(p.MATRICULA_INMOBILIARIA LIKE {placeholder} OR p.DIRECCION_PROPIEDAD LIKE {placeholder})"
            )
            busqueda_param = f"%{busqueda}%"
            params.extend([busqueda_param, busqueda_param])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        row = cursor.fetchone()
        if row:
            # Soporte robusto para sqlite3.Row (acceso key/index) y dict (Postgres wrapper, keys may be Upper)
            # Primero intentar acceso por llave estándar (TOTAL)
            try:
                return row["TOTAL"]
            except (KeyError, TypeError):
                # Fallbacks
                try:
                    return row["total"]
                except (KeyError, TypeError):
                    # Si es dict y no tiene las llaves, devolver primer value
                    if isinstance(row, dict):
                        return list(row.values())[0] if row else 0
                    # Si es tupla o sqlite3.Row, acceso por índice
                    try:
                        return row[0]
                    except (IndexError, TypeError):
                        pass
        return 0

    def listar_sin_mandato(self) -> List[dict]:
        """Retorna propiedades que no tienen mandato activo."""
        query = """
        SELECT p.ID_PROPIEDAD, p.MATRICULA_INMOBILIARIA, p.DIRECCION_PROPIEDAD, p.CANON_ARRENDAMIENTO_ESTIMADO
        FROM PROPIEDADES p
        WHERE p.ESTADO_REGISTRO IS TRUE
          AND NOT EXISTS (
              SELECT 1 FROM CONTRATOS_MANDATOS cm
              WHERE cm.ID_PROPIEDAD = p.ID_PROPIEDAD
                AND cm.ESTADO_CONTRATO_M = 'Activo'
          )
        ORDER BY p.MATRICULA_INMOBILIARIA
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def listar_para_arrendamiento(self) -> List[dict]:
        """Retorna propiedades con mandato activo y sin arriendo activo."""
        query = """
        SELECT p.ID_PROPIEDAD, p.MATRICULA_INMOBILIARIA, p.DIRECCION_PROPIEDAD, p.CANON_ARRENDAMIENTO_ESTIMADO
        FROM PROPIEDADES p
        JOIN CONTRATOS_MANDATOS cm ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD
        WHERE p.ESTADO_REGISTRO IS TRUE
          AND cm.ESTADO_CONTRATO_M = 'Activo'
          AND NOT EXISTS (
              SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca
              WHERE ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                AND ca.ESTADO_CONTRATO_A = 'Activo'
          )
        ORDER BY p.MATRICULA_INMOBILIARIA
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def crear(self, propiedad: Propiedad, usuario_sistema: str) -> Propiedad:
        """
        Crea una nueva propiedad en la BD.
        """
        # Usar transaccion del manager
        with self.db.transaccion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()

            # CAMBIO: Reemplazado placeholders manuales por {placeholder}
            query = f"""
            INSERT INTO PROPIEDADES (
                MATRICULA_INMOBILIARIA, ID_MUNICIPIO, DIRECCION_PROPIEDAD, TIPO_PROPIEDAD,
                DISPONIBILIDAD_PROPIEDAD, AREA_M2, HABITACIONES, BANO, PARQUEADERO,
                ESTRATO, VALOR_ADMINISTRACION, CANON_ARRENDAMIENTO_ESTIMADO,
                VALOR_VENTA_PROPIEDAD, COMISION_VENTA_PROPIEDAD, OBSERVACIONES_PROPIEDAD,
                CODIGO_ENERGIA, CODIGO_AGUA, CODIGO_GAS,
                TELEFONO_ADMINISTRACION, TIPO_CUENTA_ADMINISTRACION, NUMERO_CUENTA_ADMINISTRACION,
                FECHA_INGRESO_PROPIEDAD, ESTADO_REGISTRO,
                CREATED_AT, CREATED_BY
            ) VALUES (
                {placeholder}, {placeholder}, {placeholder}, {placeholder},
                {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder},
                {placeholder}, {placeholder}, {placeholder},
                {placeholder}, {placeholder}, {placeholder},
                {placeholder}, {placeholder}, {placeholder},
                {placeholder}, {placeholder}, {placeholder},
                {placeholder}, {placeholder},
                {placeholder}, {placeholder}
            )
            """

            cursor.execute(
                query,
                (
                    propiedad.matricula_inmobiliaria,
                    propiedad.id_municipio,
                    propiedad.direccion_propiedad,
                    propiedad.tipo_propiedad,
                    (
                        bool(propiedad.disponibilidad_propiedad)
                        if propiedad.disponibilidad_propiedad is not None
                        else True
                    ),  # Default True
                    propiedad.area_m2,
                    propiedad.habitaciones,
                    propiedad.bano,
                    propiedad.parqueadero,
                    propiedad.estrato,
                    propiedad.valor_administracion,
                    propiedad.canon_arrendamiento_estimado,
                    propiedad.valor_venta_propiedad,
                    propiedad.comision_venta_propiedad,
                    propiedad.observaciones_propiedad,
                    propiedad.codigo_energia,
                    propiedad.codigo_agua,
                    propiedad.codigo_gas,
                    propiedad.telefono_administracion,
                    propiedad.tipo_cuenta_administracion,
                    propiedad.numero_cuenta_administracion,
                    propiedad.fecha_ingreso_propiedad or datetime.now().isoformat(),
                    True,  # ESTADO_REGISTRO activo (True)
                    datetime.now().isoformat(),
                    usuario_sistema,
                ),
            )

            # Obtener ID generado
            propiedad.id_propiedad = self.db.get_last_insert_id(
                cursor, "PROPIEDADES", "ID_PROPIEDAD"
            )

            return propiedad

    def actualizar(self, propiedad: Propiedad, usuario_sistema: str) -> bool:
        """
        Actualiza una propiedad existente.
        """
        with self.db.transaccion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()

            query = f"""
            UPDATE PROPIEDADES SET
                MATRICULA_INMOBILIARIA = {placeholder},
                ID_MUNICIPIO = {placeholder},
                DIRECCION_PROPIEDAD = {placeholder},
                TIPO_PROPIEDAD = {placeholder},
                DISPONIBILIDAD_PROPIEDAD = {placeholder},
                AREA_M2 = {placeholder},
                HABITACIONES = {placeholder},
                BANO = {placeholder},
                PARQUEADERO = {placeholder},
                ESTRATO = {placeholder},
                VALOR_ADMINISTRACION = {placeholder},
                CANON_ARRENDAMIENTO_ESTIMADO = {placeholder},
                VALOR_VENTA_PROPIEDAD = {placeholder},
                COMISION_VENTA_PROPIEDAD = {placeholder},
                OBSERVACIONES_PROPIEDAD = {placeholder},
                CODIGO_ENERGIA = {placeholder},
                CODIGO_AGUA = {placeholder},
                CODIGO_GAS = {placeholder},
                TELEFONO_ADMINISTRACION = {placeholder},
                TIPO_CUENTA_ADMINISTRACION = {placeholder},
                NUMERO_CUENTA_ADMINISTRACION = {placeholder},
                ESTADO_REGISTRO = {placeholder},
                UPDATED_AT = {placeholder},
                UPDATED_BY = {placeholder}
            WHERE ID_PROPIEDAD = {placeholder}
            """

            cursor.execute(
                query,
                (
                    propiedad.matricula_inmobiliaria,
                    propiedad.id_municipio,
                    propiedad.direccion_propiedad,
                    propiedad.tipo_propiedad,
                    (
                        bool(propiedad.disponibilidad_propiedad)
                        if propiedad.disponibilidad_propiedad is not None
                        else True
                    ),
                    propiedad.area_m2,
                    propiedad.habitaciones,
                    propiedad.bano,
                    propiedad.parqueadero,
                    propiedad.estrato,
                    propiedad.valor_administracion,
                    propiedad.canon_arrendamiento_estimado,
                    propiedad.valor_venta_propiedad,
                    propiedad.comision_venta_propiedad,
                    propiedad.observaciones_propiedad,
                    propiedad.codigo_energia,
                    propiedad.codigo_agua,
                    propiedad.codigo_gas,
                    propiedad.telefono_administracion,
                    propiedad.tipo_cuenta_administracion,
                    propiedad.numero_cuenta_administracion,
                    # CAMBIO: Castear explícitamente a bool si es necesario, o pasar el valor tal cual
                    (
                        bool(propiedad.estado_registro)
                        if propiedad.estado_registro is not None
                        else True
                    ),
                    datetime.now().isoformat(),
                    usuario_sistema,
                    propiedad.id_propiedad,
                ),
            )

            return cursor.rowcount > 0
