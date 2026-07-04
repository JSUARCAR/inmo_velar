"""
Script de diagnóstico para verificar el estado de la liquidación 572
en la base de datos directamente.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Configuración de conexión desde .env
DB_CONFIG = {
    "host": "hopper.proxy.rlwy.net",
    "port": 12937,
    "database": "railway",
    "user": "postgres",
    "password": "tBltIuhaUSMqQFvUMtSqIPFQZdXwpPtU"
}

def diagnosticar_liquidacion_572():
    """Diagnosticar el estado de la liquidación 572"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("=" * 60)
        print("DIAGNOSTICO LIQUIDACION #572")
        print("=" * 60)
        
        # 1. Verificar liquidación
        print("\n1. DATOS DE LA LIQUIDACION:")
        cursor.execute("""
            SELECT ID_LIQUIDACION, PERIODO, ESTADO_LIQUIDACION, 
                   VALOR_INCIDENTES, GASTOS_REPARACIONES, NETO_A_PAGAR,
                   OBSERVACIONES, UPDATED_AT
            FROM LIQUIDACIONES 
            WHERE ID_LIQUIDACION = 572
        """)
        liq = cursor.fetchone()
        if liq:
            print(f"   ID: {liq['id_liquidacion']}")
            print(f"   Periodo: {liq['periodo']}")
            print(f"   Estado: {liq['estado_liquidacion']}")
            print(f"   VALOR_INCIDENTES: {liq['valor_incidentes']}")
            print(f"   GASTOS_REPARACIONES: {liq['gastos_reparaciones']}")
            print(f"   NETO_A_PAGAR: {liq['neto_a_pagar']}")
            print(f"   OBSERVACIONES: '{liq['observaciones']}'")
            print(f"   UPDATED_AT: {liq['updated_at']}")
        else:
            print("   [ERROR] Liquidacion 572 no encontrada")
            return
        
        # 2. Verificar relaciones incidente-liquidación
        print("\n2. RELACIONES INCIDENTE-LIQUIDACION:")
        cursor.execute("""
            SELECT * FROM INCIDENTE_LIQUIDACION 
            WHERE ID_LIQUIDACION = 572
        """)
        relaciones = cursor.fetchall()
        if relaciones:
            for r in relaciones:
                print(f"   Relacion ID: {r.get('id_relacion', 'N/A')}")
                print(f"   Incidente ID: {r.get('id_incidente', 'N/A')}")
                print(f"   Cuota #: {r.get('numero_cuota', 'N/A')}")
                print(f"   Valor Descuento: {r.get('valor_descuento', 'N/A')}")
                print(f"   Asociado por: {r.get('asociado_por', 'N/A')}")
                print(f"   Fecha: {r.get('created_at', 'N/A')}")
                print("   ---")
        else:
            print("   [INFO] No hay relaciones incidente-liquidacion")
        
        # 3. Verificar cuotas asociadas
        print("\n3. CUOTAS ASOCIADAS:")
        cursor.execute("""
            SELECT c.*, p.ID_INCIDENTE 
            FROM CUOTA_INCIDENTE c
            JOIN PLAN_PAGO_INCIDENTE p ON c.ID_PLAN_PAGO = p.ID_PLAN_PAGO
            WHERE c.ID_LIQUIDACION = 572
        """)
        cuotas = cursor.fetchall()
        if cuotas:
            for c in cuotas:
                print(f"   Cuota #: {c.get('numero_cuota', 'N/A')}")
                print(f"   Valor: {c.get('valor_cuota', 'N/A')}")
                print(f"   Estado: {c.get('estado_cuota', 'N/A')}")
                print(f"   Incidente ID: {c.get('id_incidente', 'N/A')}")
                print("   ---")
        else:
            print("   [INFO] No hay cuotas asociadas directamente")
        
        # 4. Verificar incidentes con plan de pago para esta liquidación
        print("\n4. INCIDENTES CON CUOTAS EN ESTA LIQUIDACION:")
        cursor.execute("""
            SELECT i.ID_INCIDENTE, i.DESCRIPCION_INCIDENTE, i.ESTADO,
                   p.ID_PLAN_PAGO, c.NUMERO_CUOTA, c.VALOR_CUOTA, c.ESTADO_CUOTA
            FROM INCIDENTES i
            JOIN PLAN_PAGO_INCIDENTE p ON i.ID_INCIDENTE = p.ID_INCIDENTE
            JOIN CUOTA_INCIDENTE c ON p.ID_PLAN_PAGO = c.ID_PLAN_PAGO
            WHERE c.ID_LIQUIDACION = 572
        """)
        incidentes = cursor.fetchall()
        if incidentes:
            for inc in incidentes:
                desc = inc['descripcion_incidente'] or 'N/A'
                print(f"   Incidente #{inc['id_incidente']}: {desc[:50]}")
                print(f"   Estado: {inc['estado']}")
                print(f"   Plan Pago ID: {inc['id_plan_pago']}")
                print(f"   Cuota #{inc['numero_cuota']}: ${inc['valor_cuota']} ({inc['estado_cuota']})")
                print("   ---")
        else:
            print("   [INFO] No se encontraron incidentes")
        
        # 5. Verificar triggers
        print("\n5. TRIGGERS RELACIONADOS:")
        cursor.execute("""
            SELECT trigger_name, event_manipulation, action_statement
            FROM information_schema.triggers
            WHERE event_object_table = 'INCIDENTE_LIQUIDACION'
        """)
        triggers = cursor.fetchall()
        if triggers:
            for t in triggers:
                print(f"   Trigger: {t['trigger_name']}")
                print(f"   Evento: {t['event_manipulation']}")
                print("   ---")
        else:
            print("   [INFO] No hay triggers en INCIDENTE_LIQUIDACION")
        
        print("\n" + "=" * 60)
        print("FIN DIAGNOSTICO")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error de conexion: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    diagnosticar_liquidacion_572()
