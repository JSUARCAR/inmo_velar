"""
Servicio de Aplicación: Desocupaciones
Gestiona la lógica de negocio para el proceso de desocupación de inmuebles.
"""

from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.desocupacion import Desocupacion, TareaDesocupacion
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_desocupacion_sqlite import (
    RepositorioDesocupacionSQLite,
)
from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite


class ServicioDesocupaciones:
    """Servicio para gestionar desocupaciones de contratos."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.repo = RepositorioDesocupacionSQLite(db_manager)
        self.repo_propiedad = RepositorioPropiedadSQLite(db_manager)

    def iniciar_desocupacion(
        self, id_contrato: int, fecha_programada: str, observaciones: Optional[str], usuario: str
    ) -> Desocupacion:
        """
        Inicia un nuevo proceso de desocupación.

        Args:
            id_contrato: ID del contrato a desocupar
            fecha_programada: Fecha esperada de entrega
            observaciones: Notas iniciales opcionales
            usuario: Usuario que inicia el proceso

        Returns:
            Desocupacion creada con tareas predefinidas

        Raises:
            ValueError: Si el contrato no está activo o ya tiene desocupación activa
        """
        # Validar que el contrato esté activo
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            placeholder = self.db_manager.get_placeholder()
            cursor.execute(
                f"""
                SELECT ESTADO_CONTRATO_A
                FROM CONTRATOS_ARRENDAMIENTOS
                WHERE ID_CONTRATO_A = {placeholder}
            """,
                (id_contrato,),
            )

            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Contrato {id_contrato} no encontrado")

            if row["ESTADO_CONTRATO_A"] != "Activo":
                raise ValueError("El contrato debe estar Activo para iniciar desocupación")

        # Verificar que no exista una desocupación con la misma fecha programada para este contrato
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            placeholder = self.db_manager.get_placeholder()
            cursor.execute(
                f"""
                SELECT ID_DESOCUPACION, ESTADO, FECHA_PROGRAMADA
                FROM DESOCUPACIONES
                WHERE ID_CONTRATO = {placeholder}
                  AND ESTADO IN ('En Proceso', 'Completada')
                  AND FECHA_PROGRAMADA = {placeholder}
            """,
                (id_contrato, fecha_programada),
            )

            desocupacion_existente = cursor.fetchone()
            if desocupacion_existente:
                estado = desocupacion_existente["ESTADO"]
                raise ValueError(
                    f"Este contrato ya tiene una desocupación con estado '{estado}' "
                    f"para la fecha programada {fecha_programada}. "
                    f"Seleccione una fecha diferente o cancele la desocupación existente."
                )

        # Crear desocupación
        desocupacion = Desocupacion(
            id_contrato=id_contrato,
            fecha_solicitud=datetime.now().date().isoformat(),
            fecha_programada=fecha_programada,
            estado="En Proceso",
            observaciones=observaciones,
            created_at=datetime.now().isoformat(),
            created_by=usuario,
        )

        return self.repo.crear(desocupacion)

    def listar_desocupaciones(self, estado: Optional[str] = None) -> List[Desocupacion]:
        """
        Lista desocupaciones con filtro opcional por estado.

        Args:
            estado: Filtro opcional ("En Proceso", "Completada", "Cancelada")

        Returns:
            Lista de desocupaciones con progreso calculado
        """
        return self.repo.listar_todas(estado=estado)

    def listar_desocupaciones_paginado(
        self, page: int = 1, page_size: int = 25, estado: Optional[str] = None
    ):
        """
        Lista desocupaciones con paginación.

        Args:
            page: Número de página (1-indexed)
            page_size: Cantidad de registros por página
            estado: Filtro opcional por estado

        Returns:
            PaginatedResult con items y total
        """
        from src.dominio.modelos.pagination import PaginatedResult

        items, total = self.repo.listar_todas_paginado(
            page=page, page_size=page_size, estado=estado
        )

        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    def obtener_desocupacion(self, id_desocupacion: int) -> Optional[Desocupacion]:
        """Obtiene una desocupación por su ID."""
        return self.repo.obtener_por_id(id_desocupacion)

    def obtener_checklist(self, id_desocupacion: int) -> List[TareaDesocupacion]:
        """
        Obtiene el checklist completo de una desocupación.

        Args:
            id_desocupacion: ID de la desocupación

        Returns:
            Lista de tareas ordenadas
        """
        return self.repo.obtener_tareas(id_desocupacion)

    def completar_tarea(self, id_tarea: int, usuario: str, observaciones: Optional[str] = None):
        """
        Marca una tarea como completada.

        Args:
            id_tarea: ID de la tarea a completar
            usuario: Usuario que completa la tarea
            observaciones: Notas opcionales sobre la tarea
        """
        self.repo.completar_tarea(id_tarea, usuario, observaciones)

    def calcular_progreso(self, id_desocupacion: int) -> dict:
        """
        Calcula el progreso de una desocupación.

        Returns:
            dict con 'porcentaje', 'completadas', 'total', 'puede_finalizar'
        """
        tareas = self.obtener_checklist(id_desocupacion)
        total = len(tareas)
        completadas = sum(1 for t in tareas if t.completada)
        porcentaje = int((completadas / total) * 100) if total > 0 else 0

        return {
            "porcentaje": porcentaje,
            "completadas": completadas,
            "total": total,
            "puede_finalizar": completadas == total,
        }

    def finalizar_desocupacion(self, id_desocupacion: int, usuario: str):
        """
        Finaliza una desocupación (marca como Completada y actualiza estados relacionados).
        Si hay tareas pendientes, las marca como completadas automáticamente (Forzar Finalización).

        Realiza las siguientes acciones (Transacción Atómica):
        1. Autocompleta tareas pendientes.
        2. Marca la desocupación como 'Completada'.
        3. Marca el contrato como 'Finalizado'.
           * El trigger de BD liberará automáticamente la propiedad.

        Args:
            id_desocupacion: ID de la desocupación a finalizar
            usuario: Usuario que finaliza

        Raises:
            ValueError: Si la desocupación no está en estado válido
        """
        # Obtener desocupación
        desocupacion = self.obtener_desocupacion(id_desocupacion)
        if not desocupacion:
            raise ValueError(f"Desocupación {id_desocupacion} no encontrada")

        # Permitir reintentar si está 'Completada' pero el contrato sigue Activo (Corrección de estado inconsistente)
        # Esto es útil para recuperar fallos previos como el reportado por el usuario.
        if desocupacion.estado not in ["En Proceso", "Completada"]:
            raise ValueError(f"Estado inválido para finalizar: {desocupacion.estado}")

        fecha_real = datetime.now().date().isoformat()
        timestamp = datetime.now().isoformat()

        try:
            with self.db_manager.obtener_conexion() as conn:
                cursor = self.db_manager.get_dict_cursor(conn)
                placeholder = self.db_manager.get_placeholder()

                # 1. Autocompletar tareas pendientes
                # (Lo hacemos directo en SQL para incluirlo en la transacción)
                update_tareas_query = f"""
                    UPDATE TAREAS_DESOCUPACION
                    SET COMPLETADA = 1,
                        FECHA_COMPLETADA = {placeholder},
                        RESPONSABLE = {placeholder},
                        OBSERVACIONES = CASE 
                            WHEN OBSERVACIONES IS NULL OR OBSERVACIONES = '' THEN 'Autocompletada por Finalización Forzada'
                            ELSE OBSERVACIONES
                        END
                    WHERE ID_DESOCUPACION = {placeholder} AND COMPLETADA = 0
                """
                cursor.execute(update_tareas_query, (timestamp, usuario, id_desocupacion))

                # 2. Actualizar desocupación a Completada
                update_desoc_query = f"""
                    UPDATE DESOCUPACIONES
                    SET ESTADO = 'Completada',
                        FECHA_REAL = {placeholder},
                        UPDATED_AT = {placeholder},
                        UPDATED_BY = {placeholder}
                    WHERE ID_DESOCUPACION = {placeholder}
                """
                cursor.execute(
                    update_desoc_query, (fecha_real, timestamp, usuario, id_desocupacion)
                )

                # 3. Actualizar contrato a Finalizado
                # El trigger TRG_ACTUALIZAR_DISPONIBILIDAD_LIBRE se encargará de liberar la propiedad.
                pass  # print(f"[DEBUG] Finalizando contrato {desocupacion.id_contrato}") [OpSec Removed]

                # Verificar primero si el contrato ya está finalizado para evitar updates redundantes
                check_contrato_query = f"SELECT ESTADO_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_CONTRATO_A = {placeholder}"
                cursor.execute(check_contrato_query, (desocupacion.id_contrato,))
                contrato_row = cursor.fetchone()

                if contrato_row and contrato_row["ESTADO_CONTRATO_A"] == "Activo":
                    update_contrato_query = f"""
                        UPDATE CONTRATOS_ARRENDAMIENTOS
                        SET ESTADO_CONTRATO_A = 'Finalizado',
                            MOTIVO_CANCELACION = 'Desocupación completada - ID {id_desocupacion}',
                            UPDATED_AT = {placeholder},
                            UPDATED_BY = {placeholder}
                        WHERE ID_CONTRATO_A = {placeholder}
                    """
                    cursor.execute(
                        update_contrato_query, (timestamp, usuario, desocupacion.id_contrato)
                    )
                    pass  # print(f"[SUCCESS] Contrato {desocupacion.id_contrato} finalizado.") [OpSec Removed]
                else:
                    pass  # print(f"[INFO] Contrato {desocupacion.id_contrato} ya estaba en estado {contrato_row['ESTADO_CONTRATO_A'] if contrato_row else 'No encontrado'}") [OpSec Removed]

                conn.commit()
                pass  # print(f"[SUCCESS] Desocupación {id_desocupacion} procesada exitosamente.") [OpSec Removed]

        except Exception as e:
            pass  # print(f"[ERROR] Transacción fallida al finalizar desocupación: {str(e)}") [OpSec Removed]
            raise e

    def cancelar_desocupacion(self, id_desocupacion: int, motivo: str, usuario: str):
        """
        Cancela una desocupación en proceso.

        Args:
            id_desocupacion: ID de la desocupación
            motivo: Razón de la cancelación
            usuario: Usuario que cancela
        """
        desocupacion = self.obtener_desocupacion(id_desocupacion)
        if not desocupacion:
            raise ValueError(f"Desocupación {id_desocupacion} no encontrada")

        if desocupacion.estado != "En Proceso":
            raise ValueError("Solo se pueden cancelar desocupaciones en proceso")

        # Actualizar observaciones con motivo de cancelación
        observaciones_actualizadas = f"{desocupacion.observaciones or ''}\n\nCANCELADA: {motivo}"

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            placeholder = self.db_manager.get_placeholder()
            cursor.execute(
                f"""
                UPDATE DESOCUPACIONES
                SET ESTADO = 'Cancelada',
                    OBSERVACIONES = {placeholder},
                    UPDATED_AT = {placeholder},
                    UPDATED_BY = {placeholder}
                WHERE ID_DESOCUPACION = {placeholder}
            """,
                (observaciones_actualizadas, datetime.now().isoformat(), usuario, id_desocupacion),
            )
            conn.commit()

    def listar_contratos_candidatos(self) -> List[dict]:
        """
        Lista contratos activos elegibles para iniciar desocupación.

        Returns:
            Lista de dicts con {id_contrato, direccion, inquilino}
        """
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(
                """
                SELECT 
                    ca.ID_CONTRATO_A, 
                    p.DIRECCION_PROPIEDAD,
                    per.NOMBRE_COMPLETO as INQUILINO
                FROM CONTRATOS_ARRENDAMIENTOS ca
                JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
                WHERE ca.ESTADO_CONTRATO_A = 'Activo'
                ORDER BY p.DIRECCION_PROPIEDAD
            """
            )

            contratos = []
            for row in cursor.fetchall():
                contratos.append(
                    {
                        "id_contrato": row["ID_CONTRATO_A"],
                        "direccion": row["DIRECCION_PROPIEDAD"],
                        "inquilino": row["INQUILINO"],
                    }
                )

            return contratos

    def obtener_datos_para_checklist(self, id_desocupacion: int) -> dict:
        """
        Obtiene los datos completos para generar el checklist de desocupación.

        Args:
            id_desocupacion: ID de la desocupación

        Returns:
            Dict con datos de desocupacion, contrato, propiedad y arrendatario
        """
        pass  # print(f"[DEBUG PDF] Servicio: Buscando datos para desocupación {id_desocupacion}") [OpSec Removed]
        desocupacion = self.obtener_desocupacion(id_desocupacion)
        if not desocupacion:
            pass  # print(f"[DEBUG PDF] ERROR: Desocupación {id_desocupacion} no encontrada en DB") [OpSec Removed]
            raise ValueError(f"Desocupación {id_desocupacion} no encontrada")

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            placeholder = self.db_manager.get_placeholder()
            cursor.execute(
                f"""
                SELECT 
                    ca.ID_CONTRATO_A,
                    ca.FECHA_INICIO_CONTRATO_A,
                    p.DIRECCION_PROPIEDAD,
                    p.MATRICULA_INMOBILIARIA,
                    per.NOMBRE_COMPLETO as INQUILINO,
                    per.NUMERO_DOCUMENTO,
                    per.TELEFONO_PRINCIPAL,
                    per.CORREO_ELECTRONICO
                FROM CONTRATOS_ARRENDAMIENTOS ca
                JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
                WHERE ca.ID_CONTRATO_A = {placeholder}
            """,
                (desocupacion.id_contrato,),
            )

            row = cursor.fetchone()
            if not row:
                pass  # print(f"[DEBUG PDF] ERROR: Contrato {desocupacion.id_contrato} no encontrado para desocupación {id_desocupacion}") [OpSec Removed]
                raise ValueError(f"Contrato {desocupacion.id_contrato} no encontrado")

            pass  # print(f"[DEBUG PDF] Datos encontrados. Inquilino: {row['inquilino']}") [OpSec Removed]
            return {
                "id_desocupacion": desocupacion.id_desocupacion,
                "fecha_solicitud": desocupacion.fecha_solicitud,
                "fecha_programada": desocupacion.fecha_programada,
                "estado": desocupacion.estado,
                "observaciones": desocupacion.observaciones,
                "id_contrato": row["id_contrato_a"],
                "fecha_contrato": row["fecha_inicio_contrato_a"],
                "direccion": row["direccion_propiedad"],
                "matricula": row["matricula_inmobiliaria"],
                "inquilino": row["inquilino"],
                "documento": row["numero_documento"],
                "telefono": row["telefono_principal"],
                "email": row["correo_electronico"],
            }
