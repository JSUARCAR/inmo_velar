from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from src.dominio.entidades.incidente import Incidente
from src.dominio.entidades.cotizacion import Cotizacion
from src.dominio.entidades.historial_incidente import HistorialIncidente
from src.dominio.interfaces.repositorio_incidentes import RepositorioIncidentes
from src.dominio.interfaces.repositorio_proveedores import RepositorioProveedores
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_incidentes_sqlite import RepositorioIncidentesSQLite
from src.infraestructura.persistencia.repositorio_proveedores_sqlite import RepositorioProveedoresSQLite
from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite

from src.dominio.entidades.orden_trabajo import OrdenTrabajo
from src.dominio.interfaces.repositorio_orden_trabajo import RepositorioOrdenTrabajo
from src.infraestructura.persistencia.repositorio_orden_trabajo_sqlite import RepositorioOrdenTrabajoSQLite

class ServicioIncidentes:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.repo_incidentes = RepositorioIncidentesSQLite(db_manager)
        self.repo_proveedores = RepositorioProveedoresSQLite(db_manager)
        self.repo_propiedades = RepositorioPropiedadSQLite(db_manager)
        self.repo_ordenes = RepositorioOrdenTrabajoSQLite(db_manager)

    def reportar_incidente(self, datos: Dict[str, Any], usuario_sistema: str) -> Incidente:
        """
        Reporta un nuevo incidente.
        Estado inicial: Reportado.
        """
        incidente = Incidente(
            id_propiedad=datos['id_propiedad'],
            id_contrato_m=datos.get('id_contrato_m'),
            descripcion_incidente=datos['descripcion'],
            fecha_incidente=datos.get('fecha_incidente', datetime.now().isoformat()),
            prioridad=datos.get('prioridad', 'Media'),
            origen_reporte=datos.get('origen_reporte', 'Inquilino'),
            created_by=usuario_sistema
        )
        id_new = self.repo_incidentes.guardar(incidente)
        incidente.id_incidente = id_new
        return incidente

    
    def listar_incidentes(self, id_propiedad: Optional[int] = None, estado: Optional[str] = None) -> List[Incidente]:
        return self.repo_incidentes.listar(id_propiedad, estado)
    
    def listar_con_filtros(
        self,
        busqueda: Optional[str] = None,
        id_propiedad: Optional[int] = None,
        prioridad: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        id_proveedor: Optional[int] = None,
        dias_min: Optional[int] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Lista incidentes aplicando múltiples filtros."""
        incidentes = self.repo_incidentes.listar()
        
        # Filtro por búsqueda (ID o descripción)
        if busqueda:
            incidentes = [
                i for i in incidentes 
                if busqueda.lower() in i.descripcion_incidente.lower() 
                or str(i.id_incidente) == busqueda
            ]
        
        # Filtro por propiedad
        if id_propiedad:
            incidentes = [i for i in incidentes if i.id_propiedad == id_propiedad]
        
        # Filtro por prioridad
        if prioridad:
            incidentes = [i for i in incidentes if i.prioridad == prioridad]
        
        # Filtro por proveedor asignado
        if id_proveedor:
            incidentes = [i for i in incidentes if i.id_proveedor_asignado == id_proveedor]
        
        # Filtro por días sin resolver
        if dias_min is not None:
            incidentes = [i for i in incidentes if i.dias_sin_resolver >= dias_min]
        
        # Filtro por rango de fechas
        if fecha_desde:
            fecha_desde_dt = datetime.fromisoformat(fecha_desde)
            incidentes = [i for i in incidentes if i.fecha_incidente >= fecha_desde_dt]
        
        if fecha_hasta:
            fecha_hasta_dt = datetime.fromisoformat(fecha_hasta)
            incidentes = [i for i in incidentes if i.fecha_incidente <= fecha_hasta_dt]
        
        # Calcular total antes de paginar
        total_items = len(incidentes)
        
        # Paginación (si se solicita)
        if page is not None and page_size is not None:
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            incidentes = incidentes[start_idx:end_idx]
            
        return {
            "items": incidentes,
            "total": total_items
        }

    def obtener_detalle(self, id_incidente: int) -> Optional[Dict[str, Any]]:
        incidente = self.repo_incidentes.obtener_por_id(id_incidente)
        if not incidente:
            return None
        
        cotizaciones = self.repo_incidentes.obtener_cotizaciones(id_incidente)
        proveedor_asignado = None
        if incidente.id_proveedor_asignado:
            proveedor_asignado = self.repo_proveedores.obtener_por_id(incidente.id_proveedor_asignado)
            
        propiedad = self.repo_propiedades.obtener_por_id(incidente.id_propiedad)

        return {
            "incidente": incidente,
            "cotizaciones": cotizaciones,
            "proveedor_asignado": proveedor_asignado,
            "propiedad": propiedad
        }

    def cambiar_estado(self, id_incidente: int, nuevo_estado: str, usuario_sistema: str, 
                       datos_extra: Optional[Dict[str, Any]] = None) -> Incidente:
        """
        Gestiona transiciones de estado.
        """
        incidente = self.repo_incidentes.obtener_por_id(id_incidente)
        if not incidente:
            raise ValueError(f"Incidente {id_incidente} no encontrado")

        incidente.avanzar_estado(nuevo_estado, usuario_sistema)
        
        # Lógica específica por estado
        if nuevo_estado == "Aprobado" and datos_extra:
             # Si se aprueba manualmente sin cotización formal (ej: emergencia menor)
             if 'costo' in datos_extra:
                 incidente.costo_incidente = datos_extra['costo']
             if 'id_proveedor' in datos_extra:
                 incidente.id_proveedor_asignado = datos_extra['id_proveedor']
             if 'responsable_pago' in datos_extra:
                 incidente.responsable_pago = datos_extra['responsable_pago']

        self.repo_incidentes.actualizar(incidente)
        return incidente

    def registrar_cotizacion(self, id_incidente: int, datos_cotizacion: Dict[str, Any], usuario_sistema: str) -> Cotizacion:
        """
        Registra una cotización y pasa el incidente a 'Cotizado'.
        """
        pass  # print("\n" + "="*80) [OpSec Removed]
        pass  # print("DEBUG SERVICIO: registrar_cotizacion INICIADO") [OpSec Removed]
        pass  # print("="*80) [OpSec Removed]
        pass  # print(f"DEBUG SERVICIO: id_incidente = {id_incidente}") [OpSec Removed]
        pass  # print(f"DEBUG SERVICIO: datos_cotizacion = {datos_cotizacion}") [OpSec Removed]
        pass  # print(f"DEBUG SERVICIO: usuario_sistema = {usuario_sistema}") [OpSec Removed]
        
        pass  # print("DEBUG SERVICIO: Obteniendo incidente...") [OpSec Removed]
        incidente = self.repo_incidentes.obtener_por_id(id_incidente)
        pass  # print(f"DEBUG SERVICIO: Incidente obtenido = {incidente}") [OpSec Removed]
        
        if not incidente:
            pass  # print("DEBUG SERVICIO: ERROR - Incidente no encontrado") [OpSec Removed]
            raise ValueError("Incidente no encontrado")
        
        pass  # print("DEBUG SERVICIO: Creando objeto Cotizacion...") [OpSec Removed]
        pass  # print(f"DEBUG SERVICIO: - id_proveedor de datos = {datos_cotizacion.get('id_proveedor')}") [OpSec Removed]
        pass  # print(f"DEBUG SERVICIO: - materiales (buscando 'materiales') = {datos_cotizacion.get('materiales', 'NO_ENCONTRADO')}") [OpSec Removed]
        pass  # print(f"DEBUG SERVICIO: - materiales (buscando 'costo_materiales') = {datos_cotizacion.get('costo_materiales', 'NO_ENCONTRADO')}") [OpSec Removed]
        pass  # print(f"DEBUG SERVICIO: - mano_obra (buscando 'mano_obra') = {datos_cotizacion.get('mano_obra', 'NO_ENCONTRADO')}") [OpSec Removed]
        pass  # print(f"DEBUG SERVICIO: - mano_obra (buscando 'costo_mano_obra') = {datos_cotizacion.get('costo_mano_obra', 'NO_ENCONTRADO')}") [OpSec Removed]
        
        cotizacion = Cotizacion(
            id_incidente=id_incidente,
            id_proveedor=datos_cotizacion['id_proveedor'],
            valor_materiales=datos_cotizacion.get('materiales', 0),
            valor_mano_obra=datos_cotizacion.get('mano_obra', 0),
            descripcion_trabajo=datos_cotizacion.get('descripcion'),
            dias_estimados=datos_cotizacion.get('dias', 1),
            created_by=usuario_sistema
        )
        pass  # print(f"DEBUG SERVICIO: Cotizacion creada = {cotizacion}") [OpSec Removed]
        
        pass  # print("DEBUG SERVICIO: Calculando total...") [OpSec Removed]
        cotizacion.calcular_total() # Suma materiales + mano de obra
        pass  # print(f"DEBUG SERVICIO: Total calculado = {cotizacion.valor_total}") [OpSec Removed]
        
        pass  # print("DEBUG SERVICIO: Llamando repo_incidentes.guardar_cotizacion...") [OpSec Removed]
        resultado = self.repo_incidentes.guardar_cotizacion(cotizacion)
        pass  # print(f"DEBUG SERVICIO: Resultado de guardar = {resultado}") [OpSec Removed]
        
        # Actualizar estado incidente si estaba en Reportado o En Revision
        pass  # print(f"DEBUG SERVICIO: Estado actual del incidente = {incidente.estado}") [OpSec Removed]
        # Actualizar estado incidente si estaba en Reportado
        if incidente.estado == "Reportado":
            pass  # print("DEBUG SERVICIO: Actualizando estado Reportado -> En Revision...") [OpSec Removed]
            incidente.avanzar_estado("En Revision", usuario_sistema)
            self.repo_incidentes.actualizar(incidente)
            pass  # print("DEBUG SERVICIO: Estado actualizado a En Revision") [OpSec Removed]
        
        # NOTA: Ya no pasamos automáticamente a "Cotizado". 
        # El usuario debe hacerlo explícitamente desde el UI cuando termine de cargar cotizaciones.
        
        pass  # print("DEBUG SERVICIO: registrar_cotizacion COMPLETADO") [OpSec Removed]
        pass  # print("="*80 + "\n") [OpSec Removed]
        return cotizacion
        
        pass  # print("DEBUG SERVICIO: registrar_cotizacion COMPLETADO") [OpSec Removed]
        pass  # print("="*80 + "\n") [OpSec Removed]
        return cotizacion

    def iniciar_reparacion(self, id_incidente: int, usuario_sistema: str) -> None:
        """
        Inicia la reparación, cambiando el estado de Aprobado a En Reparacion.
        """
        incidente = self.repo_incidentes.obtener_por_id(id_incidente)
        if not incidente:
            raise ValueError(f"Incidente {id_incidente} no encontrado")
        
        if incidente.estado != "Aprobado":
            raise ValueError(f"Solo se puede iniciar reparación desde estado Aprobado. Estado actual: {incidente.estado}")
        
        incidente.avanzar_estado("En Reparacion", usuario_sistema)
        self.repo_incidentes.actualizar(incidente)

    def aprobar_cotizacion(self, id_incidente: int, id_cotizacion: int, usuario_sistema: str, responsable_pago: str) -> None:
        """
        Aprueba una cotización, asigna el proveedor y costo, y pasa a 'Aprobado'.
        """
        incidente = self.repo_incidentes.obtener_por_id(id_incidente)
        cotizaciones = self.repo_incidentes.obtener_cotizaciones(id_incidente)
        
        cotizacion_aprobada = next((c for c in cotizaciones if c.id_cotizacion == id_cotizacion), None)
        if not cotizacion_aprobada:
             raise ValueError("Cotización no encontrada")
             
        # Actualizar todas las cotizaciones
        for c in cotizaciones:
            c.estado_cotizacion = "Aprobada" if c.id_cotizacion == id_cotizacion else "Rechazada"
            self.repo_incidentes.actualizar_cotizacion(c)
            
        # Actualizar Incidente
        incidente.id_cotizacion_aprobada = id_cotizacion
        incidente.id_proveedor_asignado = cotizacion_aprobada.id_proveedor
        incidente.costo_incidente = cotizacion_aprobada.valor_total
        incidente.responsable_pago = responsable_pago
        incidente.avanzar_estado("Aprobado", usuario_sistema)
        
        self.repo_incidentes.actualizar(incidente)

        # Crear Orden de Trabajo automáticamente (DISABLED PER USER REQUEST)
        # orden = OrdenTrabajo(
        #     id_incidente=id_incidente,
        #     id_proveedor=cotizacion_aprobada.id_proveedor,
        #     costo_mano_obra=cotizacion_aprobada.valor_mano_obra,
        #     costo_materiales=cotizacion_aprobada.valor_materiales,
        #     descripcion_trabajo=cotizacion_aprobada.descripcion_trabajo,
        #     # dias_estimados no está en OrdenTrabajo, calculamos fecha fin
        #     estado="Pendiente"
        # )
        # self.repo_ordenes.guardar(orden)

    def obtener_costos_reparaciones_periodo(self, id_contrato_m: int, mes_anio: str) -> int:
        """
        Retorna la suma de costos de incidentes Aprobados/Finalizados en un mes dado,
        cuyo responsable de pago sea el Propietario.
        Útil para integración financiera.
        """
        # Esto requeriría un método en repositorio más específico.
        # Por ahora implementamos lógica en memoria o query raw si repo lo permite.
        # Simplificación: Listar todos y filtrar.
        # TODO: Optimizar con query SQL específica.
        incidentes = self.repo_incidentes.listar() # Ojo: performance. Mejorar repo.
        
        total = 0
        for inc in incidentes:
            if inc.id_contrato_m == id_contrato_m and inc.responsable_pago == "Propietario":
                 # Verificar fecha. Usamos fecha_arreglo o fecha_incidente?
                 # Usualmente fecha_arreglo o fecha de aprobación determina cuando se cobra.
                 # Usaremos updated_at como proxy de aprobación/finalización si fecha_arreglo es nula.
                 fecha_ref = inc.fecha_arreglo or inc.updated_at
                 if fecha_ref:
                     if isinstance(fecha_ref, str):
                         fecha_ref = datetime.fromisoformat(fecha_ref)
                     if fecha_ref.strftime("%Y-%m") == mes_anio:
                         total += inc.costo_incidente
        return total

    # ==================== NUEVOS MÉTODOS FASE 6.5 ====================
    
    def _registrar_historial(self, id_incidente: int, estado_anterior: str, estado_nuevo: str,
                             usuario: str, tipo_accion: str, comentario: str = None, 
                             datos_extra: Dict = None) -> None:
        """
        Método interno para registrar cambios en el historial del incidente.
        """
        historial = HistorialIncidente(
            id_incidente=id_incidente,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            usuario=usuario,
            comentario=comentario,
            tipo_accion=tipo_accion,
            datos_adicionales=json.dumps(datos_extra) if datos_extra else None
        )
        self.repo_incidentes.guardar_historial(historial)
    
    def rechazar_cotizacion(self, id_incidente: int, id_cotizacion: int, 
                            usuario_sistema: str, motivo: str = None) -> None:
        """
        Rechaza una cotización específica sin afectar el estado del incidente.
        Permite solicitar nuevas cotizaciones.
        """
        # Obtener incidente para saber su estado actual
        incidente = self.repo_incidentes.obtener_por_id(id_incidente)
        if not incidente:
            raise ValueError(f"Incidente {id_incidente} no encontrado")
        
        cotizaciones = self.repo_incidentes.obtener_cotizaciones(id_incidente)
        cotizacion = next((c for c in cotizaciones if c.id_cotizacion == id_cotizacion), None)
        
        if not cotizacion:
            raise ValueError("Cotización no encontrada")
        
        if cotizacion.estado_cotizacion != "Pendiente":
            raise ValueError(f"Solo se pueden rechazar cotizaciones pendientes. Estado actual: {cotizacion.estado_cotizacion}")
        
        # Actualizar estado de la cotización
        cotizacion.estado_cotizacion = "Rechazada"
        self.repo_incidentes.actualizar_cotizacion(cotizacion)
        
        # Registrar en historial (estado del incidente no cambia)
        self._registrar_historial(
            id_incidente=id_incidente,
            estado_anterior=incidente.estado,
            estado_nuevo=incidente.estado,  # No hay cambio de estado
            usuario=usuario_sistema,
            tipo_accion="COTIZACION_RECHAZADA",
            comentario=motivo,
            datos_extra={
                "id_cotizacion": id_cotizacion,
                "id_proveedor": cotizacion.id_proveedor,
                "valor_total": cotizacion.valor_total
            }
        )
    
    def finalizar_incidente(self, id_incidente: int, usuario_sistema: str, 
                            costo_final: int = None, comentario: str = None, 
                            fecha_arreglo: datetime = None) -> Incidente:
        """
        Finaliza un incidente que está En Reparación.
        Permite registrar el costo final real si difiere del presupuestado.
        """
        incidente = self.repo_incidentes.obtener_por_id(id_incidente)
        if not incidente:
            raise ValueError(f"Incidente {id_incidente} no encontrado")
        
        if incidente.estado != "En Reparacion":
            raise ValueError(f"Solo se pueden finalizar incidentes En Reparación. Estado actual: {incidente.estado}")
        
        estado_anterior = incidente.estado
        costo_anterior = incidente.costo_incidente
        
        # Actualizar costo si se proporciona uno diferente
        if costo_final is not None and costo_final != incidente.costo_incidente:
            incidente.costo_incidente = costo_final
        
        # Cambiar estado
        incidente.avanzar_estado("Finalizado", usuario_sistema)
        
        # Establecer fecha de arreglo (usar la provista o now)
        incidente.fecha_arreglo = fecha_arreglo if fecha_arreglo else datetime.now()
        
        self.repo_incidentes.actualizar(incidente)
        
        # Registrar en historial
        self._registrar_historial(
            id_incidente=id_incidente,
            estado_anterior=estado_anterior,
            estado_nuevo="Finalizado",
            usuario=usuario_sistema,
            tipo_accion="CAMBIO_ESTADO",
            comentario=comentario,
            datos_extra={
                "costo_presupuestado": costo_anterior,
                "costo_final": incidente.costo_incidente
            }
        )
        
        return incidente
    
    def cancelar_incidente(self, id_incidente: int, usuario_sistema: str, motivo: str) -> Incidente:
        """
        Cancela un incidente. Requiere un motivo obligatorio.
        Solo se puede cancelar si no está Finalizado o ya Cancelado.
        """
        if not motivo or not motivo.strip():
            raise ValueError("Se requiere un motivo para cancelar el incidente")
        
        incidente = self.repo_incidentes.obtener_por_id(id_incidente)
        if not incidente:
            raise ValueError(f"Incidente {id_incidente} no encontrado")
        
        if incidente.estado in ["Finalizado", "Cancelado"]:
            raise ValueError(f"No se puede cancelar un incidente {incidente.estado}")
        
        estado_anterior = incidente.estado
        
        # Cambiar estado
        incidente.estado = "Cancelado"  # Bypass avanzar_estado ya que cancelar es especial
        incidente.motivo_cancelacion = motivo
        incidente.updated_by = usuario_sistema
        incidente.updated_at = datetime.now()
        
        self.repo_incidentes.actualizar(incidente)
        
        # Registrar en historial
        self._registrar_historial(
            id_incidente=id_incidente,
            estado_anterior=estado_anterior,
            estado_nuevo="Cancelado",
            usuario=usuario_sistema,
            tipo_accion="CANCELACION",
            comentario=motivo
        )
        
        return incidente
    
    def obtener_historial(self, id_incidente: int) -> List[HistorialIncidente]:
        """
        Obtiene el historial completo de cambios de un incidente.
        """
        return self.repo_incidentes.obtener_historial(id_incidente)
    
    def obtener_cotizaciones_rechazadas(self, id_incidente: int) -> List[Cotizacion]:
        """
        Obtiene solo las cotizaciones rechazadas de un incidente.
        """
        cotizaciones = self.repo_incidentes.obtener_cotizaciones(id_incidente)
        return [c for c in cotizaciones if c.estado_cotizacion == "Rechazada"]

