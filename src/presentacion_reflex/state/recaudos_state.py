from datetime import datetime
from typing import Any, Dict, List, Optional

import reflex as rx

from src.dominio.entidades.recaudo import Recaudo
from src.dominio.entidades.recaudo_concepto import RecaudoConcepto
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_recaudo_sqlite import RepositorioRecaudoSQLite
from src.presentacion_reflex.state.documentos_mixin import DocumentosStateMixin
from src.presentacion_reflex.utils.formatters import format_currency, format_number


class RecaudosState(DocumentosStateMixin):
    """Estado para gestión de recaudos (pagos de arrendatarios).
    Maneja paginación, filtros, CRUD y validaciones.
    """

    # Paginación
    current_page: int = 1
    page_size: int = 25
    total_items: int = 0

    # Datos
    recaudos: List[Dict[str, Any]] = []
    recaudo_actual: Optional[Dict[str, Any]] = None
    is_loading: bool = False
    error_message: str = ""

    # Filtros
    search_text: str = ""
    filter_estado: str = "Todos"
    filter_contrato: str = ""
    filter_fecha_desde: str = ""
    filter_fecha_hasta: str = ""

    # Opciones de filtros
    estado_options: List[str] = ["Todos", "Pendiente", "Aplicado", "Reversado"]
    contratos_options: List[Dict[str, Any]] = []
    contratos_select_options: List[str] = []

    # Modales
    show_form_modal: bool = False
    show_detail_modal: bool = False

    # Form data
    form_data: Dict[str, Any] = {}

    @rx.event(background=True)
    async def on_load(self):
        """Carga inicial al montar la página."""
        async with self:
            self.is_loading = True

        try:
            # Cargar contratos activos para filtros
            yield RecaudosState.load_filter_options()
            # Cargar recaudos
            yield RecaudosState.load_recaudos()
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def load_filter_options(self):
        """Carga contratos activos para dropdown de filtros."""
        query = """
        SELECT 
            ca.ID_CONTRATO_A,
            p.DIRECCION_PROPIEDAD,
            per.NOMBRE_COMPLETO,
            ca.CANON_ARRENDAMIENTO
        FROM CONTRATOS_ARRENDAMIENTOS ca
        INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
        INNER JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
        INNER JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
        WHERE ca.ESTADO_CONTRATO_A = 'Activo'
        ORDER BY p.DIRECCION_PROPIEDAD
        """

        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            cursor.execute(query)
            rows = cursor.fetchall()

            contratos = [
                {
                    "id": str(row["ID_CONTRATO_A"]),
                    "texto": f"ID:{row['ID_CONTRATO_A']} - {row['DIRECCION_PROPIEDAD']} ({row['NOMBRE_COMPLETO']})",
                    "canon": row["CANON_ARRENDAMIENTO"],
                }
                for row in rows
            ]
            contratos_select = [c["texto"] for c in contratos]

        async with self:
            self.contratos_options = contratos
            self.contratos_select_options = contratos_select

    @rx.event(background=True)
    async def load_recaudos(self):
        """Carga recaudos con filtros y paginación."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            placeholder = db_manager.get_placeholder()

            # Construir query con filtros
            query = """
            SELECT 
                r.ID_RECAUDO,
                r.ID_CONTRATO_A,
                r.FECHA_PAGO,
                r.VALOR_TOTAL,
                r.METODO_PAGO,
                r.REFERENCIA_BANCARIA,
                r.ESTADO_RECAUDO,
                r.OBSERVACIONES,
                p.DIRECCION_PROPIEDAD,
                p.MATRICULA_INMOBILIARIA,
                per.NOMBRE_COMPLETO as NOMBRE_ARRENDATARIO
            FROM RECAUDOS r
            INNER JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
            INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            INNER JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
            INNER JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
            WHERE 1=1
            """

            params = []

            # Aplicar filtros
            if self.filter_estado and self.filter_estado != "Todos":
                query += f" AND r.ESTADO_RECAUDO = {placeholder}"
                params.append(self.filter_estado)

            if self.filter_fecha_desde:
                query += f" AND r.FECHA_PAGO >= {placeholder}"
                params.append(self.filter_fecha_desde)

            if self.filter_fecha_hasta:
                query += f" AND r.FECHA_PAGO <= {placeholder}"
                params.append(self.filter_fecha_hasta)

            if self.search_text:
                query += f""" AND (
                    p.MATRICULA_INMOBILIARIA LIKE {placeholder} OR
                    p.DIRECCION_PROPIEDAD LIKE {placeholder} OR
                    per.NOMBRE_COMPLETO LIKE {placeholder} OR
                    ca.ID_CONTRATO_A::TEXT LIKE {placeholder}
                )"""
                search_pattern = f"%{self.search_text}%"
                params.extend([search_pattern] * 4)

            # Ordenar por fecha desc
            query += " ORDER BY r.FECHA_PAGO DESC"

            # Contar total (sin paginación)
            count_query = f"SELECT COUNT(*) as total FROM ({query}) as subq"

            # Aplicar paginación
            offset = (self.current_page - 1) * self.page_size
            query += f" LIMIT {placeholder} OFFSET {placeholder}"
            params.extend([self.page_size, offset])

            with db_manager.obtener_conexion() as conn:
                cursor = db_manager.get_dict_cursor(conn)

                # Obtener total
                cursor.execute(count_query, params[:-2])  # Sin LIMIT/OFFSET
                total_row = cursor.fetchone()
                total = (
                    (
                        total_row.get("total")
                        or total_row.get("TOTAL")
                        or total_row.get("count")
                        or 0
                    )
                    if total_row
                    else 0
                )

                # Obtener datos paginados
                cursor.execute(query, params)
                rows = cursor.fetchall()

                recaudos_list = [
                    {
                        "id_recaudo": row["ID_RECAUDO"],
                        "id_contrato": row["ID_CONTRATO_A"],
                        "codigo_contrato": f"ID:{row['ID_CONTRATO_A']}",
                        "direccion": row["DIRECCION_PROPIEDAD"],
                        "matricula": row["MATRICULA_INMOBILIARIA"],
                        "arrendatario": row["NOMBRE_ARRENDATARIO"],
                        "fecha_pago": row["FECHA_PAGO"],
                        "valor_total": row["VALOR_TOTAL"],
                        "metodo_pago": row["METODO_PAGO"],
                        "referencia": row["REFERENCIA_BANCARIA"] or "",
                        "estado": row["ESTADO_RECAUDO"],
                        "observaciones": row["OBSERVACIONES"] or "",
                    }
                    for row in rows
                ]

            async with self:
                # Aplicar formateo a los items de la lista
                formatted_list = []
                for row in recaudos_list:
                    new_item = row.copy()
                    new_item["valor_total_view"] = format_currency(row.get("valor_total", 0))
                    formatted_list.append(new_item)
                
                self.recaudos = formatted_list
                self.total_items = total
                self.is_loading = False

        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar recaudos: {str(e)}"
                self.recaudos = []
                self.total_items = 0
                self.is_loading = False

    # Paginación
    def next_page(self):
        """Avanza a la siguiente página."""
        if self.current_page * self.page_size < self.total_items:
            self.current_page += 1
            return RecaudosState.load_recaudos

    def prev_page(self):
        """Retrocede a la página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            return RecaudosState.load_recaudos

    def set_page_size(self, size: str):
        """Cambia el tamaño de página."""
        self.page_size = int(size)
        self.current_page = 1
        return RecaudosState.load_recaudos

    # Búsqueda y Filtros
    def set_search(self, value: str):
        """Actualiza búsqueda."""
        self.search_text = value

    def search_recaudos(self):
        """Ejecuta búsqueda."""
        self.current_page = 1
        return RecaudosState.load_recaudos

    def handle_search_key_down(self, key: str):
        """Maneja Enter en búsqueda."""
        if key == "Enter":
            return self.search_recaudos()

    def set_filter_estado(self, value: str):
        """Cambia filtro de estado."""
        self.filter_estado = value
        self.current_page = 1
        return RecaudosState.load_recaudos

    def set_filter_fecha_desde(self, value: str):
        """Cambia filtro de fecha desde."""
        self.filter_fecha_desde = value
        self.current_page = 1
        return RecaudosState.load_recaudos

    def set_filter_fecha_hasta(self, value: str):
        """Cambia filtro de fecha hasta."""
        self.filter_fecha_hasta = value
        self.current_page = 1
        return RecaudosState.load_recaudos

    # Modal CRUD
    def open_create_modal(self):
        """Abre modal para crear nuevo recaudo."""
        self.show_form_modal = True
        self.show_detail_modal = False
        self.form_data = {
            "id_contrato_a": "",
            "fecha_pago": datetime.now().date().isoformat(),
            "valor_total": "",
            "metodo_pago": "Transferencia",
            "referencia_bancaria": "",
            "observaciones": "",
            # Conceptos - simplificado
            "tipo_concepto": "Canon",
            "periodo": datetime.now().strftime("%Y-%m"),
        }

        self.error_message = ""

    def set_form_field(self, field: str, value: str):
        """Actualiza un campo del formulario manual."""
        self.form_data[field] = value

    def on_contract_change(self, value: str):
        """Maneja el cambio de contrato seleccionado."""
        # Buscar el contrato seleccionado
        contrato = next((c for c in self.contratos_options if c["texto"] == value), None)

        if contrato:
            self.form_data["id_contrato_a"] = value  # El select usa el texto como valor
            # Auto-llenar valor con el canon
            if "canon" in contrato and contrato["canon"]:
                self.form_data["valor_total"] = str(contrato["canon"])
        else:
            self.form_data["id_contrato_a"] = value

    @rx.event(background=True)
    async def open_edit_modal(self, id_recaudo: int):
        """Abre modal para editar recaudo existente."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            repo = RepositorioRecaudoSQLite(db_manager)
            recaudo = repo.obtener_por_id(id_recaudo)

            if not recaudo:
                async with self:
                    self.error_message = "Recaudo no encontrado"
                    self.is_loading = False
                return

            # Solo permitir editar pendientes
            if recaudo.estado_recaudo != "Pendiente":
                async with self:
                    self.error_message = "Solo se pueden editar recaudos en estado 'Pendiente'"
                    self.is_loading = False
                return

            async with self:
                self.form_data = {
                    "id_recaudo": id_recaudo,
                    "id_contrato_a": recaudo.id_contrato_a,
                    "fecha_pago": recaudo.fecha_pago,
                    "valor_total": recaudo.valor_total,
                    "metodo_pago": recaudo.metodo_pago,
                    "referencia_bancaria": recaudo.referencia_bancaria or "",
                    "observaciones": recaudo.observaciones or "",
                }
                self.show_form_modal = True
                self.show_detail_modal = False
                self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar recaudo: {str(e)}"
                self.is_loading = False

    def close_modal(self):
        """Cierra todos los modales."""
        self.show_form_modal = False
        self.show_detail_modal = False
        self.recaudo_actual = None
        self.form_data = {}
        self.error_message = ""

    @rx.event(background=True)
    async def open_detail_modal(self, id_recaudo: int):
        """Abre modal de detalle para un recaudo."""
        async with self:
            self.is_loading = True
            self.error_message = ""

            # Contexto Documental
            self.current_entidad_tipo = "RECAUDO"
            self.current_entidad_id = str(id_recaudo)
            self.cargar_documentos()

        try:
            repo = RepositorioRecaudoSQLite(db_manager)
            recaudo = repo.obtener_por_id(id_recaudo)
            conceptos = repo.obtener_conceptos_por_recaudo(id_recaudo)

            if not recaudo:
                async with self:
                    self.error_message = "Recaudo no encontrado"
                    self.is_loading = False
                return

            # Buscar info adicional del contrato
            placeholder = db_manager.get_placeholder()
            query = f"""
                SELECT 
                    p.DIRECCION_PROPIEDAD,
                    p.MATRICULA_INMOBILIARIA,
                    per.NOMBRE_COMPLETO as ARRENDATARIO
                FROM CONTRATOS_ARRENDAMIENTOS ca
                INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                INNER JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                INNER JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
                WHERE ca.ID_CONTRATO_A = {placeholder}
            """
            with db_manager.obtener_conexion() as conn:
                cursor = db_manager.get_dict_cursor(conn)
                cursor.execute(query, (recaudo.id_contrato_a,))
                row = cursor.fetchone()
                direccion = row["DIRECCION_PROPIEDAD"] if row else ""
                matricula = row["MATRICULA_INMOBILIARIA"] if row else ""
                arrendatario = row["ARRENDATARIO"] if row else ""

            async with self:
                self.recaudo_actual = {
                    "id_recaudo": recaudo.id_recaudo,
                    "id_contrato": recaudo.id_contrato_a,
                    "direccion": direccion,
                    "matricula": matricula,
                    "arrendatario": arrendatario,
                    "fecha_pago": recaudo.fecha_pago,
                    "valor_total": recaudo.valor_total,
                    "valor_total_view": format_currency(recaudo.valor_total),
                    "metodo_pago": recaudo.metodo_pago,
                    "referencia": recaudo.referencia_bancaria or "",
                    "estado": recaudo.estado_recaudo,
                    "observaciones": recaudo.observaciones or "",
                    "created_at": recaudo.created_at or "",
                    "created_by": recaudo.created_by or "",
                    "conceptos": [
                        {
                            "tipo": c.tipo_concepto, 
                            "periodo": c.periodo, 
                            "valor": c.valor,
                            "valor_view": format_currency(c.valor)
                        }
                        for c in conceptos
                    ],
                }
                self.show_detail_modal = True
                self.show_form_modal = False
                self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar detalle: {str(e)}"
                self.is_loading = False

    @rx.event(background=True)
    async def save_recaudo(self, form_data: Dict):
        """Guarda recaudo (crear o editar)."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            repo = RepositorioRecaudoSQLite(db_manager)
            usuario_sistema = "admin"  # TODO: Obtener de AuthState

            # Validaciones
            # Validaciones y parsing de ID Contrato
            id_contrato = form_data["id_contrato_a"]
            if isinstance(id_contrato, str) and not id_contrato.isdigit():
                # Buscar en las opciones
                contrato_opt = next(
                    (c for c in self.contratos_options if c["texto"] == id_contrato), None
                )
                if contrato_opt:
                    id_contrato = contrato_opt["id"]
                else:
                    # Intentar extraer ID si formato es "ID:123 - ..."
                    if id_contrato.startswith("ID:"):
                        try:
                            id_contrato = id_contrato.split(":")[1].split(" -")[0].strip()
                        except:
                            pass

            valor_total = int(form_data.get("valor_total", 0))
            if valor_total <= 0:
                async with self:
                    self.error_message = "El valor total debe ser mayor a cero"
                    self.is_loading = False
                return

            metodo_pago = form_data.get("metodo_pago", "")
            if metodo_pago != "Efectivo" and not form_data.get("referencia _bancaria", "").strip():
                async with self:
                    self.error_message = (
                        "La referencia bancaria es obligatoria para pagos electrónicos"
                    )
                    self.is_loading = False
                return

            # Crear entidad
            recaudo = Recaudo(
                id_recaudo=form_data.get("id_recaudo"),
                id_contrato_a=int(id_contrato),
                fecha_pago=form_data["fecha_pago"],
                valor_total=valor_total,
                metodo_pago=metodo_pago,
                referencia_bancaria=form_data.get("referencia_bancaria", "").strip() or None,
                estado_recaudo="Pendiente",
                observaciones=form_data.get("observaciones", "").strip() or None,
                created_by=usuario_sistema,
            )

            # Crear concepto simple (Canon completo)
            concepto = RecaudoConcepto(
                id_recaudo=None,
                tipo_concepto=form_data.get("tipo_concepto", "Canon"),
                periodo=form_data.get("periodo", datetime.now().strftime("%Y-%m")),
                valor=valor_total,
            )

            if form_data.get("id_recaudo"):
                # Editar (sin cambiar conceptos por ahora)
                repo.actualizar(recaudo, usuario_sistema)
            else:
                # Crear
                repo.crear(recaudo, [concepto], usuario_sistema)

            async with self:
                self.show_form_modal = False
                self.form_data = {}

            # Recargar lista
            yield RecaudosState.load_recaudos()

        except ValueError as e:
            async with self:
                self.error_message = str(e)
        except Exception as e:
            async with self:
                self.error_message = f"Error al guardar: {str(e)}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def eliminar_recaudo(self, id_recaudo: int):
        """Elimina (soft delete) un recaudo."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            repo = RepositorioRecaudoSQLite(db_manager)
            usuario_sistema = "admin"  # TODO: Obtener de AuthState

            # Verificar que esté pendiente
            recaudo = repo.obtener_por_id(id_recaudo)
            if recaudo and recaudo.estado_recaudo != "Pendiente":
                async with self:
                    self.error_message = "Solo se pueden eliminar recaudos en estado 'Pendiente'"
                    self.is_loading = False
                return

            repo.eliminar(id_recaudo, usuario_sistema)

            async with self:
                self.is_loading = False

            # Recargar lista
            yield RecaudosState.load_recaudos()

        except Exception as e:
            async with self:
                self.error_message = f"Error al eliminar: {str(e)}"
                self.is_loading = False

    @rx.event(background=True)
    async def aplicar_pago(self, id_recaudo: int):
        """Aplica un pago pendiente, cambiando su estado a 'Aplicado'.

        Business Rules:
        - Solo pagos en estado 'Pendiente' pueden ser aplicados
        - Una vez aplicado, el pago no puede ser editado ni eliminado
        - El pago aplicado sí puede ser reversado
        """
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            repo = RepositorioRecaudoSQLite(db_manager)
            usuario_sistema = "admin"  # TODO: Obtener de AuthState

            # Verificar estado actual
            recaudo = repo.obtener_por_id(id_recaudo)
            if not recaudo:
                async with self:
                    self.error_message = "Recaudo no encontrado"
                    self.is_loading = False
                return

            if recaudo.estado_recaudo != "Pendiente":
                async with self:
                    self.error_message = f"Solo se pueden aplicar pagos en estado 'Pendiente'. Estado actual: {recaudo.estado_recaudo}"
                    self.is_loading = False
                return

            # Cambiar estado a Aplicado
            repo.cambiar_estado(id_recaudo, "Aplicado", usuario_sistema)

            async with self:
                self.is_loading = False

            # Toast de éxito
            yield rx.toast.success(f"Pago #{id_recaudo} aplicado exitosamente")

            # Recargar lista
            yield RecaudosState.load_recaudos()

        except Exception as e:
            async with self:
                self.error_message = f"Error al aplicar pago: {str(e)}"
                self.is_loading = False

    @rx.event(background=True)
    async def reversar_pago(self, id_recaudo: int):
        """Reversa un pago aplicado, cambiando su estado a 'Reversado'.

        Business Rules:
        - Solo pagos en estado 'Aplicado' pueden ser reversados
        - Un pago reversado NO puede volver a aplicarse
        - El reversado es una acción definitiva (requiere crear nuevo pago si es error)
        """
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            repo = RepositorioRecaudoSQLite(db_manager)
            usuario_sistema = "admin"  # TODO: Obtener de AuthState

            # Verificar estado actual
            recaudo = repo.obtener_por_id(id_recaudo)
            if not recaudo:
                async with self:
                    self.error_message = "Recaudo no encontrado"
                    self.is_loading = False
                return

            if recaudo.estado_recaudo != "Aplicado":
                async with self:
                    self.error_message = f"Solo se pueden reversar pagos en estado 'Aplicado'. Estado actual: {recaudo.estado_recaudo}"
                    self.is_loading = False
                return

            # Cambiar estado a Reversado
            repo.cambiar_estado(id_recaudo, "Reversado", usuario_sistema)

            async with self:
                self.is_loading = False

            # Toast de advertencia (es una acción importante)
            yield rx.toast.warning(f"Pago #{id_recaudo} reversado")

            # Recargar lista
            yield RecaudosState.load_recaudos()

        except Exception as e:
            async with self:
                self.error_message = f"Error al reversar pago: {str(e)}"
                self.is_loading = False

    @rx.event(background=True)
    async def generar_pagos_masivos(self):
        """Genera pagos masivos para todos los contratos de arrendamiento activos.
        - Fecha de pago = fecha del sistema (hoy)
        - Valor total = canon de arrendamiento del contrato
        - Método de pago = Masivo
        - Tipo de concepto = Canon
        - Período = mes actual en español
        """
        pass  # print("=" * 60) [OpSec Removed]
        pass  # print("[DEBUG] === INICIO generar_pagos_masivos ===") [OpSec Removed]
        pass  # print("=" * 60) [OpSec Removed]

        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            pass  # print("[DEBUG] Creando repositorio...") [OpSec Removed]
            repo = RepositorioRecaudoSQLite(db_manager)
            usuario_sistema = "admin"
            fecha_hoy = datetime.now().date().isoformat()
            pass  # print(f"[DEBUG] Fecha hoy: {fecha_hoy}") [OpSec Removed]

            # Calcular período: YYYY-MM para BD, español para observaciones
            mes_actual = datetime.now().month
            anio_actual = datetime.now().year
            periodo_bd = f"{anio_actual}-{mes_actual:02d}"  # Formato YYYY-MM para BD
            meses_espanol = [
                "enero",
                "febrero",
                "marzo",
                "abril",
                "mayo",
                "junio",
                "julio",
                "agosto",
                "septiembre",
                "octubre",
                "noviembre",
                "diciembre",
            ]
            periodo_display = (
                f"{meses_espanol[mes_actual - 1]} de {anio_actual}"  # Para observaciones
            )
            pass  # print(f"[DEBUG] Periodo BD: {periodo_bd}, Display: {periodo_display}") [OpSec Removed]

            # Obtener todos los contratos activos con su canon
            query = """
                SELECT 
                    ca.ID_CONTRATO_A,
                    ca.CANON_ARRENDAMIENTO,
                    p.DIRECCION_PROPIEDAD
                FROM CONTRATOS_ARRENDAMIENTOS ca
                INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                WHERE ca.ESTADO_CONTRATO_A = 'Activo'
            """

            pass  # print("[DEBUG] Ejecutando query para obtener contratos activos...") [OpSec Removed]
            with db_manager.obtener_conexion() as conn:
                cursor = db_manager.get_dict_cursor(conn)
                cursor.execute(query)
                contratos_activos = cursor.fetchall()

            pass  # print(f"[DEBUG] Contratos activos encontrados: {len(contratos_activos)}") [OpSec Removed]

            if not contratos_activos:
                pass  # print("[DEBUG] No hay contratos activos - SALIENDO") [OpSec Removed]
                async with self:
                    self.error_message = "No hay contratos activos para generar pagos"
                    self.is_loading = False
                return

            # Mostrar detalle de contratos
            for i, c in enumerate(contratos_activos):
                pass  # print(f"[DEBUG] Contrato {i+1}: ID={c.get('ID_CONTRATO_A')}, Canon={c.get('CANON_ARRENDAMIENTO')}") [OpSec Removed]

            pagos_generados = 0
            errores = []

            for contrato in contratos_activos:
                try:
                    id_contrato = contrato["ID_CONTRATO_A"]
                    canon = contrato["CANON_ARRENDAMIENTO"]
                    pass  # print(f"[DEBUG] Procesando contrato {id_contrato} con canon {canon}") [OpSec Removed]

                    if not canon or canon <= 0:
                        pass  # print(f"[DEBUG] Contrato {id_contrato}: Canon inválido ({canon})") [OpSec Removed]
                        errores.append(f"Contrato {id_contrato}: Canon inválido")
                        continue

                    # Crear entidad Recaudo
                    pass  # print(f"[DEBUG] Creando entidad Recaudo para contrato {id_contrato}...") [OpSec Removed]
                    recaudo = Recaudo(
                        id_recaudo=None,
                        id_contrato_a=id_contrato,
                        fecha_pago=fecha_hoy,
                        valor_total=canon,
                        metodo_pago="Efectivo",
                        referencia_bancaria=None,
                        estado_recaudo="Pendiente",
                        observaciones=f"Pago masivo generado - {periodo_display}",
                        created_by=usuario_sistema,
                    )
                    pass  # print(f"[DEBUG] Recaudo creado: {recaudo.__dict__}") [OpSec Removed]

                    # Crear concepto (Canon completo)
                    pass  # print(f"[DEBUG] Creando concepto para contrato {id_contrato}...") [OpSec Removed]
                    concepto = RecaudoConcepto(
                        id_recaudo=None,
                        tipo_concepto="Canon",
                        periodo=periodo_bd,  # Usar formato YYYY-MM
                        valor=canon,
                    )
                    pass  # print(f"[DEBUG] Concepto creado: {concepto.__dict__}") [OpSec Removed]

                    pass  # print(f"[DEBUG] Guardando en BD contrato {id_contrato}...") [OpSec Removed]
                    repo.crear(recaudo, [concepto], usuario_sistema)
                    pass  # print(f"[DEBUG] Contrato {id_contrato} guardado exitosamente!") [OpSec Removed]
                    pagos_generados += 1

                except Exception as e:
                    pass  # print(f"[DEBUG] ERROR en contrato {id_contrato}: {str(e)}") [OpSec Removed]
                    import traceback

                    traceback.print_exc()
                    errores.append(f"Contrato {id_contrato}: {str(e)}")

            pass  # print(f"[DEBUG] Pagos generados: {pagos_generados}, Errores: {len(errores)}") [OpSec Removed]

            async with self:
                self.is_loading = False
                if errores:
                    self.error_message = (
                        f"Generados {pagos_generados} pagos. Errores: {len(errores)}"
                    )
                    pass  # print(f"[DEBUG] Errores: {errores}") [OpSec Removed]
                else:
                    self.error_message = ""

            # Mostrar toast de éxito
            pass  # print(f"[DEBUG] Mostrando toast de éxito...") [OpSec Removed]
            yield rx.toast.success(f"Se generaron {pagos_generados} pagos masivos exitosamente")

            # Recargar lista
            pass  # print("[DEBUG] Recargando lista de recaudos...") [OpSec Removed]
            yield RecaudosState.load_recaudos()

            pass  # print("=" * 60) [OpSec Removed]
            pass  # print("[DEBUG] === FIN generar_pagos_masivos ===") [OpSec Removed]
            pass  # print("=" * 60) [OpSec Removed]

        except Exception as e:
            pass  # print(f"[DEBUG] ERROR GENERAL: {str(e)}") [OpSec Removed]
            import traceback

            traceback.print_exc()
            async with self:
                self.error_message = f"Error al generar pagos masivos: {str(e)}"
                self.is_loading = False
