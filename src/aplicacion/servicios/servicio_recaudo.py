"""
Servicio de Aplicación para la gestión de Recaudos (cobros a arrendatarios).
Coordina la lógica de negocio y la persistencia de pagos.
"""

from datetime import datetime
from typing import Dict, List, Optional

from src.dominio.entidades.recaudo import Recaudo
from src.dominio.entidades.recaudo_concepto import RecaudoConcepto
from src.dominio.interfaces.repositorio_recaudo import IRepositorioRecaudo
from src.infraestructura.persistencia.database import DatabaseManager

class ServicioRecaudo:
    """Servicio para orquestar operaciones de recaudos."""

    def __init__(self, repo_recaudo: IRepositorioRecaudo, db_manager: DatabaseManager):
        self.repo = repo_recaudo
        self.db = db_manager

    def generar_recaudos_mes_actual(self, usuario_sistema: str) -> Dict[str, int]:
        """
        Genera masivamente los recaudos de canon para todos los contratos activos 
        que aún no tengan un recaudo generado en el mes actual.
        
        Returns:
            Dict con el resumen: {"generados": int, "omitidos_por_duplicidad": int}
        """
        ahora = datetime.now()
        periodo_bd = ahora.strftime("%Y-%m")
        fecha_hoy = ahora.date().isoformat()
        
        meses_espanol = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]
        periodo_display = f"{meses_espanol[ahora.month - 1]} de {ahora.year}"

        # 1. Obtener contratos activos
        query_contratos = """
            SELECT ID_CONTRATO_A, CANON_ARRENDAMIENTO
            FROM CONTRATOS_ARRENDAMIENTOS
            WHERE ESTADO_CONTRATO_A = 'Activo'
        """
        
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query_contratos)
            contratos_activos = cursor.fetchall()

        if not contratos_activos:
            return {"generados": 0, "omitidos_por_duplicidad": 0}

        # 2. Obtener IDs de contratos que ya tienen recaudo este mes
        ids_ya_facturados = set(self.repo.obtener_ids_contratos_con_recaudo(periodo_bd))

        recaudos_a_crear = []
        omitidos = 0

        # 3. Filtrar y preparar entidades
        for contrato in contratos_activos:
            id_contrato = contrato["ID_CONTRATO_A"]
            canon = contrato["CANON_ARRENDAMIENTO"]

            if id_contrato in ids_ya_facturados:
                omitidos += 1
                continue

            if not canon or canon <= 0:
                continue

            recaudo = Recaudo(
                id_recaudo=None,
                id_contrato_a=id_contrato,
                fecha_pago=fecha_hoy,
                valor_total=canon,
                metodo_pago="Efectivo",
                referencia_bancaria=None,
                estado_recaudo="Pendiente",
                observaciones=f"Generación masiva - {periodo_display}",
                created_by=usuario_sistema
            )

            concepto = RecaudoConcepto(
                id_recaudo=None,
                tipo_concepto="Canon",
                periodo=periodo_bd,
                valor=canon
            )

            recaudos_a_crear.append((recaudo, [concepto]))

        # 4. Persistir masivamente
        generados = self.repo.crear_masivo(recaudos_a_crear, usuario_sistema)

        return {
            "generados": generados,
            "omitidos_por_duplicidad": omitidos
        }
