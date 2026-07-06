"""Constantes de textos para Tooltips del sistema Velar.

Centraliza todos los textos de tooltips para facilitar mantenimiento
y futuras traducciones. Cada módulo importa sus textos desde aquí.
"""

__all__ = [
    # Personas
    "TOOLTIP_PERSONAS_FILTRO_NOMBRE",
    "TOOLTIP_PERSONAS_FILTRO_DOCUMENTO",
    "TOOLTIP_PERSONAS_FILTRO_ROL",
    "TOOLTIP_PERSONAS_FILTRO_ESTADO",
    # Propiedades
    "TOOLTIP_PROPIEDADES_FILTRO_DIRECCION",
    "TOOLTIP_PROPIEDADES_FILTRO_TIPO",
    "TOOLTIP_PROPIEDADES_FILTRO_ESTADO",
    "TOOLTIP_PROPIEDADES_FILTRO_PRECIO",
    # Contratos
    "TOOLTIP_CONTRATOS_FILTRO_PROPIEDAD",
    "TOOLTIP_CONTRATOS_FILTRO_INQUILINO",
    "TOOLTIP_CONTRATOS_FILTRO_ESTADO",
    "TOOLTIP_CONTRATOS_FILTRO_FECHAS",
    # Liquidaciones
    "TOOLTIP_LIQUIDACIONES_FILTRO_PERIODO",
    "TOOLTIP_LIQUIDACIONES_FILTRO_ESTADO",
    "TOOLTIP_LIQUIDACIONES_FILTRO_PROPIEDAD",
    # Liquidación Asesores
    "TOOLTIP_LIQUIDACION_ASESORES_FILTRO_PERIODO",
    "TOOLTIP_LIQUIDACION_ASESORES_FILTRO_ASESOR",
    # Recaudos
    "TOOLTIP_RECAUDOS_FILTRO_FECHA",
    "TOOLTIP_RECAUDOS_FILTRO_PROPIEDAD",
    "TOOLTIP_RECAUDOS_FILTRO_ESTADO",
    # Desocupaciones
    "TOOLTIP_DESOCUPACIONES_FILTRO_PROPIEDAD",
    "TOOLTIP_DESOCUPACIONES_FILTRO_ESTADO",
    # Incidentes
    "TOOLTIP_INCIDENTES_FILTRO_PROPIEDAD",
    "TOOLTIP_INCIDENTES_FILTRO_ESTADO",
    "TOOLTIP_INCIDENTES_FILTRO_TIPO",
    # Seguros
    "TOOLTIP_SEGUROS_FILTRO_PROPIEDAD",
    "TOOLTIP_SEGUROS_FILTRO_ESTADO",
    "TOOLTIP_SEGUROS_FILTRO_VENCIMIENTO",
    # Recibos Públicos
    "TOOLTIP_RECIBOS_FILTRO_SERVICIO",
    "TOOLTIP_RECIBOS_FILTRO_PROPIEDAD",
    "TOOLTIP_RECIBOS_FILTRO_ESTADO",
    # Usuarios
    "TOOLTIP_USUARIOS_FILTRO_NOMBRE",
    "TOOLTIP_USUARIOS_FILTRO_ROL",
    "TOOLTIP_USUARIOS_FILTRO_ESTADO",
    # Modales comunes
    "TOOLTIP_MODAL_CAMPO_REQUERIDO",
    "TOOLTIP_MODAL_FORMATO_FECHA",
    "TOOLTIP_MODAL_SELECCIONAR_OPCION",
]

# --- Personas ---
TOOLTIP_PERSONAS_FILTRO_NOMBRE = "Filtra por nombre completo del propietario o arrendatario"
TOOLTIP_PERSONAS_FILTRO_DOCUMENTO = "Busca por número de cédula o RUC"
TOOLTIP_PERSONAS_FILTRO_ROL = "Filtra por tipo de rol: Propietario, Arrendatario, Asesor, etc."
TOOLTIP_PERSONAS_FILTRO_ESTADO = "Filtra por estado: Activo o Inactivo"

