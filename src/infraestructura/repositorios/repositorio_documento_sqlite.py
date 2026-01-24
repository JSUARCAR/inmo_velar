import sqlite3
from typing import List, Optional
from src.dominio.entidades.documento import Documento
from src.infraestructura.persistencia.database import DatabaseManager

class RepositorioDocumentoSQLite:
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()

    def _row_to_entity(self, row, include_content=False) -> Documento:
        """Conversión de fila SQL a entidad Documento."""
        # Estructura de row esperada depende de la query (con o sin contenido)
        # ID, ENTIDAD_TIPO, ENTIDAD_ID, NOMBRE_ARCHIVO, EXTENSION, MIME_TYPE, DESCRIPCION, VERSION, ES_VIGENTE, CONTENIDO (opc)
        
        # Como usamos indices fijos, debemos tener cuidado con el orden en las queries
        # Asumiremos que las queries de listar SIEMPRE traen la metadata base en orden fijo
        
        # Support for both sqlite3.Row (index/name) and RealDictCursor (name only)
        # Using uppercase keys as enforced by UpperCaseCursorWrapper in database.py
        
        # Helper to get value securely
        def get_val(key, idx):
            if hasattr(row, 'keys'): # Dict-like (Postgres)
                return row.get(key)
            return row[idx] # Tuple-like or sqlite3.Row (SQLite)

        doc = Documento(
            id=get_val('ID', 0),
            entidad_tipo=get_val('ENTIDAD_TIPO', 1),
            entidad_id=get_val('ENTIDAD_ID', 2),
            nombre_archivo=get_val('NOMBRE_ARCHIVO', 3),
            extension=get_val('EXTENSION', 4),
            mime_type=get_val('MIME_TYPE', 5),
            descripcion=get_val('DESCRIPCION', 6),
            version=get_val('VERSION', 7),
            # Logic fixed in previous step, ensuring boolean consistency
            es_vigente=(str(get_val('ES_VIGENTE', 8)) == '1' or get_val('ES_VIGENTE', 8) == 1 or get_val('ES_VIGENTE', 8) is True),
            created_at=get_val('CREATED_AT', 9),
            created_by=get_val('CREATED_BY', 10)
        )
        
        if include_content:
             # Check for content in keys or index 11
             if hasattr(row, 'keys'):
                 doc.contenido = bytes(row.get('CONTENIDO')) if row.get('CONTENIDO') else None
             elif len(row) > 11:
                 doc.contenido = bytes(row[11]) if row[11] else None
             
        return doc

    def crear(self, documento: Documento) -> Documento:
        """Guarda un nuevo documento (incluyendo BLOB). Retorna el documento con ID."""
        ph = self.db.get_placeholder()
        sql = f"""
        INSERT INTO DOCUMENTOS (
            ENTIDAD_TIPO, ENTIDAD_ID, NOMBRE_ARCHIVO, EXTENSION, MIME_TYPE, 
            DESCRIPCION, CONTENIDO, VERSION, ES_VIGENTE, CREATED_BY
        ) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
        """
        params = (
            documento.entidad_tipo,
            documento.entidad_id,
            documento.nombre_archivo,
            documento.extension,
            documento.mime_type,
            documento.descripcion,
            documento.contenido,
            documento.version,
            "1" if documento.es_vigente else "0", # Store as string '1'/'0' to match DB TEXT column
            documento.created_by
        )
        
        try:
            conn = self.db.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            documento.id = cursor.lastrowid
            conn.commit()
            return documento
        except sqlite3.Error as e:
            pass  # print(f"Error al crear documento: {e}") [OpSec Removed]
            raise

    def listar_por_entidad(self, entidad_tipo: str, entidad_id: str) -> List[Documento]:
        """
        Retorna la metadata de los documentos vigentes de una entidad.
        NO TRAE EL CONTENIDO (BLOB) para optimizar rendimiento.
        """
        ph = self.db.get_placeholder()
        sql = f"""
        SELECT 
            ID, ENTIDAD_TIPO, ENTIDAD_ID, NOMBRE_ARCHIVO, EXTENSION, MIME_TYPE, 
            DESCRIPCION, VERSION, ES_VIGENTE, CREATED_AT, CREATED_BY
        FROM DOCUMENTOS
        WHERE ENTIDAD_TIPO = {ph} AND CAST(ENTIDAD_ID AS VARCHAR) = {ph} AND ES_VIGENTE = {ph}
        ORDER BY CREATED_AT DESC
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        # Use '1' for ES_VIGENTE to match TEXT type
        cursor.execute(sql, (entidad_tipo, str(entidad_id), "1"))
        rows = cursor.fetchall()
        return [self._row_to_entity(row, include_content=False) for row in rows]

    def obtener_por_id_con_contenido(self, id_documento: int) -> Optional[Documento]:
        """
        Retorna el documento completo INCLUYENDO EL CONTENIDO (BLOB).
        Usar solo cuando se vaya a visualizar o descargar el archivo.
        """
        ph = self.db.get_placeholder()
        sql = f"""
        SELECT 
            ID, ENTIDAD_TIPO, ENTIDAD_ID, NOMBRE_ARCHIVO, EXTENSION, MIME_TYPE, 
            DESCRIPCION, VERSION, ES_VIGENTE, CREATED_AT, CREATED_BY,
            CONTENIDO
        FROM DOCUMENTOS
        WHERE ID = {ph}
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(sql, (id_documento,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_entity(row, include_content=True)
        return None

    def anular_version_anterior(self, entidad_tipo: str, entidad_id: str, nombre_archivo: str):
        """
        Marca como 'NO VIGENTE' las versiones anteriores de un archivo con el mismo nombre
        para la misma entidad. Útil para el control de versiones.
        """
        ph = self.db.get_placeholder()
        sql = f"""
        UPDATE DOCUMENTOS 
        SET ES_VIGENTE = {ph} 
        WHERE ENTIDAD_TIPO = {ph} AND CAST(ENTIDAD_ID AS VARCHAR) = {ph} AND NOMBRE_ARCHIVO = {ph} AND ES_VIGENTE = {ph}
        """
        try:
            conn = self.db.obtener_conexion()
            cursor = conn.cursor()
            # Set to '0' where is '1'
            cursor.execute(sql, ("0", entidad_tipo, str(entidad_id), nombre_archivo, "1"))
            conn.commit()
        except sqlite3.Error as e:
            pass  # print(f"Error al anular versiones anteriores: {e}") [OpSec Removed]
            raise

    def obtener_ultima_version(self, entidad_tipo: str, entidad_id: str, nombre_archivo: str) -> int:
        """Retorna el número de la última versión registrada para ese archivo."""
        ph = self.db.get_placeholder()
        sql = f"""
        SELECT MAX(VERSION) 
        FROM DOCUMENTOS 
        WHERE ENTIDAD_TIPO = {ph} AND CAST(ENTIDAD_ID AS VARCHAR) = {ph} AND NOMBRE_ARCHIVO = {ph}
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(sql, (entidad_tipo, str(entidad_id), nombre_archivo))
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(sql, (entidad_tipo, str(entidad_id), nombre_archivo))
        row = cursor.fetchone()
        
        if row is None:
            return 0
            
        # Handle dict (Postgres) vs tuple/Row (SQLite)
        if hasattr(row, 'values'): 
            # RealDictCursor return dict, get the first value regardless of key name (max, MAX(version), etc)
            return list(row.values())[0] if list(row.values())[0] else 0
        else:
            # sqlite3.Row or tuple
            return row[0] if row[0] else 0

    def eliminar_logico(self, id_documento: int):
        """Marca un documento como no vigente (Soft Delete)."""
        ph = self.db.get_placeholder()
        sql = f"UPDATE DOCUMENTOS SET ES_VIGENTE = {ph} WHERE ID = {ph}"
        try:
            conn = self.db.obtener_conexion()
            cursor = conn.cursor()
            # Set to '0'
            cursor.execute(sql, ("0", id_documento))
            conn.commit()
        except sqlite3.Error as e:
            pass  # print(f"Error al eliminar documento: {e}") [OpSec Removed]
            raise
