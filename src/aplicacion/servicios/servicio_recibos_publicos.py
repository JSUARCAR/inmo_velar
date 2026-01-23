"""
Servicio de Aplicación para gestión de Recibos Públicos.
Contiene la lógica de negocio para operaciones de servicios públicos.
"""

from typing import List, Optional, Dict
from datetime import datetime, date

from src.dominio.entidades.recibo_publico import ReciboPublico
from src.infraestructura.repositorios.repositorio_recibo_publico_sqlite import RepositorioReciboPublicoSQLite
from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite


class ServicioRecibosPublicos:
    """Servicio para gestión de recibos de servicios públicos"""
    
    def __init__(
        self,
        repo_recibo: RepositorioReciboPublicoSQLite,
        repo_propiedad: RepositorioPropiedadSQLite
    ):
        self.repo_recibo = repo_recibo
        self.repo_propiedad = repo_propiedad
    
    def registrar_recibo(self, datos: dict, usuario: str) -> ReciboPublico:
        """
        Registra un nuevo recibo de servicio público.
        
        Args:
            datos: Diccionario con datos del recibo
            usuario: Usuario que registra
        
        Returns:
            ReciboPublico creado
        
        Raises:
            ValueError: Si hay errores de validación
        """
        # Validar que la propiedad existe
        id_propiedad = datos.get('id_propiedad')
        if not id_propiedad:
            raise ValueError("Debe especificar la propiedad")
        
        propiedad = self.repo_propiedad.obtener_por_id(id_propiedad)
        if not propiedad:
            raise ValueError(f"No existe la propiedad con ID {id_propiedad}")
        
        # Validar período
        periodo = datos.get('periodo_recibo', '').strip()
        if not periodo:
            raise ValueError("El período es obligatorio")
        
        # Validar formato YYYY-MM
        import re
        if not re.match(r'^\d{4}-\d{2}$', periodo):
            raise ValueError("El período debe tener formato YYYY-MM (ej: 2025-12)")
        
        # Validar tipo de servicio
        tipo_servicio = datos.get('tipo_servicio', '').strip()
        if not tipo_servicio:
            raise ValueError("El tipo de servicio es obligatorio")
        
        if tipo_servicio not in ReciboPublico.TIPOS_SERVICIO:
            raise ValueError(
                f"Tipo de servicio inválido. Debe ser uno de: {', '.join(ReciboPublico.TIPOS_SERVICIO)}"
            )
        
        # Validar valor
        try:
            valor_recibo = int(datos.get('valor_recibo', 0))
        except (ValueError, TypeError):
            raise ValueError("El valor del recibo debe ser un número válido")
        
        if valor_recibo < 0:
            raise ValueError("El valor del recibo no puede ser negativo")
        
        # Validar fechas calculadas
        fecha_desde = datos.get('fecha_desde')
        fecha_hasta = datos.get('fecha_hasta')
        dias_facturados = 0
        
        if fecha_desde and fecha_hasta:
            try:
                f_desde = date.fromisoformat(fecha_desde)
                f_hasta = date.fromisoformat(fecha_hasta)
                
                if f_hasta < f_desde:
                    raise ValueError("La fecha hasta no puede ser menor a la fecha desde")
                
                # Diferencia de días
                # Usuario pide "diferencia de dias".
                dias_facturados = (f_hasta - f_desde).days
                
            except ValueError as e:
                if "Invalid isoformat" in str(e):
                     raise ValueError("Formato de fechas inválido (YYYY-MM-DD)")
                raise e

        # Crear entidad
        recibo = ReciboPublico(
            id_propiedad=id_propiedad,
            periodo_recibo=periodo,
            tipo_servicio=tipo_servicio,
            valor_recibo=valor_recibo,
            fecha_vencimiento=datos.get('fecha_vencimiento'),
            estado=datos.get('estado', 'Pendiente'),
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            dias_facturados=dias_facturados,
            created_by=usuario,
            updated_by=usuario
        )
        
        # Persistir
        try:
            return self.repo_recibo.crear(recibo, usuario)
        except ValueError as e:
            # Ya existe un recibo para esta combinación
            raise
    
    def actualizar_recibo(self, id_recibo: int, datos: dict, usuario: str) -> ReciboPublico:
        """
        Actualiza un recibo existente.
        
        Args:
            id_recibo: ID del recibo
            datos: Datos a actualizar
            usuario: Usuario que actualiza
        
        Returns:
            ReciboPublico actualizado
        
        Raises:
            ValueError: Si el recibo no existe o hay errores de validación
        """
        # Obtener recibo actual
        recibo = self.repo_recibo.obtener_por_id(id_recibo)
        if not recibo:
            raise ValueError(f"No existe el recibo con ID {id_recibo}")
        
        # No permitir editar recibos pagados
        if recibo.esta_pagado and datos.get('estado') != 'Pagado':
            raise ValueError("No se puede editar un recibo que ya está pagado")
        
        # Actualizar campos si se proporcionan
        if 'valor_recibo' in datos:
            try:
                valor = int(datos['valor_recibo'])
                if valor < 0:
                    raise ValueError("El valor no puede ser negativo")
                recibo.valor_recibo = valor
            except (ValueError, TypeError):
                raise ValueError("El valor del recibo debe ser un número válido")
        
        if 'fecha_vencimiento' in datos:
            recibo.fecha_vencimiento = datos['fecha_vencimiento']
        
        if 'estado' in datos:
            estado = datos['estado']
            if estado not in ReciboPublico.ESTADOS:
                raise ValueError(f"Estado inválido: {estado}")
            recibo.estado = estado

        # Actualizar fechas y días
        nuevo_desde = datos.get('fecha_desde', recibo.fecha_desde)
        nuevo_hasta = datos.get('fecha_hasta', recibo.fecha_hasta)
        
        if nuevo_desde and nuevo_hasta:
            try:
                f_desde = date.fromisoformat(nuevo_desde)
                f_hasta = date.fromisoformat(nuevo_hasta)
                
                if f_hasta < f_desde:
                    raise ValueError("La fecha hasta no puede ser menor a la fecha desde")
                
                recibo.fecha_desde = nuevo_desde
                recibo.fecha_hasta = nuevo_hasta
                recibo.dias_facturados = (f_hasta - f_desde).days
            except ValueError:
                 raise ValueError("Formato de fechas inválido")
                 
        # Actualizar
        return self.repo_recibo.actualizar(recibo, usuario)
    
    def marcar_como_pagado(
        self,
        id_recibo: int,
        fecha_pago: str,
        comprobante: str,
        usuario: str
    ) -> ReciboPublico:
        """
        Marca un recibo como pagado.
        
        Args:
            id_recibo: ID del recibo
            fecha_pago: Fecha del pago (YYYY-MM-DD)
            comprobante: Referencia o número de comprobante
            usuario: Usuario que marca como pagado
        
        Returns:
            ReciboPublico actualizado
        
        Raises:
            ValueError: Si hay errores de validación
        """
        # Obtener recibo
        recibo = self.repo_recibo.obtener_por_id(id_recibo)
        if not recibo:
            raise ValueError(f"No existe el recibo con ID {id_recibo}")
        
        # Validar que no esté ya pagado
        if recibo.esta_pagado:
            raise ValueError("El recibo ya está marcado como pagado")
        
        # Validar fecha de pago
        if not fecha_pago:
            raise ValueError("La fecha de pago es obligatoria")
        
        try:
            date.fromisoformat(fecha_pago)
        except ValueError:
            raise ValueError("Formato de fecha de pago inválido. Use YYYY-MM-DD")
        
        # Validar comprobante
        if not comprobante or not comprobante.strip():
            raise ValueError("El comprobante es obligatorio")
        
        # Marcar como pagado
        recibo.marcar_como_pagado(fecha_pago, comprobante.strip())
        
        # Actualizar en BD
        return self.repo_recibo.actualizar(recibo, usuario)
    
    def obtener_por_propiedad(
        self,
        id_propiedad: int,
        periodo_inicio: Optional[str] = None,
        periodo_fin: Optional[str] = None
    ) -> List[ReciboPublico]:
        """
        Obtiene recibos de una propiedad.
        
        Args:
            id_propiedad: ID de la propiedad
            periodo_inicio: Período inicial (opcional)
            periodo_fin: Período final (opcional)
        
        Returns:
            Lista de recibos
        """
        return self.repo_recibo.listar_por_propiedad(id_propiedad, periodo_inicio, periodo_fin)
    
    def obtener_resumen_por_propiedad(self, id_propiedad: int, periodo: str) -> Dict[str, any]:
        """
        Obtiene un resumen de recibos de una propiedad para un período.
        
        Args:
            id_propiedad: ID de la propiedad
            periodo: Período (YYYY-MM)
        
        Returns:
            Diccionario con resumen:
            {
                'total': int,
                'pagado': int,
                'pendiente': int,
                'vencido': int,
                'recibos': List[ReciboPublico]
            }
        """
        recibos = self.repo_recibo.listar_por_propiedad(id_propiedad, periodo, periodo)
        
        total = sum(r.valor_recibo for r in recibos)
        pagado = sum(r.valor_recibo for r in recibos if r.esta_pagado)
        pendiente = sum(r.valor_recibo for r in recibos if r.estado == 'Pendiente')
        vencido = sum(r.valor_recibo for r in recibos if r.esta_vencido and not r.esta_pagado)
        
        return {
            'total': total,
            'pagado': pagado,
            'pendiente': pendiente,
            'vencido': vencido,
            'recibos': recibos
        }
    
    def listar_con_filtros(
        self,
        id_propiedad: Optional[int] = None,
        periodo_inicio: Optional[str] = None,
        periodo_fin: Optional[str] = None,
        tipo_servicio: Optional[str] = None,
        estado: Optional[str] = None
    ) -> List[ReciboPublico]:
        """
        Lista recibos con filtros múltiples.
        
        Args:
            id_propiedad: Filtrar por propiedad
            periodo_inicio: Filtrar desde período
            periodo_fin: Filtrar hasta período
            tipo_servicio: Filtrar por tipo
            estado: Filtrar por estado
        
        Returns:
            Lista de recibos filtrados
        """
        return self.repo_recibo.listar_con_filtros(
            id_propiedad=id_propiedad,
            periodo_inicio=periodo_inicio,
            periodo_fin=periodo_fin,
            tipo_servicio=tipo_servicio,
            estado=estado
        )
    
    def verificar_vencimientos(self, usuario: str) -> int:
        """
        Job para actualizar estados de recibos vencidos.
        Actualiza recibos 'Pendientes' a 'Vencidos' si pasó la fecha.
        
        Args:
            usuario: Usuario del sistema que ejecuta el job
        
        Returns:
            Cantidad de recibos actualizados
        """
        recibos_vencidos = self.repo_recibo.listar_vencidos()
        actualizados = 0
        
        for recibo in recibos_vencidos:
            if recibo.actualizar_estado_vencimiento():
                self.repo_recibo.actualizar(recibo, usuario)
                actualizados += 1
        
        return actualizados
    
    def obtener_recibos_vencidos(self) -> List[ReciboPublico]:
        """
        Obtiene lista de recibos vencidos para alertas.
        
        Returns:
            Lista de recibos vencidos
        """
        return self.repo_recibo.listar_vencidos()
    
    def eliminar_recibo(self, id_recibo: int) -> bool:
        """
        Elimina un recibo.
        
        Args:
            id_recibo: ID del recibo
        
        Returns:
            True si se eliminó
        
        Raises:
            ValueError: Si el recibo está pagado (no se puede eliminar)
        """
        recibo = self.repo_recibo.obtener_por_id(id_recibo)
        if not recibo:
            raise ValueError(f"No existe el recibo con ID {id_recibo}")
        
        if recibo.esta_pagado:
            raise ValueError("No se puede eliminar un recibo que ya está pagado")
        
        return self.repo_recibo.eliminar(id_recibo)
    
    def obtener_todos(self) -> List[ReciboPublico]:
        """
        Obtiene todos los recibos.
        
        Returns:
            Lista de todos los recibos
        """
        return self.repo_recibo.listar_todos()

    def obtener_detalle_ui(self, id_recibo: int) -> Optional[Dict]:
        """
        Obtiene los detalles de un recibo con formato para UI.
        
        Args:
            id_recibo: ID del recibo
            
        Returns:
            Diccionario con datos formateados o None si no existe
        """
        recibo = self.repo_recibo.obtener_por_id(id_recibo)
        if not recibo:
            return None
            
        propiedad = self.repo_propiedad.obtener_por_id(recibo.id_propiedad)
        direccion = propiedad.direccion_propiedad if propiedad else "Desconocida"
        
        # Obtener municipio si es posible (asumiendo que repository lo tiene o se puede cargar)
        # Por ahora simplificado
        
        return {
            'id_recibo': recibo.id_recibo_publico,
            'id_propiedad': recibo.id_propiedad,
            'direccion_propiedad': direccion,
            'periodo': recibo.periodo_recibo,
            'tipo_servicio': recibo.tipo_servicio,
            'valor': recibo.valor_recibo,
            'fecha_vencimiento': recibo.fecha_vencimiento or 'N/A',
            'fecha_pago': recibo.fecha_pago or 'No registrado',
            'comprobante': recibo.comprobante or 'N/A',
            'estado': recibo.estado,
            'esta_pagado': recibo.esta_pagado,
            'esta_vencido': recibo.esta_vencido,
            'created_at': recibo.created_at,
            'created_by': recibo.created_by,
            'updated_at': recibo.updated_at,
            'updated_by': recibo.updated_by
        }

    def listar_recibos_proximos_vencer(self, dias: int = 5) -> List[ReciboPublico]:
        """
        Lista recibos pendientes que vencen en los próximos N días (o ya vencieron).
        """
        # Delegamos en el repositorio
        return self.repo_recibo.listar_proximos_vencer(dias)
