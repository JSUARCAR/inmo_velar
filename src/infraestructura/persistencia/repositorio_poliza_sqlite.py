"""
Repositorio SQLite para la entidad PolizaSeguro.
"""

from typing import List, Optional
from datetime import datetime
from src.dominio.entidades.poliza import PolizaSeguro
from src.infraestructura.persistencia.database import DatabaseManager

class RepositorioPolizaSQLite:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self._ensure_table()

    def _ensure_table(self):
        if self.db.use_postgresql:
            return
        """Asegura que la tabla POLIZAS exista."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        
        # Este método usa DDL específico, puede requerir ajuste para PostgreSQL si no fuera compatible
        # Pero CREATE TABLE es bastante estándar. AUTOINCREMENT vs SERIAL es la diferencia.
        # Por ahora lo dejamos como está en SQLite, asumiendo que el usuario no borrará el archivo de migración
        # Ojo: si esto corre en Postgres fallará por syntax. 
        # Pero el objetivo es que funcione en Postgres YA migrado. Este metodo podría sobrar.
        # Dejémoslo con try/pass o solo para sqlite.
        if not self.db.use_postgresql:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS POLIZAS (
                    ID_POLIZA INTEGER PRIMARY KEY AUTOINCREMENT,
                    ID_CONTRATO INTEGER NOT NULL,
                    ID_SEGURO INTEGER NOT NULL,
                    FECHA_INICIO TEXT NOT NULL,
                    FECHA_FIN TEXT NOT NULL,
                    NUMERO_POLIZA TEXT,
                    ESTADO TEXT DEFAULT 'Activa',
                    CREATED_AT TEXT,
                    CREATED_BY TEXT,
                    UPDATED_AT TEXT,
                    UPDATED_BY TEXT,
                    FOREIGN KEY(ID_CONTRATO) REFERENCES CONTRATOS_ARRENDAMIENTOS(ID_CONTRATO_A),
                    FOREIGN KEY(ID_SEGURO) REFERENCES SEGUROS(ID_SEGURO)
                )
            """)
            conn.commit()

    def _row_to_entity(self, row, with_joins=False) -> PolizaSeguro:
        # Manejar tanto sqlite3.Row como dict (PostgreSQL)
        if row is None:
            return None
            
        if hasattr(row, 'keys'):
            row_dict = dict(row)
            # Adaptación para índices numéricos si el código original usaba row[0]
            # Si el código original usaba row[0], row[1], PostgreSQL dict NO SOPORTA indices.
            # DEBO CAMBIAR a nombres de columnas si uso dict cursor.
            # O usar row_factory=None en Postgres para tener tuplas? No, RealDictCursor es dict.
            # Si el código original usaba índices, DEBO reescribirlo para usar nombres.
            # Este repositorio usaba row[0], row[1]...
            
            # Mapeo basado en el SELECT del código original
            entidad = PolizaSeguro(
                id_poliza=row_dict.get('id_poliza') or row_dict.get('ID_POLIZA'),
                id_contrato=row_dict.get('id_contrato') or row_dict.get('ID_CONTRATO'),
                id_seguro=row_dict.get('id_seguro') or row_dict.get('ID_SEGURO'),
                fecha_inicio=row_dict.get('fecha_inicio') or row_dict.get('FECHA_INICIO'),
                fecha_fin=row_dict.get('fecha_fin') or row_dict.get('FECHA_FIN'),
                numero_poliza=row_dict.get('numero_poliza') or row_dict.get('NUMERO_POLIZA'),
                estado=row_dict.get('estado') or row_dict.get('ESTADO'),
                created_at=row_dict.get('created_at') or row_dict.get('CREATED_AT'),
                created_by=row_dict.get('created_by') or row_dict.get('CREATED_BY'),
                updated_at=row_dict.get('updated_at') or row_dict.get('UPDATED_AT'),
                updated_by=row_dict.get('updated_by') or row_dict.get('UPDATED_BY')
            )
            if with_joins:
                entidad.nombre_seguro = row_dict.get('nombre_seguro') or row_dict.get('NOMBRE_SEGURO')
                entidad.propiedad_info = row_dict.get('direccion_propiedad') or row_dict.get('DIRECCION_PROPIEDAD')
                entidad.inquilino_info = row_dict.get('inquilino') or row_dict.get('INQUILINO')
            return entidad
        else:
            # Fallback para SQLite si usa row_factory=None o tuplas (pero usaba Row)
            # Row soporta indices y nombres.
            entidad = PolizaSeguro(
                id_poliza=row['ID_POLIZA'],
                id_contrato=row['ID_CONTRATO'],
                id_seguro=row['ID_SEGURO'],
                fecha_inicio=row['FECHA_INICIO'],
                fecha_fin=row['FECHA_FIN'],
                numero_poliza=row['NUMERO_POLIZA'],
                estado=row['ESTADO'],
                created_at=row['CREATED_AT'],
                created_by=row['CREATED_BY'],
                updated_at=row['UPDATED_AT'],
                updated_by=row['UPDATED_BY']
            )
            if with_joins:
                entidad.nombre_seguro = row['NOMBRE_SEGURO']
                entidad.propiedad_info = row['DIRECCION_PROPIEDAD']
                entidad.inquilino_info = row['INQUILINO']
            return entidad

    def crear(self, poliza: PolizaSeguro, usuario: str) -> PolizaSeguro:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()
        ahora = datetime.now().replace(microsecond=0).isoformat()
        
        cursor.execute(f"""
            INSERT INTO POLIZAS (
                ID_CONTRATO, ID_SEGURO, FECHA_INICIO, FECHA_FIN, 
                NUMERO_POLIZA, ESTADO, CREATED_AT, CREATED_BY
            ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """, (
            poliza.id_contrato, poliza.id_seguro, poliza.fecha_inicio,
            poliza.fecha_fin, poliza.numero_poliza, poliza.estado,
            ahora, usuario
        ))
        conn.commit()
        poliza.id_poliza = self.db.get_last_insert_id(cursor, 'POLIZAS', 'ID_POLIZA')
        poliza.created_at = ahora
        poliza.created_by = usuario
        return poliza

    def listar_todas(self) -> List[PolizaSeguro]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
        # Join para traer info extra útil en UI
        cursor.execute(f"""
            SELECT 
                p.ID_POLIZA, p.ID_CONTRATO, p.ID_SEGURO, 
                p.FECHA_INICIO, p.FECHA_FIN, p.NUMERO_POLIZA, p.ESTADO,
                p.CREATED_AT, p.CREATED_BY, p.UPDATED_AT, p.UPDATED_BY,
                s.NOMBRE_SEGURO,
                prop.DIRECCION_PROPIEDAD,
                per.NOMBRE_COMPLETO as INQUILINO
            FROM POLIZAS p
            JOIN SEGUROS s ON p.ID_SEGURO = s.ID_SEGURO
            JOIN CONTRATOS_ARRENDAMIENTOS ca ON p.ID_CONTRATO = ca.ID_CONTRATO_A
            JOIN PROPIEDADES prop ON ca.ID_PROPIEDAD = prop.ID_PROPIEDAD
            JOIN PERSONAS per ON ca.ID_ARRENDATARIO = per.ID_PERSONA
            ORDER BY p.FECHA_FIN ASC
        """)
        rows = cursor.fetchall()
        return [self._row_to_entity(row, with_joins=True) for row in rows]

    def actualizar_estado(self, id_poliza: int, nuevo_estado: str, usuario: str):
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()
        ahora = datetime.now().replace(microsecond=0).isoformat()
        cursor.execute(f"""
            UPDATE POLIZAS SET ESTADO = {placeholder}, UPDATED_AT = {placeholder}, UPDATED_BY = {placeholder}
            WHERE ID_POLIZA = {placeholder}
        """, (nuevo_estado, ahora, usuario, id_poliza))
        conn.commit()
