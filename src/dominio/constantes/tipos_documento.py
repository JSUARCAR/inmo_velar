"""
Constantes y definiciones para el módulo de Gestión Documental Elite.
Define los tipos de documentos permitidos por módulo y reglas de validación.
"""

from typing import Dict, List, Any

# Configuración de tipos de documento por módulo
TIPOS_DOCUMENTO_MODULO: Dict[str, Dict[str, Any]] = {
    "CONTRATO_MANDATO": {
        "contrato_firmado": {"label": "Contrato Firmado", "tipos": [".pdf"], "max_size": 10*1024*1024},
        "cedula_propietario": {"label": "Cédula Propietario", "tipos": [".jpg", ".png", ".pdf"], "max_size": 2*1024*1024},
        "rut_propietario": {"label": "RUT Propietario", "tipos": [".pdf"], "max_size": 2*1024*1024},
        "camara_comercio": {"label": "Cámara de Comercio", "tipos": [".pdf"], "max_size": 2*1024*1024},
        "certificado_libertad": {"label": "Certificado de Libertad", "tipos": [".pdf"], "max_size": 2*1024*1024}
    },
    "CONTRATO_ARRENDAMIENTO": {
        "contrato_firmado": {"label": "Contrato Firmado", "tipos": [".pdf"], "max_size": 10*1024*1024},
        "poder_notarial": {"label": "Poder Notarial", "tipos": [".pdf"], "max_size": 5*1024*1024},
        "cedula_arrendatario": {"label": "Cédula Arrendatario", "tipos": [".jpg", ".png", ".pdf"], "max_size": 2*1024*1024},
        "cedula_codeudor": {"label": "Cédula Codeudor", "tipos": [".jpg", ".png", ".pdf"], "max_size": 2*1024*1024},
        "acta_entrega": {"label": "Acta de Entrega", "tipos": [".pdf"], "max_size": 5*1024*1024},
        "acta_desocupacion": {"label": "Acta de Desocupación", "tipos": [".pdf"], "max_size": 5*1024*1024}
    },
    "INCIDENTE": {
        "foto_daño": {"label": "Foto del Daño", "tipos": [".jpg", ".png", ".jpeg"], "max_size": 5*1024*1024, "multiple": True},
        "cotizacion_proveedor": {"label": "Cotización Proveedor", "tipos": [".pdf"], "max_size": 3*1024*1024},
        "comprobante_reparacion": {"label": "Comprobante Reparación", "tipos": [".pdf"], "max_size": 5*1024*1024}
    },
    "DESOCUPACION": {
        "checklist_fisico": {"label": "Checklist Físico", "tipos": [".pdf"], "max_size": 2*1024*1024},
        "foto_estado_inicial": {"label": "Foto Estado Inicial", "tipos": [".jpg", ".png"], "max_size": 3*1024*1024, "multiple": True},
        "foto_estado_final": {"label": "Foto Estado Final", "tipos": [".jpg", ".png"], "max_size": 3*1024*1024, "multiple": True},
        "paz_y_salvo_servicios": {"label": "Paz y Salvo Servicios", "tipos": [".pdf"], "max_size": 2*1024*1024}
    },
    "RECAUDO": {
        "comprobante_pago": {"label": "Comprobante de Pago", "tipos": [".pdf", ".jpg", ".png"], "max_size": 2*1024*1024},
        "soporte_transferencia": {"label": "Soporte Transferencia", "tipos": [".pdf"], "max_size": 1*1024*1024}
    },
    "LIQUIDACION": {
        "recibo_pago": {"label": "Recibo de Pago", "tipos": [".pdf"], "max_size": 2*1024*1024},
        "comprobante_bancario": {"label": "Comprobante Bancario", "tipos": [".pdf"], "max_size": 1*1024*1024}
    },
    "LIQUIDACION_ASESOR": {
        "recibo_pago": {"label": "Recibo de Pago", "tipos": [".pdf"], "max_size": 2*1024*1024},
        "comprobante_descuento": {"label": "Comprobante Descuento", "tipos": [".pdf"], "max_size": 1*1024*1024}
    },
    "RECIBO_PUBLICO": {
        "factura_servicio": {"label": "Factura Servicio", "tipos": [".pdf"], "max_size": 2*1024*1024},
        "comprobante_pago": {"label": "Comprobante de Pago", "tipos": [".pdf", ".jpg", ".png"], "max_size": 1*1024*1024}
    }
}

# Validaciones de documentos requeridos por estado del módulo
DOCUMENTOS_REQUERIDOS_POR_ESTADO: Dict[str, Dict[str, List[str]]] = {
    "CONTRATO_MANDATO": {
        "Activo": ["contrato_firmado", "cedula_propietario", "certificado_libertad"],
        "Finalizado": []
    },
    "CONTRATO_ARRENDAMIENTO": {
        "Activo": ["contrato_firmado", "cedula_arrendatario", "acta_entrega"],
        "Finalizado": ["acta_desocupacion"]
    },
    "INCIDENTE": {
        "Diagnóstico": ["foto_daño"],
        "En Reparación": ["cotizacion_proveedor"],
        "Finalizado": ["comprobante_reparacion"]
    },
    "DESOCUPACION": {
        "En Proceso": ["checklist_fisico", "foto_estado_inicial"],
        "Finalizada": ["acta_desocupacion", "foto_estado_final", "paz_y_salvo_servicios"]
    }
}