# --- Propiedades ---
TOOLTIP_PROPIEDADES_FILTRO_DIRECCION = "Busca por dirección o nombre del inmueble"
TOOLTIP_PROPIEDADES_FILTRO_TIPO = "Filtra por tipo: Apartamento, Casa, Local, Oficina, etc."
TOOLTIP_PROPIEDADES_FILTRO_ESTADO = "Filtra por estado: Disponible, Ocupada, En mantenimiento"
TOOLTIP_PROPIEDADES_FILTRO_PRECIO = "Filtra por rango de precio de arrendamiento mensual"

# --- Contratos ---
TOOLTIP_CONTRATOS_FILTRO_PROPIEDAD = "Filtra contratos por propiedad asociada"
TOOLTIP_CONTRATOS_FILTRO_INQUILINO = "Filtra por nombre del inquilino actual"
TOOLTIP_CONTRATOS_FILTRO_ESTADO = "Filtra por estado: Vigente, Vencido, Terminado"
TOOLTIP_CONTRATOS_FILTRO_FECHAS = "Filtra por rango de fechas de vigencia del contrato"

# --- Liquidaciones ---
TOOLTIP_LIQUIDACIONES_FILTRO_PERIODO = "Selecciona el mes y año de la liquidación"
TOOLTIP_LIQUIDACIONES_FILTRO_ESTADO = "Filtra por estado: Pendiente, Aprobada, Pagada"
TOOLTIP_LIQUIDACIONES_FILTRO_PROPIEDAD = "Filtra liquidaciones por propiedad"

# --- Liquidación Asesores ---
TOOLTIP_LIQUIDACION_ASESORES_FILTRO_PERIODO = "Selecciona el mes y año de la liquidación del asesor"
TOOLTIP_LIQUIDACION_ASESORES_FILTRO_ASESOR = "Filtra por nombre del asesor comercial"

# --- Recaudos ---
TOOLTIP_RECAUDOS_FILTRO_FECHA = "Filtra por fecha de recaudo o depósito"
TOOLTIP_RECAUDOS_FILTRO_PROPIEDAD = "Filtra recaudos por propiedad asociada"
TOOLTIP_RECAUDOS_FILTRO_ESTADO = "Filtra por estado: Registrado, Conciliado, Anulado"

# --- Desocupaciones ---
TOOLTIP_DESOCUPACIONES_FILTRO_PROPIEDAD = "Filtra procesos de desocupación por propiedad"
TOOLTIP_DESOCUPACIONES_FILTRO_ESTADO = "Filtra por estado: En proceso, Completada, Cancelada"

# --- Incidentes ---
TOOLTIP_INCIDENTES_FILTRO_PROPIEDAD = "Filtra incidentes por propiedad donde ocurrieron"
TOOLTIP_INCIDENTES_FILTRO_ESTADO = "Filtra por estado: Abierto, En atención, Cerrado"
TOOLTIP_INCIDENTES_FILTRO_TIPO = "Filtra por tipo: Mantenimiento, Daño, Queja, etc."

# --- Seguros ---
TOOLTIP_SEGUROS_FILTRO_PROPIEDAD = "Filtra pólizas de seguro por propiedad cubierta"
TOOLTIP_SEGUROS_FILTRO_ESTADO = "Filtra por estado: Vigente, Vencido, Cancelado"
TOOLTIP_SEGUROS_FILTRO_VENCIMIENTO = "Filtra por fecha de vencimiento de la póliza"

# --- Recibos Públicos ---
TOOLTIP_RECIBOS_FILTRO_SERVICIO = "Filtra por tipo de servicio: Agua, Electricidad, Gas, etc."
TOOLTIP_RECIBOS_FILTRO_PROPIEDAD = "Filtra recibos por propiedad"
TOOLTIP_RECIBOS_FILTRO_ESTADO = "Filtra por estado: Pendiente, Pagado, Vencido"

# --- Usuarios ---
TOOLTIP_USUARIOS_FILTRO_NOMBRE = "Busca por nombre o email del usuario"
TOOLTIP_USUARIOS_FILTRO_ROL = "Filtra por rol: Administrador, Operador, Visualizador"
TOOLTIP_USUARIOS_FILTRO_ESTADO = "Filtra por estado: Activo o Inactivo"

# --- Modales comunes ---
TOOLTIP_MODAL_CAMPO_REQUERIDO = "Este campo es obligatorio para continuar"
TOOLTIP_MODAL_FORMATO_FECHA = "Formato: DD/MM/AAAA"
TOOLTIP_MODAL_SELECCIONAR_OPCION = "Selecciona una opción de la lista"
