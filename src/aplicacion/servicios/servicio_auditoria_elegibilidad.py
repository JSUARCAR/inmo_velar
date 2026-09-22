from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import logging
from src.infraestructura.persistencia.database import db_manager

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class CriteriosAuditoria:
    fecha_reconstruccion: str
    filtro_regla: str
    periodo: str

@dataclass(frozen=True)
class LiquidacionInelegible:
    id_liquidacion: int
    periodo: str
    fecha_generacion: str
    id_propiedad: int
    direccion_propiedad: str
    id_propietario: int
    nombre_propietario: str
    motivo: str

@dataclass(frozen=True)
class AuditoriaElegibilidadResultado:
    criterios: CriteriosAuditoria
    liquidaciones_auditadas: int
    no_elegibles: List[LiquidacionInelegible]

class ServicioAuditoriaElegibilidad:
    def auditar(self, periodo: Optional[str] = None, fecha_reconstruccion: Optional[str] = None) -> AuditoriaElegibilidadResultado:
        fecha_rec = fecha_reconstruccion or datetime.now().isoformat()
        filtro = "Todos" if not periodo else periodo
        criterios = CriteriosAuditoria(fecha_reconstruccion=fecha_rec, filtro_regla="mandato_activo + arrendamiento_activo (misma ID_PROPIEDAD)", periodo=filtro)
        
        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            query = """
            SELECT l.ID_LIQUIDACION, l.PERIODO, l.FECHA_GENERACION, 
                   cm.ID_PROPIEDAD, p.DIRECCION_PROPIEDAD, 
                   cm.ID_PROPIETARIO, COALESCE(per.NOMBRE_COMPLETO, 'DESCONOCIDO') as NOMBRE_PROPIETARIO,
                   CASE WHEN l.FECHA_GENERACION >= cm.FECHA_INICIO_CONTRATO_M AND (cm.FECHA_FIN_CONTRATO_M IS NULL OR l.FECHA_GENERACION <= cm.FECHA_FIN_CONTRATO_M) THEN cm.ESTADO_CONTRATO_M ELSE 'INACTIVO' END as ESTADO_CONTRATO_M,
                   (SELECT ca.ESTADO_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS ca WHERE ca.ID_PROPIEDAD = cm.ID_PROPIEDAD AND l.FECHA_GENERACION >= ca.FECHA_INICIO_CONTRATO_A AND (ca.FECHA_FIN_CONTRATO_A IS NULL OR l.FECHA_GENERACION <= ca.FECHA_FIN_CONTRATO_A) ORDER BY ca.FECHA_INICIO_CONTRATO_A DESC LIMIT 1) as ESTADO_CONTRATO_A
            FROM LIQUIDACIONES l
            JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
            JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
            LEFT JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
            LEFT JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
            """
            params = []
            if periodo:
                query += " WHERE l.PERIODO = %s"
                params.append(periodo)
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            no_elegibles = []
            for r in rows:
                m_activo = r['ESTADO_CONTRATO_M'] == 'ACTIVO'
                a_activo = r['ESTADO_CONTRATO_A'] == 'ACTIVO'
                if not m_activo and not a_activo:
                    motivo = "sin contrato de mandato activo y sin contrato de arrendamiento activo"
                elif not m_activo:
                    motivo = "sin contrato de mandato activo"
                elif not a_activo:
                    motivo = "sin contrato de arrendamiento activo en esta propiedad"
                else:
                    continue
                no_elegibles.append(LiquidacionInelegible(
                    id_liquidacion=r['ID_LIQUIDACION'],
                    periodo=r['PERIODO'],
                    fecha_generacion=str(r['FECHA_GENERACION']),
                    id_propiedad=r['ID_PROPIEDAD'],
                    direccion_propiedad=r['DIRECCION_PROPIEDAD'],
                    id_propietario=r['ID_PROPIETARIO'],
                    nombre_propietario=r['NOMBRE_PROPIETARIO'],
                    motivo=motivo
                ))
        
        logger.info(f"Auditora ejecutada: {criterios}")
        return AuditoriaElegibilidadResultado(criterios=criterios, liquidaciones_auditadas=len(rows), no_elegibles=no_elegibles)

