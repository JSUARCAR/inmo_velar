"""
Servicio de Aplicación: Gestión de Contratos
Coordina la lógica de negocio para contratos de mandato y arrendamiento.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.dominio.entidades.contrato_arrendamiento import ContratoArrendamiento
from src.dominio.entidades.contrato_mandato import ContratoMandato
from src.dominio.entidades.renovacion_contrato import RenovacionContrato

# Integración Fase 3: CacheManager e Interfaces
from src.aplicacion.servicios.servicio_contrato_arrendamiento import (
    ServicioContratoArrendamiento,
)
from src.aplicacion.servicios.servicio_contrato_mandato import ServicioContratoMandato
from src.infraestructura.cache.cache_manager import cache_manager
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import (
    RepositorioArrendatarioSQLite,
)
from src.infraestructura.persistencia.repositorio_codeudor_sqlite import RepositorioCodeudorSQLite
from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import (
    RepositorioContratoArrendamientoSQLite,
)
from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import (
    RepositorioContratoMandatoSQLite,
)
from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite
from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite
from src.infraestructura.persistencia.repositorio_renovacion_sqlite import (
    RepositorioRenovacionSQLite,
)


class ServicioContratos:
    def __init__(
        self,
        db_manager: DatabaseManager,
        repo_mandato: RepositorioContratoMandatoSQLite,
        repo_arriendo: RepositorioContratoArrendamientoSQLite,
        repo_propiedad: RepositorioPropiedadSQLite,
        repo_renovacion: RepositorioRenovacionSQLite,
        repo_ipc: RepositorioIPCSQLite,
        repo_arrendatario: RepositorioArrendatarioSQLite,
        repo_codeudor: RepositorioCodeudorSQLite
    ):
        self.db = db_manager
        self.repo_mandato = repo_mandato
        self.repo_arriendo = repo_arriendo
        self.repo_propiedad = repo_propiedad
        self.repo_renovacion = repo_renovacion
        self.repo_ipc = repo_ipc

        # Servicios especializados (SRP)
        self.servicio_mandato = ServicioContratoMandato(
            self.repo_mandato, self.repo_propiedad, self.repo_renovacion
        )
        self.servicio_arriendo = ServicioContratoArrendamiento(
            self.repo_arriendo, self.repo_propiedad, self.repo_renovacion, self.repo_ipc
        )

        # Repositorios auxiliares
        self.repo_arrendatario = repo_arrendatario
        self.repo_codeudor = repo_codeudor

    # =========================================================================
    # DROPDOWN HELPERS
    # =========================================================================

    def obtener_propiedades_sin_mandato_activo(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de propiedades que NO tienen contrato de mandato activo.
        Útil para el dropdown de Creación de Mandato.
        """
        query = """
        SELECT p.ID_PROPIEDAD, p.MATRICULA_INMOBILIARIA, p.DIRECCION_PROPIEDAD, p.CANON_ARRENDAMIENTO_ESTIMADO
        FROM PROPIEDADES p
        WHERE p.ESTADO_REGISTRO = TRUE
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
            return [
                {
                    "id": row["ID_PROPIEDAD"],
                    "texto": f"{row['MATRICULA_INMOBILIARIA']} - {row['DIRECCION_PROPIEDAD']}",
                    "canon": row["CANON_ARRENDAMIENTO_ESTIMADO"],
                }
                for row in cursor.fetchall()
            ]

    def obtener_propiedades_para_arrendamiento(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de propiedades con Mandato Activo y SIN Arriendo Activo.
        Útil para el dropdown de Creación de Arrendamiento.
        """
        query = """
        SELECT p.ID_PROPIEDAD, p.MATRICULA_INMOBILIARIA, p.DIRECCION_PROPIEDAD, p.CANON_ARRENDAMIENTO_ESTIMADO
        FROM PROPIEDADES p
        JOIN CONTRATOS_MANDATOS cm ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD
        WHERE p.ESTADO_REGISTRO = TRUE
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
            return [
                {
                    "id": row["ID_PROPIEDAD"],
                    "texto": f"{row['MATRICULA_INMOBILIARIA']} - {row['DIRECCION_PROPIEDAD']}",
                    "canon": row["CANON_ARRENDAMIENTO_ESTIMADO"],
                }
                for row in cursor.fetchall()
            ]

    # =========================================================================
    # GESTIÓN DE MANDATOS
    # =========================================================================

    def crear_mandato(self, datos: Dict, usuario_sistema: str) -> ContratoMandato:
        return self.servicio_mandato.crear_mandato(datos, usuario_sistema)

    def obtener_mandato_activo(self, id_propiedad: int) -> Optional[ContratoMandato]:
        return self.servicio_mandato.repo_mandato.obtener_activo_por_propiedad(id_propiedad)

    def obtener_mandato_por_id(self, id_contrato: int) -> Optional[ContratoMandato]:
        return self.servicio_mandato.obtener_mandato(id_contrato)

    @cache_manager.invalidates("mandatos:list_paginated")
    def actualizar_mandato(self, id_contrato: int, datos: Dict, usuario_sistema: str) -> None:
        return self.servicio_mandato.actualizar_mandato(id_contrato, datos, usuario_sistema)
        """
        Actualiza un contrato de mandato existente.
        """
        pass  # print(f">>> DEBUG [ServicioContratos]: actualizar_mandato(id={id_contrato})") [OpSec Removed]
        pass  # print(f">>> DEBUG [ServicioContratos]: Datos recibidos: {datos}") [OpSec Removed]

        mandato = self.repo_mandato.obtener_por_id(id_contrato)
        if not mandato:
            pass  # print(f">>> DEBUG [ServicioContratos]: Contrato no encontrado") [OpSec Removed]
            raise ValueError(f"No existe el contrato de mandato con ID {id_contrato}")

        pass  # print(f">>> DEBUG [ServicioContratos]: Estado previo: {mandato}") [OpSec Removed]

        # Actualizar campos (IDs pueden cambiar en edición)
        mandato.id_propiedad = datos.get("id_propiedad", mandato.id_propiedad)
        mandato.id_propietario = datos.get("id_propietario", mandato.id_propietario)
        mandato.id_asesor = datos.get("id_asesor", mandato.id_asesor)

        # Actualizar fechas y condiciones
        mandato.fecha_inicio_contrato_m = datos.get("fecha_inicio", mandato.fecha_inicio_contrato_m)
        mandato.fecha_fin_contrato_m = datos.get("fecha_fin", mandato.fecha_fin_contrato_m)
        mandato.duracion_contrato_m = datos.get("duracion_meses", mandato.duracion_contrato_m)
        mandato.canon_mandato = datos.get("canon", mandato.canon_mandato)
        mandato.comision_porcentaje_contrato_m = datos.get(
            "comision_porcentaje", mandato.comision_porcentaje_contrato_m
        )

        # Actualizar metadatos
        mandato.updated_by = usuario_sistema
        mandato.updated_at = datetime.now().isoformat()

        pass  # print(f">>> DEBUG [ServicioContratos]: Estado actualizado: {mandato}") [OpSec Removed]
        pass  # print(f">>> DEBUG [ServicioContratos]: Llamando repo.actualizar...") [OpSec Removed]
        self.repo_mandato.actualizar(mandato, usuario_sistema)
        pass  # print(f">>> DEBUG [ServicioContratos]: repo.actualizar finalizado.") [OpSec Removed]

    def listar_mandatos(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de mandatos para la vista principal.
        Incluye datos de Propiedad y Propietario.
        """
        query = """
        SELECT 
            cm.ID_CONTRATO_M,
            cm.ESTADO_CONTRATO_M,
            cm.CANON_MANDATO,
            cm.FECHA_INICIO_CONTRATO_M,
            cm.FECHA_FIN_CONTRATO_M,
            p.DIRECCION_PROPIEDAD,
            per.NOMBRE_COMPLETO as PROPIETARIO,
            per.NUMERO_DOCUMENTO
        FROM CONTRATOS_MANDATOS cm
        JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
        JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
        ORDER BY cm.ID_CONTRATO_M DESC
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query)
            return [
                {
                    "id": row["ID_CONTRATO_M"],
                    "estado": row["ESTADO_CONTRATO_M"],
                    "canon": row["CANON_MANDATO"],
                    "fecha_inicio": row["FECHA_INICIO_CONTRATO_M"],
                    "fecha_fin": row["FECHA_FIN_CONTRATO_M"],
                    "propiedad": row["DIRECCION_PROPIEDAD"],
                    "propietario": row["PROPIETARIO"],
                    "documento_propietario": row["NUMERO_DOCUMENTO"],
                }
                for row in cursor.fetchall()
            ]

    # Integración Fase 4: Paginación
    def listar_mandatos_paginado(self, **kwargs) -> Any:
        return self.servicio_mandato.listar_mandatos_paginado(**kwargs)

    def listar_mandatos_activos(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de mandatos ACTIVOS para dropdowns.
        """
        query = """
        SELECT 
            cm.ID_CONTRATO_M,
            p.DIRECCION_PROPIEDAD,
            per.NOMBRE_COMPLETO as PROPIETARIO,
            cm.CANON_MANDATO,
            cm.COMISION_PORCENTAJE_CONTRATO_M
        FROM CONTRATOS_MANDATOS cm
        JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
        JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
        WHERE cm.ESTADO_CONTRATO_M = 'Activo'
        ORDER BY p.DIRECCION_PROPIEDAD
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query)
            return [
                {
                    "id": row["ID_CONTRATO_M"],
                    "texto": f"{row['DIRECCION_PROPIEDAD']} - {row['PROPIETARIO']}",  # Direccion - Propietario
                    "canon": row["CANON_MANDATO"],
                    "comision": row["COMISION_PORCENTAJE_CONTRATO_M"],
                }
                for row in cursor.fetchall()
            ]

    # =========================================================================
    # GESTIÓN DE ARRENDAMIENTOS
    # =========================================================================

    def crear_arrendamiento(self, datos: Dict, usuario_sistema: str) -> ContratoArrendamiento:
        return self.servicio_arriendo.crear_arrendamiento(datos, usuario_sistema)

    def obtener_arrendamiento_activo(self, id_propiedad: int) -> Optional[ContratoArrendamiento]:
        return self.servicio_arriendo.repo_arriendo.obtener_activo_por_propiedad(id_propiedad)

    def obtener_arrendamiento_por_id(self, id_contrato: int) -> Optional[ContratoArrendamiento]:
        return self.servicio_arriendo.obtener_arrendamiento(id_contrato)

    @cache_manager.invalidates("arriendos:list_paginated")
    def actualizar_arrendamiento(self, id_contrato: int, datos: Dict, usuario_sistema: str) -> None:
        return self.servicio_arriendo.actualizar_arrendamiento(id_contrato, datos, usuario_sistema)
        """
        Actualiza un contrato de arrendamiento existente.
        Nota: No actualiza propiedad ni inquilinos, solo condiciones.
        """
        arriendo = self.repo_arriendo.obtener_por_id(id_contrato)
        if not arriendo:
            raise ValueError(f"No existe el contrato de arrendamiento con ID {id_contrato}")

        # Actualizar campos permitidos
        arriendo.fecha_fin_contrato_a = datos.get("fecha_fin", arriendo.fecha_fin_contrato_a)
        arriendo.canon_arrendamiento = datos.get("canon", arriendo.canon_arrendamiento)

        # El repositorio actualiza: FECHA_FIN, CANON, ESTADO, MOTIVO, ALERTAS...
        # No actualiza: DEPOSITO, DURACION (?), PROPIEDAD, ARRENDATARIO

        arriendo.updated_by = usuario_sistema
        arriendo.updated_at = datetime.now().isoformat()

        self.repo_arriendo.actualizar(arriendo, usuario_sistema)

    @cache_manager.invalidates("arriendos:list_paginated")
    def renovar_arrendamiento(
        self, id_contrato: int, usuario_sistema: str
    ) -> ContratoArrendamiento:
        return self.servicio_arriendo.renovar_arrendamiento(id_contrato, usuario_sistema)

    @cache_manager.invalidates("mandatos:list_paginated")
    def renovar_mandato(self, id_contrato: int, usuario_sistema: str) -> ContratoMandato:
        return self.servicio_mandato.renovar_mandato(id_contrato, usuario_sistema)

    @cache_manager.invalidates("arriendos:list_paginated")
    def terminar_arrendamiento(self, id_contrato: int, motivo: str, usuario_sistema: str) -> None:
        return self.servicio_arriendo.terminar_arrendamiento(id_contrato, motivo, usuario_sistema)

    @cache_manager.invalidates("mandatos:list_paginated")
    def terminar_mandato(self, id_contrato: int, motivo: str, usuario_sistema: str) -> None:
        return self.servicio_mandato.terminar_mandato(id_contrato, motivo, usuario_sistema)

    def _verificar_paz_y_salvo(self, id_contrato: int) -> bool:
        """
        STUB: Verifica si el contrato está al día.
        En el futuro conectará con módulo de Pagos/Cartera.
        """
        # TODO: Implementar lógica real con tabla PAGOS
        return True

    def _calcular_incremento_ipc(self, canon_actual: int) -> tuple[int, float]:
        """
        Retorna (nuevo_canon, porcentaje_usado).
        """
        ipc = self.repo_ipc.obtener_ultimo()
        if not ipc:
            pass  # print(">>> WARNING: No hay IPC registrado. Incremento 0%.") [OpSec Removed]
            return canon_actual, 0.0

        # IPC.valor_ipc viene como entero/float. Asumimos que viene "4.5" para 4.5% o "13" para 13%
        # Ajustar según definicion de entidad. En view_file IPC era valor_ipc: int.
        # Asumimos que es porcentaje entero o float.
        porcentaje = float(ipc.valor_ipc)

        incremento = canon_actual * (porcentaje / 100)
        nuevo_canon = int(canon_actual + incremento)

        # Regla de negocio habitual: Redondear a miles?
        # Por ahora exacto (entero).
        return nuevo_canon, porcentaje

    def listar_arrendamientos(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de arrendamientos para la vista principal.
        Incluye datos de Propiedad y Arrendatario.
        """
        query = """
        SELECT 
            ca.ID_CONTRATO_A,
            ca.ESTADO_CONTRATO_A,
            ca.CANON_ARRENDAMIENTO,
            ca.FECHA_INICIO_CONTRATO_A,
            ca.FECHA_FIN_CONTRATO_A,
            p.DIRECCION_PROPIEDAD,
            per.NOMBRE_COMPLETO as ARRENDATARIO,
            per.NUMERO_DOCUMENTO
        FROM CONTRATOS_ARRENDAMIENTOS ca
        JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
        JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
        ORDER BY ca.ID_CONTRATO_A DESC
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query)
            return [
                {
                    "id": row["ID_CONTRATO_A"],
                    "estado": row["ESTADO_CONTRATO_A"],
                    "canon": row["CANON_ARRENDAMIENTO"],
                    "fecha_inicio": row["FECHA_INICIO_CONTRATO_A"],
                    "fecha_fin": row["FECHA_FIN_CONTRATO_A"],
                    "propiedad": row["DIRECCION_PROPIEDAD"],
                    "arrendatario": row["ARRENDATARIO"],
                    "documento_arrendatario": row["NUMERO_DOCUMENTO"],
                }
                for row in cursor.fetchall()
            ]

    # Integración Fase 4: Paginación
    def listar_arrendamientos_paginado(self, **kwargs) -> Any:
        return self.servicio_arriendo.listar_arrendamientos_paginado(**kwargs)

    def listar_arrendamientos_por_vencer(self, dias_antelacion: int = 60) -> List[Dict[str, Any]]:
        """
        Lista contratos de arrendamiento que vencen en los próximos N días.
        """
        fecha_limite = (datetime.now() + timedelta(days=dias_antelacion)).strftime("%Y-%m-%d")
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")

        query = """
        SELECT 
            ca.ID_CONTRATO_A,
            ca.FECHA_FIN_CONTRATO_A,
            p.DIRECCION_PROPIEDAD,
            per.NOMBRE_COMPLETO as ARRENDATARIO
        FROM CONTRATOS_ARRENDAMIENTOS ca
        JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
        JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
        WHERE ca.ESTADO_CONTRATO_A = 'Activo'
          AND ca.FECHA_FIN_CONTRATO_A <= ?
          AND ca.FECHA_FIN_CONTRATO_A >= ?
        ORDER BY ca.FECHA_FIN_CONTRATO_A ASC
        """
        # Note: Using '?' for simplicity here, but should use self.db.get_placeholder() if strictly following pattern.
        # Given this is likely SQLite/Postgres hybrid, let's stick to get_placeholder if possible or adjust.
        # However, replace_file_content is static text. I'll use logic inside.

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()

            # Replace ? with placeholder dynamically in Python code? No, I must write the code.
            # I will use f-string with placeholder call if I can, but I can't inject variable in Replace tool easily.
            # I'll write the code to use db.get_placeholder()

            final_query = query.replace("?", placeholder)

            cursor.execute(final_query, (fecha_limite, fecha_hoy))
            return [
                {
                    "id": row["ID_CONTRATO_A"],
                    "fecha_fin": row["FECHA_FIN_CONTRATO_A"],
                    "propiedad": row["DIRECCION_PROPIEDAD"],
                    "arrendatario": row["ARRENDATARIO"],
                    "dias_restantes": (
                        datetime.strptime(row["FECHA_FIN_CONTRATO_A"], "%Y-%m-%d") - datetime.now()
                    ).days,
                }
                for row in cursor.fetchall()
            ]

    def exportar_contratos_csv(
        self,
        filtro_tipo: str = "Todos",
        estado: Optional[str] = None,
        busqueda: Optional[str] = None,
    ) -> str:
        """
        Genera un CSV con el listado de contratos según filtros.
        Columnas: ID, Tipo, Propiedad, Propietario/Inquilino, Estado, Canon, Inicio, Fin.
        """
        import csv
        import io

        # Helper para obtener valor seguro de diccionario (case insensitive fallback)
        def get_val(row: dict, keys: list) -> Any:
            for k in keys:
                if k in row:
                    return row[k]
                if k.lower() in row:
                    return row[k.lower()]
                if k.upper() in row:
                    return row[k.upper()]
            return ""

        # 1. Obtener datos (sin paginación)
        items = []

        # Mandatos
        if filtro_tipo in ["Todos", "Mandato"]:
            resultado_mandatos = self._listar_todos_mandatos(estado, busqueda)
            for m in resultado_mandatos:
                items.append(
                    {
                        "id": get_val(m, ["ID_CONTRATO_M", "id"]),
                        "tipo": "Mandato",
                        "estado": get_val(m, ["ESTADO_CONTRATO_M", "estado"]),
                        "propiedad": get_val(m, ["DIRECCION_PROPIEDAD", "propiedad"]),
                        "persona": get_val(
                            m, ["PROPIETARIO", "nombre_propietario", "nombre_completo"]
                        ),
                        "documento": get_val(m, ["NUMERO_DOCUMENTO", "documento_propietario"]),
                        "canon": get_val(m, ["CANON_MANDATO", "canon"]),
                        "fecha_inicio": get_val(m, ["FECHA_INICIO_CONTRATO_M", "fecha_inicio"]),
                        "fecha_fin": get_val(m, ["FECHA_FIN_CONTRATO_M", "fecha_fin"]),
                    }
                )

        # Arrendamientos
        if filtro_tipo in ["Todos", "Arrendamiento"]:
            resultado_arriendos = self._listar_todos_arrendamientos(estado, busqueda)
            for a in resultado_arriendos:
                items.append(
                    {
                        "id": get_val(a, ["ID_CONTRATO_A", "id"]),
                        "tipo": "Arrendamiento",
                        "estado": get_val(a, ["ESTADO_CONTRATO_A", "estado"]),
                        "propiedad": get_val(a, ["DIRECCION_PROPIEDAD", "propiedad"]),
                        "persona": get_val(a, ["ARRENDATARIO", "nombre_b", "nombre_completo"]),
                        "documento": get_val(a, ["NUMERO_DOCUMENTO", "documento"]),
                        "canon": get_val(a, ["CANON_ARRENDAMIENTO", "canon"]),
                        "fecha_inicio": get_val(a, ["FECHA_INICIO_CONTRATO_A", "fecha_inicio"]),
                        "fecha_fin": get_val(a, ["FECHA_FIN_CONTRATO_A", "fecha_fin"]),
                    }
                )

        # 2. Generar CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(
            [
                "ID",
                "TIPO",
                "ESTADO",
                "PROPIEDAD",
                "PERSONA (Propietario/Inquilino)",
                "DOCUMENTO",
                "CANON",
                "FECHA INICIO",
                "FECHA FIN",
            ]
        )

        # Data
        for item in items:
            writer.writerow(
                [
                    item["id"],
                    item["tipo"],
                    item["estado"],
                    item["propiedad"],
                    item["persona"],
                    item["documento"],
                    item["canon"],
                    item["fecha_inicio"],
                    item["fecha_fin"],
                ]
            )

        return output.getvalue()

    def _listar_todos_mandatos(self, estado, busqueda):
        """Helper para exportación: Trae mandatos sin paginación."""
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()

            base_query = """
                SELECT 
                    cm.ID_CONTRATO_M as id,
                    cm.ESTADO_CONTRATO_M as estado,
                    cm.CANON_MANDATO as canon,
                    cm.FECHA_INICIO_CONTRATO_M as fecha_inicio,
                    cm.FECHA_FIN_CONTRATO_M as fecha_fin,
                    p.DIRECCION_PROPIEDAD as propiedad,
                    per.NOMBRE_COMPLETO as propietario,
                    per.NUMERO_DOCUMENTO as documento_propietario
                FROM CONTRATOS_MANDATOS cm
                JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN PROPIETARIOS prop ON cm.ID_PROPIEDAD = prop.ID_PROPIEDAD -- Correction: ID_PROPIETARIO usually linked via mandate or prop? Mandato structure: cm.ID_PROPIETARIO
                JOIN PROPIETARIOS prop_correct ON cm.ID_PROPIETARIO = prop_correct.ID_PROPIETARIO
                JOIN PERSONAS per ON prop_correct.ID_PERSONA = per.ID_PERSONA
            """
            # Correction on JOIN: The previous listar_mandatos had:
            # JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO

            base_query = """
                SELECT 
                    cm.ID_CONTRATO_M as id,
                    cm.ESTADO_CONTRATO_M as estado,
                    cm.CANON_MANDATO as canon,
                    cm.FECHA_INICIO_CONTRATO_M as fecha_inicio,
                    cm.FECHA_FIN_CONTRATO_M as fecha_fin,
                    p.DIRECCION_PROPIEDAD as propiedad,
                    per.NOMBRE_COMPLETO as propietario,
                    per.NUMERO_DOCUMENTO as documento_propietario
                FROM CONTRATOS_MANDATOS cm
                JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
                JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
            """

            conditions = []
            params = []

            if estado and estado != "Todos":
                if estado == "Activo":
                    conditions.append("cm.ESTADO_CONTRATO_M = 'Activo'")
                elif estado == "Cancelado":
                    conditions.append("cm.ESTADO_CONTRATO_M != 'Activo'")
                else:
                    conditions.append(f"cm.ESTADO_CONTRATO_M = {placeholder}")
                    params.append(estado)

            if busqueda:
                conditions.append(
                    f"(p.DIRECCION_PROPIEDAD LIKE {placeholder} OR per.NOMBRE_COMPLETO LIKE {placeholder})"
                )
                params.extend([f"%{busqueda}%", f"%{busqueda}%"])

            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)

            base_query += " ORDER BY cm.ID_CONTRATO_M DESC"

            cursor.execute(base_query, params)
            return cursor.fetchall()

    def _listar_todos_arrendamientos(self, estado, busqueda):
        """Helper para exportación: Trae arriendos sin paginación."""
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()

            base_query = """
                SELECT 
                    ca.ID_CONTRATO_A as id,
                    ca.ESTADO_CONTRATO_A as estado,
                    ca.CANON_ARRENDAMIENTO as canon,
                    ca.FECHA_INICIO_CONTRATO_A as fecha_inicio,
                    ca.FECHA_FIN_CONTRATO_A as fecha_fin,
                    p.DIRECCION_PROPIEDAD as propiedad,
                    per.NOMBRE_COMPLETO as arrendatario,
                    per.NUMERO_DOCUMENTO as documento_arrendatario
                FROM CONTRATOS_ARRENDAMIENTOS ca
                JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
            """

            conditions = []
            params = []

            if estado and estado != "Todos":
                if estado == "Activo":
                    conditions.append("ca.ESTADO_CONTRATO_A = 'Activo'")
                elif estado == "Cancelado":
                    conditions.append("ca.ESTADO_CONTRATO_A != 'Activo'")
                else:
                    conditions.append(f"ca.ESTADO_CONTRATO_A = {placeholder}")
                    params.append(estado)

            if busqueda:
                conditions.append(
                    f"(p.DIRECCION_PROPIEDAD LIKE {placeholder} OR per.NOMBRE_COMPLETO LIKE {placeholder})"
                )
                params.extend([f"%{busqueda}%", f"%{busqueda}%"])

            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)

            base_query += " ORDER BY ca.ID_CONTRATO_A DESC"

            cursor.execute(base_query, params)
            return cursor.fetchall()

    def obtener_detalle_contrato_ui(self, id_contrato: int, tipo: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene detalles completos de un contrato para mostrar en la UI.

        Args:
            id_contrato: ID del contrato
            tipo: 'Mandato' o 'Arrendamiento'

        Returns:
            Diccionario con información completa del contrato o None si no existe
        """
        placeholder = self.db.get_placeholder()

        if tipo == "Mandato":
            query = f"""
            SELECT 
                cm.ID_CONTRATO_M,
                cm.FECHA_INICIO_CONTRATO_M,
                cm.FECHA_FIN_CONTRATO_M,
                cm.DURACION_CONTRATO_M,
                cm.CANON_MANDATO,
                cm.COMISION_PORCENTAJE_CONTRATO_M,
                cm.IVA_CONTRATO_M,
                cm.ESTADO_CONTRATO_M,
                cm.MOTIVO_CANCELACION,
                cm.ALERTA_VENCIMINETO_CONTRATO_M,
                cm.FECHA_RENOVACION_CONTRATO_M,
                cm.CREATED_AT,
                cm.CREATED_BY,
                p.MATRICULA_INMOBILIARIA,
                p.DIRECCION_PROPIEDAD,
                p.TIPO_PROPIEDAD,
                p.AREA_M2,
                per.NOMBRE_COMPLETO as PROPIETARIO,
                per.NUMERO_DOCUMENTO,
                per.TELEFONO_PRINCIPAL as TELEFONO,
                per.CORREO_ELECTRONICO as EMAIL,
                ases.NOMBRE_COMPLETO as ASESOR
            FROM CONTRATOS_MANDATOS cm
            JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
            JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
            JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
            LEFT JOIN ASESORES a ON cm.ID_ASESOR = a.ID_ASESOR
            LEFT JOIN PERSONAS ases ON a.ID_PERSONA = ases.ID_PERSONA
            WHERE cm.ID_CONTRATO_M = {placeholder}
            """

            with self.db.obtener_conexion() as conn:
                cursor = self.db.get_dict_cursor(conn)
                cursor.execute(query, (id_contrato,))
                row = cursor.fetchone()

                if not row:
                    return None

                return {
                    "tipo": "Mandato",
                    "id": row["ID_CONTRATO_M"],
                    "fecha_inicio": row["FECHA_INICIO_CONTRATO_M"],
                    "fecha_fin": row["FECHA_FIN_CONTRATO_M"],
                    "duracion": row["DURACION_CONTRATO_M"],
                    "canon": row["CANON_MANDATO"],
                    "comision_pct": row["COMISION_PORCENTAJE_CONTRATO_M"] / 100,
                    "iva_pct": row["IVA_CONTRATO_M"] / 100,
                    "estado": row["ESTADO_CONTRATO_M"],
                    "motivo_cancelacion": row["MOTIVO_CANCELACION"],
                    "alerta_vencimiento": row["ALERTA_VENCIMINETO_CONTRATO_M"],
                    "fecha_renovacion": row["FECHA_RENOVACION_CONTRATO_M"],
                    "created_at": row["CREATED_AT"],
                    "created_by": row["CREATED_BY"],
                    # Propiedad
                    "matricula": row["MATRICULA_INMOBILIARIA"],
                    "direccion": row["DIRECCION_PROPIEDAD"],
                    "tipo_propiedad": row["TIPO_PROPIEDAD"],
                    "area_m2": row["AREA_M2"],
                    # Propietario
                    "propietario": row["PROPIETARIO"],
                    "documento": row["NUMERO_DOCUMENTO"],
                    "telefono": row["TELEFONO"] or "N/A",
                    "email": row["EMAIL"] or "N/A",
                    "asesor": row["ASESOR"] or "N/A",
                }

        else:  # Arrendamiento
            query = f"""
            SELECT 
                ca.ID_CONTRATO_A,
                ca.FECHA_INICIO_CONTRATO_A,
                ca.FECHA_FIN_CONTRATO_A,
                ca.DURACION_CONTRATO_A,
                ca.CANON_ARRENDAMIENTO,
                ca.DEPOSITO,
                ca.ESTADO_CONTRATO_A,
                ca.MOTIVO_CANCELACION,
                ca.ALERTA_VENCIMIENTO_CONTRATO_A,
                ca.FECHA_RENOVACION_CONTRATO_A,
                ca.CREATED_AT,
                ca.CREATED_BY,
                p.MATRICULA_INMOBILIARIA,
                p.DIRECCION_PROPIEDAD,
                p.TIPO_PROPIEDAD,
                p.AREA_M2,
                per_arr.NOMBRE_COMPLETO as ARRENDATARIO,
                per_arr.NUMERO_DOCUMENTO as DOC_ARRENDATARIO,
                per_arr.TELEFONO_PRINCIPAL as TEL_ARRENDATARIO,
                per_arr.CORREO_ELECTRONICO as EMAIL_ARRENDATARIO,
                per_code.NOMBRE_COMPLETO as CODEUDOR,
                per_code.NUMERO_DOCUMENTO as DOC_CODEUDOR
            FROM CONTRATOS_ARRENDAMIENTOS ca
            JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
            JOIN PERSONAS per_arr ON arr.ID_PERSONA = per_arr.ID_PERSONA
            LEFT JOIN CODEUDORES code ON ca.ID_CODEUDOR = code.ID_CODEUDOR
            LEFT JOIN PERSONAS per_code ON code.ID_PERSONA = per_code.ID_PERSONA
            WHERE ca.ID_CONTRATO_A = {placeholder}
            """

            with self.db.obtener_conexion() as conn:
                cursor = self.db.get_dict_cursor(conn)
                cursor.execute(query, (id_contrato,))
                row = cursor.fetchone()

                if not row:
                    return None

                return {
                    "tipo": "Arrendamiento",
                    "id": row["ID_CONTRATO_A"],
                    "fecha_inicio": row["FECHA_INICIO_CONTRATO_A"],
                    "fecha_fin": row["FECHA_FIN_CONTRATO_A"],
                    "duracion": row["DURACION_CONTRATO_A"],
                    "canon": row["CANON_ARRENDAMIENTO"],
                    "deposito": row["DEPOSITO"],
                    "estado": row["ESTADO_CONTRATO_A"],
                    "motivo_cancelacion": row["MOTIVO_CANCELACION"],
                    "alerta_vencimiento": row["ALERTA_VENCIMIENTO_CONTRATO_A"],
                    "fecha_renovacion": row["FECHA_RENOVACION_CONTRATO_A"],
                    "created_at": row["CREATED_AT"],
                    "created_by": row["CREATED_BY"],
                    # Propiedad
                    "matricula": row["MATRICULA_INMOBILIARIA"],
                    "direccion": row["DIRECCION_PROPIEDAD"],
                    "tipo_propiedad": row["TIPO_PROPIEDAD"],
                    "area_m2": row["AREA_M2"],
                    # Arrendatario
                    "arrendatario": row["ARRENDATARIO"],
                    "documento": row["DOC_ARRENDATARIO"],
                    "telefono": row["TEL_ARRENDATARIO"] or "N/A",
                    "email": row["EMAIL_ARRENDATARIO"] or "N/A",
                    # Codeudor
                    "codeudor": row["CODEUDOR"] or "N/A",
                    "documento_codeudor": row["DOC_CODEUDOR"] or "N/A",
                }

    def listar_arrendamientos_por_vencimiento(
        self, fecha_inicio: str, fecha_fin: str
    ) -> List[Dict[str, Any]]:
        """
        Lista arrendamientos ACTIVOS que vencen en el rango de fechas.
        Incluye proyección de incremento IPC.
        """
        # 1. Obtener IPC actual para proyección
        ipc = self.repo_ipc.obtener_ultimo()
        porcentaje_ipc = float(ipc.valor_ipc) if ipc else 0.0

        placeholder = self.db.get_placeholder()
        query = f"""
        SELECT 
            ca.ID_CONTRATO_A,
            ca.CANON_ARRENDAMIENTO,
            ca.FECHA_FIN_CONTRATO_A,
            p.DIRECCION_PROPIEDAD,
            per.NOMBRE_COMPLETO as ARRENDATARIO
        FROM CONTRATOS_ARRENDAMIENTOS ca
        JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
        JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
        WHERE ca.ESTADO_CONTRATO_A = 'Activo'
          AND ca.FECHA_FIN_CONTRATO_A BETWEEN {placeholder} AND {placeholder}
        ORDER BY ca.FECHA_FIN_CONTRATO_A ASC
        """

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query, (fecha_inicio, fecha_fin))

            resultados = []
            for row in cursor.fetchall():
                canon_actual = row["canon_arrendamiento"]
                incremento = int(canon_actual * (porcentaje_ipc / 100))
                nuevo_canon = canon_actual + incremento

                resultados.append(
                    {
                        "id": row["id_contrato_a"],
                        "propiedad": row["direccion_propiedad"],
                        "arrendatario": row["arrendatario"],
                        "fecha_vencimiento": row["fecha_fin_contrato_a"],
                        "canon_actual": canon_actual,
                        "ipc_porcentaje": porcentaje_ipc,
                        "canon_proyectado": nuevo_canon,
                        "incremento_valor": incremento,
                    }
                )

            return resultados

    def listar_arrendamientos_activos(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de arrendamientos ACTIVOS para dropdowns.
        """
        query = """
        SELECT 
            ca.ID_CONTRATO_A,
            p.DIRECCION_PROPIEDAD,
            per.NOMBRE_COMPLETO as ARRENDATARIO,
            ca.CANON_ARRENDAMIENTO
        FROM CONTRATOS_ARRENDAMIENTOS ca
        JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
        JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
        WHERE ca.ESTADO_CONTRATO_A = 'Activo'
        ORDER BY p.DIRECCION_PROPIEDAD
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query)
            return [
                {
                    "id": row["id_contrato_a"],
                    "texto": f"{row['direccion_propiedad']} - {row['arrendatario']} (${row['canon_arrendamiento']:,})",  # Direccion - Arrendatario (Canon)
                    "canon": row["canon_arrendamiento"],
                }
                for row in cursor.fetchall()
            ]

    def listar_arrendamientos_por_asesor(self, id_asesor: int) -> List[Dict[str, Any]]:
        """
        Retorna lista de arrendamientos ACTIVOS asociados a un asesor específico.

        El asesor se identifica por ID_ASESOR.

        Args:
            id_asesor: ID del asesor (tabla ASESORES)

        Returns:
            Lista de diccionarios con información de cada contrato activo
        """
        placeholder = self.db.get_placeholder()
        query = f"""
        SELECT DISTINCT
            ca.ID_CONTRATO_A,
            ca.CANON_ARRENDAMIENTO,
            p.DIRECCION_PROPIEDAD,
            p.MATRICULA_INMOBILIARIA,
            per_arr.NOMBRE_COMPLETO as ARRENDATARIO,
            ca.FECHA_INICIO_CONTRATO_A,
            ca.FECHA_FIN_CONTRATO_A
        FROM CONTRATOS_ARRENDAMIENTOS ca
        JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN CONTRATOS_MANDATOS cm ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD
        JOIN ASESORES a ON cm.ID_ASESOR = a.ID_ASESOR
        JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
        JOIN PERSONAS per_arr ON arr.ID_PERSONA = per_arr.ID_PERSONA
        WHERE a.ID_ASESOR = {placeholder}
          AND ca.ESTADO_CONTRATO_A = 'Activo'
          AND cm.ESTADO_CONTRATO_M = 'Activo'
        ORDER BY p.DIRECCION_PROPIEDAD
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query, (id_asesor,))
            return [
                {
                    "id": row["id_contrato_a"],
                    "canon": row["canon_arrendamiento"],
                    "propiedad": row["direccion_propiedad"],
                    "matricula": row["matricula_inmobiliaria"],
                    "arrendatario": row["arrendatario"],
                    "fecha_inicio": row["fecha_inicio_contrato_a"],
                    "fecha_fin": row["fecha_fin_contrato_a"],
                    "texto": f"Contrato #{row['id_contrato_a']} - {row['direccion_propiedad']} - Canon: ${row['canon_arrendamiento']:,}",
                }
                for row in cursor.fetchall()
            ]

    # =========================================================================
    # ALERTAS Y VENCIMIENTOS
    # =========================================================================

    def verificar_vencimientos(self, usuario_sistema: str = "sistema"):
        """
        Verifica contratos por vencer y genera alertas (90, 60, 30, 0 días).
        Se recomienda ejecutar este método diariamente (Job).
        """
        dias_alerta = [90, 60, 30, 0]

        with self.repo_mandato.db.obtener_conexion() as conn:
            cursor = conn.cursor()

            # 1. Verificar Mandatos
            for dias in dias_alerta:
                # Query para encontrar contratos que vencen en 'dias' exactos
                # (date('now', '+90 days') == fecha_fin)
                query = f"""
                SELECT ID_CONTRATO_M, FECHA_FIN_CONTRATO_M 
                FROM CONTRATOS_MANDATOS 
                WHERE ESTADO_CONTRATO_M = 'Activo'
                  AND date(FECHA_FIN_CONTRATO_M) = date('now', '+{dias} days')
                """
                cursor.execute(query)
                mandatos = cursor.fetchall()

                for m in mandatos:
                    self._crear_alerta(
                        conn,
                        tipo="Vencimiento Contrato Mandato",
                        descripcion=f"El contrato de mandato {m[0]} vence en {dias} días (Fecha: {m[1]}).",
                        id_entidad=m[0],
                        tipo_entidad="CONTRATO_MANDATO",
                        usuario=usuario_sistema,
                    )

            # 2. Verificar Arrendamientos (Vencimiento)
            for dias in dias_alerta:
                query = f"""
                SELECT ID_CONTRATO_A, FECHA_FIN_CONTRATO_A 
                FROM CONTRATOS_ARRENDAMIENTOS 
                WHERE ESTADO_CONTRATO_A = 'Activo'
                  AND date(FECHA_FIN_CONTRATO_A) = date('now', '+{dias} days')
                """
                cursor.execute(query)
                arriendos = cursor.fetchall()

                for a in arriendos:
                    self._crear_alerta(
                        conn,
                        tipo="Vencimiento Contrato Arrendamiento",
                        descripcion=f"El contrato de arrendamiento {a[0]} vence en {dias} días (Fecha: {a[1]}).",
                        id_entidad=a[0],
                        tipo_entidad="CONTRATO_ARRENDAMIENTO",
                        usuario=usuario_sistema,
                    )

            # 3. Verificar IPC Aniversario (60 días antes)
            # Buscamos contratos donde (Hoy + 60) coincida con MM-DD de Fecha Inicio
            # Y que NO sea el año de vencimiento final (ya cubierto por vencimiento)
            query_ipc = """
            SELECT ID_CONTRATO_A, FECHA_INICIO_CONTRATO_A
            FROM CONTRATOS_ARRENDAMIENTOS
            WHERE ESTADO_CONTRATO_A = 'Activo'
            AND strftime('%m-%d', date('now', '+60 days')) = strftime('%m-%d', FECHA_INICIO_CONTRATO_A)
            AND date(FECHA_FIN_CONTRATO_A) > date('now', '+60 days') -- Que no sea el fin del contrato
            """
            cursor.execute(query_ipc)
            arriendos_ipc = cursor.fetchall()

            for a in arriendos_ipc:
                # Calcular qué aniversario es
                datetime.strptime(a[1], "%Y-%m-%d")
                datetime.now()  # Aprox, para el mensaje
                # Aniversario numero?
                # Si hoy es 2024, inicia 2023 -> 1er aniversario.
                # Mensaje genérico es seguro.
                self._crear_alerta(
                    conn,
                    tipo="Incremento IPC Anual",
                    descripcion=f"Próximo aniversario de contrato {a[0]} en 60 días. Preparar incremento de IPC.",
                    id_entidad=a[0],
                    tipo_entidad="CONTRATO_ARRENDAMIENTO",
                    usuario=usuario_sistema,
                )

            conn.commit()

    def _crear_alerta(self, conn, tipo, descripcion, id_entidad, tipo_entidad, usuario):
        """Helper para insertar alerta evitando duplicados pendientes."""
        # Verificar si ya existe alerta pendiente del mismo tipo para la entidad hoy
        check_query = """
        SELECT ID_ALERTAS FROM ALERTAS 
        WHERE TIPO_ALERTA = ? AND ID_ENTIDAD_RELACIONADA = ? 
          AND TIPO_ENTIDAD = ? AND ESTADO_ALERTA = 'Pendiente'
          AND date(FECHA_GENERACION_ALERTA) = date('now')
        """
        cursor = conn.cursor()
        cursor.execute(check_query, (tipo, id_entidad, tipo_entidad))
        if cursor.fetchone():
            return  # Ya existe alerta hoy

        insert_query = """
        INSERT INTO ALERTAS (
            TIPO_ALERTA, DESCRIPCION_ALERTA, PRIORIDAD, 
            ID_ENTIDAD_RELACIONADA, TIPO_ENTIDAD, CREATED_BY
        ) VALUES (?, ?, 'Alta', ?, ?, ?)
        """
        cursor.execute(insert_query, (tipo, descripcion, id_entidad, tipo_entidad, usuario))

    def obtener_detalle_mandato_ui(self, id_contrato: int) -> Optional[Dict[str, Any]]:
        """
        Retorna un diccionario con TODOS los detalles legibles del mandato
        (Dirección, Nombres, etc.) para visualización en UI.
        """
        placeholder = self.db.get_placeholder()
        query = f"""
        SELECT 
            CONTRATOS_MANDATOS.ID_CONTRATO_M,
            PROPIEDADES.ID_PROPIEDAD,
            PROPIEDADES.DIRECCION_PROPIEDAD, 
            PROPIEDADES.MATRICULA_INMOBILIARIA,
            CONTRATOS_MANDATOS.ID_PROPIETARIO,
            per_prop.NOMBRE_COMPLETO as NOMBRE_PROPIETARIO,
            CONTRATOS_MANDATOS.ID_ASESOR,
            per_ases.NOMBRE_COMPLETO as NOMBRE_ASESOR,
            CONTRATOS_MANDATOS.FECHA_INICIO_CONTRATO_M,
            CONTRATOS_MANDATOS.FECHA_FIN_CONTRATO_M,
            CONTRATOS_MANDATOS.DURACION_CONTRATO_M,
            CONTRATOS_MANDATOS.CANON_MANDATO,
            CONTRATOS_MANDATOS.COMISION_PORCENTAJE_CONTRATO_M,
            CONTRATOS_MANDATOS.ESTADO_CONTRATO_M,
            CONTRATOS_MANDATOS.CREATED_AT,
            CONTRATOS_MANDATOS.CREATED_BY
        FROM CONTRATOS_MANDATOS
        JOIN PROPIEDADES ON CONTRATOS_MANDATOS.ID_PROPIEDAD = PROPIEDADES.ID_PROPIEDAD
        JOIN PROPIETARIOS ON CONTRATOS_MANDATOS.ID_PROPIETARIO = PROPIETARIOS.ID_PROPIETARIO
        JOIN PERSONAS per_prop ON PROPIETARIOS.ID_PERSONA = per_prop.ID_PERSONA
        JOIN ASESORES ON CONTRATOS_MANDATOS.ID_ASESOR = ASESORES.ID_ASESOR
        JOIN PERSONAS per_ases ON ASESORES.ID_PERSONA = per_ases.ID_PERSONA
        WHERE CONTRATOS_MANDATOS.ID_CONTRATO_M = {placeholder}
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query, (id_contrato,))
            row = cursor.fetchone()
            if row:
                return {
                    "id_contrato": row["id_contrato_m"],
                    "id_propiedad": row["id_propiedad"],
                    "direccion_propiedad": row["direccion_propiedad"],
                    "matricula": row["matricula_inmobiliaria"],
                    "id_propietario": row["id_propietario"],
                    "nombre_propietario": row["nombre_propietario"],
                    "id_asesor": row["id_asesor"],
                    "nombre_asesor": row["nombre_asesor"],
                    "fecha_inicio": row["fecha_inicio_contrato_m"],
                    "fecha_fin": row["fecha_fin_contrato_m"],
                    "duracion": row["duracion_contrato_m"],
                    "canon": row["canon_mandato"],
                    "comision": row["comision_porcentaje_contrato_m"],
                    "estado": row["estado_contrato_m"],
                    "created_at": row["created_at"],
                    "created_by": row["created_by"],
                }
            return None

    def obtener_detalle_arriendo_ui(self, id_contrato: int) -> Optional[Dict[str, Any]]:
        """
        Retorna un diccionario con TODOS los detalles legibles del arriendo
        (Dirección, Nombres, etc.) para visualización en UI.
        """
        placeholder = self.db.get_placeholder()
        query = f"""
        SELECT 
            a.ID_CONTRATO_A,
            p.ID_PROPIEDAD,
            p.DIRECCION_PROPIEDAD,
            p.MATRICULA_INMOBILIARIA,
            a.ID_ARRENDATARIO,
            per_arr.NOMBRE_COMPLETO as NOMBRE_INQUILINO,
            a.ID_CODEUDOR,
            COALESCE(per_cod.NOMBRE_COMPLETO, 'N/A') as NOMBRE_CODEUDOR,
            a.FECHA_INICIO_CONTRATO_A,
            a.FECHA_FIN_CONTRATO_A,
            a.CANON_ARRENDAMIENTO,
            a.DEPOSITO,
            a.ESTADO_CONTRATO_A,
            a.CREATED_AT
        FROM CONTRATOS_ARRENDAMIENTOS a
        JOIN PROPIEDADES p ON a.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN ARRENDATARIOS rr ON a.ID_ARRENDATARIO = rr.ID_ARRENDATARIO
        JOIN PERSONAS per_arr ON rr.ID_PERSONA = per_arr.ID_PERSONA
        LEFT JOIN CODEUDORES rc ON a.ID_CODEUDOR = rc.ID_CODEUDOR
        LEFT JOIN PERSONAS per_cod ON rc.ID_PERSONA = per_cod.ID_PERSONA
        WHERE a.ID_CONTRATO_A = {placeholder}
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query, (id_contrato,))
            row = cursor.fetchone()
            if row:
                return {
                    "id_contrato": row["id_contrato_a"],
                    "id_propiedad": row["id_propiedad"],
                    "direccion_propiedad": row["direccion_propiedad"],
                    "matricula": row["matricula_inmobiliaria"],
                    "id_inquilino": row["id_arrendatario"],
                    "nombre_inquilino": row["nombre_inquilino"],
                    "id_codeudor": row["id_codeudor"],
                    "nombre_codeudor": row["nombre_codeudor"],
                    "fecha_inicio": row["fecha_inicio_contrato_a"],
                    "fecha_fin": row["fecha_fin_contrato_a"],
                    "canon": row["canon_arrendamiento"],
                    "deposito": row["deposito"],
                    "estado": row["estado_contrato_a"],
                    "created_at": row["created_at"],
                }
            return None

    def aplicar_incremento_ipc(
        self,
        id_contrato: int,
        porcentaje_ipc: float,
        fecha_aplicacion: str,
        observaciones: str = "",
        usuario: str = "admin",
    ) -> Dict[str, Any]:
        """
        Aplica incremento IPC a contrato de arrendamiento activo.
        También actualiza en cascada la Propiedad y el Contrato de Mandato.

        Args:
            id_contrato: ID del contrato de arrendamiento
            porcentaje_ipc: Porcentaje de incremento (ej: 5.62 para 5.62%)
            fecha_aplicacion: Fecha de aplicación (YYYY-MM-D)
            observaciones: Notas adicionales
            usuario: Usuario que ejecuta la acción

        Returns:
            Dict con resultado de la operación
        """
        try:
            # FIX "NUCLEAR": AUTOCOMMIT = TRUE con ROLLBACK MANUAL
            # La única forma verificada de persistir cambios en este entorno es con autocommit=True.
            # Para mantener la atomicidad, implementamos "Undo" manual en caso de error.
            conn = self.db.obtener_conexion()
            real_conn = conn
            if hasattr(conn, "_conn"):
                real_conn = conn._conn

            real_conn.autocommit = True
            cursor = real_conn.cursor()

            try:
                placeholder = "%s"

                # 1. Validar contrato existe y está activo
                cursor.execute(
                    """
                    SELECT ID_CONTRATO_A, CANON_ARRENDAMIENTO, ESTADO_CONTRATO_A,
                           FECHA_ULTIMO_INCREMENTO_IPC, ID_PROPIEDAD
                    FROM CONTRATOS_ARRENDAMIENTOS
                    WHERE ID_CONTRATO_A = %s
                """,
                    (id_contrato,),
                )

                row = cursor.fetchone()
                if not row:
                    return {"success": False, "message": f"Contrato {id_contrato} no encontrado"}

                estado = row[2]
                if estado != "Activo":
                    return {
                        "success": False,
                        "message": "Solo se puede aplicar IPC a contratos activos",
                    }

                id_propiedad = row[4]
                ultimo_incremento = row[3]
                canon_actual = row[1]

                # 2. Validar no hay incremento reciente
                if ultimo_incremento:
                    from datetime import datetime

                    try:
                        ultima_fecha = (
                            ultimo_incremento
                            if isinstance(ultimo_incremento, (datetime, list))
                            else datetime.strptime(str(ultimo_incremento), "%Y-%m-%d")
                        )
                        if isinstance(ultima_fecha, str):
                            ultima_fecha = datetime.strptime(ultima_fecha, "%Y-%m-%d")

                        nueva_fecha = datetime.strptime(fecha_aplicacion, "%Y-%m-%d")

                        if (
                            ultima_fecha.year == nueva_fecha.year
                            and ultima_fecha.month == nueva_fecha.month
                        ):
                            return {
                                "success": False,
                                "message": f"Ya se aplicó incremento en {ultima_fecha.strftime('%Y-%m')}",
                            }
                    except Exception:
                        pass

                # 3. Porcentaje check
                if porcentaje_ipc <= 0 or porcentaje_ipc > 20:
                    return {"success": False, "message": "Porcentaje invalido"}

                # 4. Calculo
                canon_anterior = int(canon_actual) if canon_actual else 0
                incremento = canon_anterior * (porcentaje_ipc / 100)
                canon_nuevo = round(canon_anterior + incremento)

                # 5. EXECUTE UPDATES
                # (No hay bloque de transacción, operaciones inmediatas por autocommit=True)

                # 5a. Contrato
                cursor.execute(
                    """
                    UPDATE CONTRATOS_ARRENDAMIENTOS
                    SET CANON_ARRENDAMIENTO = %s,
                        FECHA_ULTIMO_INCREMENTO_IPC = %s,
                        ALERTA_IPC = FALSE,
                        UPDATED_AT = CURRENT_TIMESTAMP,
                        UPDATED_BY = %s
                    WHERE ID_CONTRATO_A = %s
                """,
                    (canon_nuevo, fecha_aplicacion, usuario, id_contrato),
                )

                # 5b. Propiedad
                cursor.execute(
                    """
                    UPDATE PROPIEDADES
                    SET CANON_ARRENDAMIENTO_ESTIMADO = %s,
                        UPDATED_AT = CURRENT_TIMESTAMP,
                        UPDATED_BY = %s
                    WHERE ID_PROPIEDAD = %s
                """,
                    (canon_nuevo, usuario, id_propiedad),
                )

                # 5c. Mandato
                cursor.execute(
                    """
                    UPDATE CONTRATOS_MANDATOS
                    SET CANON_MANDATO = %s,
                        UPDATED_AT = CURRENT_TIMESTAMP,
                        UPDATED_BY = %s
                    WHERE ID_PROPIEDAD = %s
                    AND ESTADO_CONTRATO_M = 'Activo'
                """,
                    (canon_nuevo, usuario, id_propiedad),
                )

                # 6. Registar Historial
                try:
                    cursor.execute(
                        """
                        INSERT INTO IPC_INCREMENT_HISTORY (
                            ID_CONTRATO_A, FECHA_APLICACION, PORCENTAJE_IPC,
                            CANON_ANTERIOR, CANON_NUEVO, OBSERVACIONES, CREATED_BY
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                        (
                            id_contrato,
                            fecha_aplicacion,
                            porcentaje_ipc,
                            canon_anterior,
                            canon_nuevo,
                            observaciones,
                            usuario,
                        ),
                    )
                except Exception:
                    pass

                cursor.close()
                # Confirmación implicita por autocommit=True

                return {
                    "success": True,
                    "message": f"IPC aplicado correctamente. Canon: ${canon_anterior:,} → ${canon_nuevo:,}",
                    "canon_anterior": canon_anterior,
                    "canon_nuevo": canon_nuevo,
                    "porcentaje_aplicado": porcentaje_ipc,
                }

            except Exception as e:
                # MANUAL ROLLBACK (Compensating Transaction)
                # Restaurar valores anteriores si falla algo a mitad de camino para mantener consistencia
                try:
                    pass  # print(f"ERROR IPC: {str(e)} - Iniciando rollback manual...") [OpSec Removed]
                    # Restaurar Contrato
                    cursor.execute(
                        """
                        UPDATE CONTRATOS_ARRENDAMIENTOS 
                        SET CANON_ARRENDAMIENTO=%s, FECHA_ULTIMO_INCREMENTO_IPC=%s 
                        WHERE ID_CONTRATO_A=%s
                    """,
                        (canon_anterior, ultimo_incremento, id_contrato),
                    )

                    # Restaurar Propiedad
                    cursor.execute(
                        """
                        UPDATE PROPIEDADES SET CANON_ARRENDAMIENTO_ESTIMADO=%s WHERE ID_PROPIEDAD=%s
                    """,
                        (canon_anterior, id_propiedad),
                    )

                    # Restaurar Mandato
                    cursor.execute(
                        """
                        UPDATE CONTRATOS_MANDATOS SET CANON_MANDATO=%s 
                        WHERE ID_PROPIEDAD=%s AND ESTADO_CONTRATO_M='Activo'
                    """,
                        (canon_anterior, id_propiedad),
                    )
                    pass  # print("Rollback manual completado.") [OpSec Removed]
                except Exception:
                    pass  # print(f"FALLO FATAL ROLLBACK: {str(e_roll)}") [OpSec Removed]

                raise e
            finally:
                # CRITICO: Restaurar autocommit a False para no afectar otras operaciones
                # Y NO cerrar la conexión porque es compartida (Singleton/Pool)
                if "real_conn" in locals() and real_conn:
                    real_conn.autocommit = False

                # if 'conn' in locals():
                #     conn.close()  <-- NO CERRAR, es gestionada por DatabaseManager
                pass

        except Exception as e:
            import traceback

            traceback.print_exc()
            return {"success": False, "message": f"Error al aplicar IPC: {str(e)}"}

        except Exception as e:
            import traceback

            traceback.print_exc()
            return {"success": False, "message": f"Error al aplicar IPC: {str(e)}"}
