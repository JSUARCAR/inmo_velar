# Contrato de Template: EstadoCuentaElite

**Feature**: 057-redisejo-estado-cuenta-pdf
**Date**: 2026-07-15

## Entrada del Template

El template `EstadoCuentaElite.generate(data)` acepta un dict con la siguiente estructura:

```python
{
    "estado_id": int,                    # ID de la liquidación
    "periodo": str,                      # Formato "YYYY-MM"
    "fecha_generacion": str,             # Fecha de generación
    "modo": str,                         # "individual" | "consolidado"
    "empresa": {                         # Configuración de empresa
        "logo": str,                     # Ruta al logo
        "nombre": str,                   # Nombre de la empresa
        # ... otros campos
    },
    "propietario": {                     # Datos del propietario
        "nombre": str,
        "documento": str,
        "telefono": str,
        "email": str,
    },
    "inmueble": {                        # Datos del inmueble
        "direccion": str,
        "tipo": str,
        "canon": int,
    },
    "lista_propiedades": [               # Lista de propiedades
        {"id": int, "direccion": str}
    ],
    "detalle_propiedades": [             # Detalle financiero por propiedad
        {
            "id": int,                   # ID del contrato
            "canon": int,                # Canon bruto
            "comision": int,             # Monto comisión
            "iva": int,                  # IVA comisión
            "admin": int,                # Gastos administración
            "servicios": int,            # Gastos servicios
            "predial": int,              # Pago predial
            "incidentes": int,           # valor_incidentes (RENOMBRADO de "incidente")
            "total": int,                # neto_a_pagar
            "comision_porcentaje": int,  # Porcentaje en base 10000 (NUEVO)
        }
    ],
    "resumen": {                         # Resumen financiero
        "total_ingresos": int,
        "comision_monto": int,
        "comision_porcentaje": int,      # NUEVO
        "iva_comision": int,
        "gastos_administracion": int,
        "gastos_servicios": int,
        "pago_predial": int,
        "valor_incidentes": int,
        "valor_neto": int,
        "cuenta_bancaria": str,
    },
    "observaciones": str | None,         # Observaciones de la liquidación
}
```

## Salida del Template

El método `generate()` retorna la ruta del archivo PDF generado:

```python
str  # Ruta absoluta al archivo PDF generado
```

## Cambios en el Contrato

### Renombrado de campo
- `detalle_propiedades[].incidente` → `detalle_propiedades[].incidentes`

### Nuevos campos
- `detalle_propiedades[].comision_porcentaje` — Porcentaje de comisión en base 10000
- `resumen.comision_porcentaje` — Porcentaje de comisión en base 10000
- `resumen.comision_monto` — Monto de la comisión
- `resumen.iva_comision` — IVA sobre comisión
- `resumen.gastos_administracion` — Gastos de administración
- `resumen.gastos_servicios` — Gastos de servicios
- `resumen.pago_predial` — Pago de predial
- `resumen.valor_incidentes` — Total de incidentes

### Eliminación de comportamiento
- Se elimina la llamada a `enable_verification_qr()` — el QR ya no se renderiza
- Se elimina la fila TOTAL de la tabla de detalle financiero

### Comportamiento nuevo
- Columna INCIDENTES siempre visible (no condicional)
- Sección OBSERVACIONES siempre visible (con contenido vacío si no hay observaciones)
- Resumen Financiero con 8 conceptos en orden específico
