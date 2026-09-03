import re

with open('src/aplicacion/servicios/servicio_propiedades.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = """                update_admin_sql = \"\"\"
                UPDATE LIQUIDACIONES
                SET GASTOS_ADMINISTRACION = %s,
                    TOTAL_EGRESOS = COALESCE(HONORARIOS, 0) + COALESCE(IVA, 0) + 
                                    COALESCE(RETEFUENTE, 0) + COALESCE(RETEICA, 0) + 
                                    COALESCE(TOTAL_DEDUCCIONES, 0) + %s,
                    NETO_A_PAGAR = COALESCE(TOTAL_INGRESOS, 0) - (
                                    COALESCE(HONORARIOS, 0) + COALESCE(IVA, 0) + 
                                    COALESCE(RETEFUENTE, 0) + COALESCE(RETEICA, 0) + 
                                    COALESCE(TOTAL_DEDUCCIONES, 0) + %s
                                   ),
                    UPDATED_AT = CURRENT_TIMESTAMP,
                    UPDATED_BY = %s
                WHERE ID_CONTRATO_M IN (
                    SELECT ID_CONTRATO_M FROM CONTRATOS_MANDATOS WHERE ID_PROPIEDAD = %s
                )
                AND ESTADO_LIQUIDACION = 'En Proceso'
                AND PERIODO = %s
                AND GASTOS_ADMINISTRACION = %s -- Solo si no fue sobreescrito manualmente con otro valor
                \"\"\""""

replacement = """                update_admin_sql = \"\"\"
                UPDATE LIQUIDACIONES
                SET GASTOS_ADMINISTRACION = %s,
                    TOTAL_EGRESOS = COALESCE(COMISION_MONTO, 0) + COALESCE(IVA_COMISION, 0) + 
                                    COALESCE(IMPUESTO_4X1000, 0) + COALESCE(GASTOS_SERVICIOS, 0) + 
                                    COALESCE(GASTOS_REPARACIONES, 0) + COALESCE(PAGO_PREDIAL, 0) + 
                                    COALESCE(SEGURO_MONTO, 0) + COALESCE(OTROS_EGRESOS, 0) + %s,
                    NETO_A_PAGAR = COALESCE(TOTAL_INGRESOS, 0) - (
                                    COALESCE(COMISION_MONTO, 0) + COALESCE(IVA_COMISION, 0) + 
                                    COALESCE(IMPUESTO_4X1000, 0) + COALESCE(GASTOS_SERVICIOS, 0) + 
                                    COALESCE(GASTOS_REPARACIONES, 0) + COALESCE(PAGO_PREDIAL, 0) + 
                                    COALESCE(SEGURO_MONTO, 0) + COALESCE(OTROS_EGRESOS, 0) + %s
                                   ) - COALESCE(VALOR_INCIDENTES, 0),
                    UPDATED_AT = CURRENT_TIMESTAMP,
                    UPDATED_BY = %s
                WHERE ID_CONTRATO_M IN (
                    SELECT ID_CONTRATO_M FROM CONTRATOS_MANDATOS WHERE ID_PROPIEDAD = %s
                )
                AND ESTADO_LIQUIDACION = 'En Proceso'
                AND PERIODO = %s
                AND GASTOS_ADMINISTRACION = %s -- Solo si no fue sobreescrito manualmente con otro valor
                \"\"\""""

if target in content:
    content = content.replace(target, replacement)
    with open('src/aplicacion/servicios/servicio_propiedades.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replace successful")
else:
    print("Target block not found in file")
