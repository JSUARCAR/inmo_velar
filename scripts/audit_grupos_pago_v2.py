import sys
import os
import csv
from datetime import datetime

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager
from src.dominio.servicios.calculadora_contratos import CalculadoraContratos

def auditar_contratos_mandato():
    print("Iniciando auditoría de Contratos de Mandato para migración a V2...")
    db = db_manager
    conn = db.obtener_conexion()
    cursor = db.get_dict_cursor(conn)
    
    query = """
    SELECT ID_CONTRATO_M, FECHA_INICIO_CONTRATO_M, GRUPO_OPERATIVO, FECHA_PAGO
    FROM CONTRATOS_MANDATOS
    WHERE ESTADO_CONTRATO_M = 'ACTIVO'
    """
    cursor.execute(query)
    contratos = cursor.fetchall()
    
    resultados = []
    
    for contrato in contratos:
        id_contrato = contrato['ID_CONTRATO_M']
        fecha_inicio = contrato['FECHA_INICIO_CONTRATO_M']
        grupo_actual = contrato['GRUPO_OPERATIVO']
        dia_pago_actual = contrato['FECHA_PAGO']
        
        # Calcular nuevos valores V2
        nuevo_grupo, nuevo_dia_pago = CalculadoraContratos.calcular_ciclo_pago_mandato(fecha_inicio)
        
        # Calcular un ejemplo del próximo pago basado en el mes actual
        hoy = datetime.now()
        fecha_pago_ejemplo = CalculadoraContratos.resolver_fecha_pago_habil(nuevo_dia_pago, hoy.month, hoy.year)
        
        resultados.append({
            'ID_Contrato': id_contrato,
            'Fecha_Inicio': fecha_inicio,
            'Grupo_V1': grupo_actual,
            'Dia_Pago_V1': dia_pago_actual,
            'Grupo_V2': nuevo_grupo,
            'Dia_Pago_V2': nuevo_dia_pago,
            f'Ejemplo_Pago_{hoy.month}_{hoy.year}': fecha_pago_ejemplo.strftime('%Y-%m-%d')
        })
        
    # Escribir a CSV
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    
    csv_file = os.path.join(output_dir, 'auditoria_grupos_pago_v2.csv')
    with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
        if resultados:
            writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
            writer.writeheader()
            writer.writerows(resultados)
            
    print(f"Auditoría completada. {len(resultados)} contratos analizados.")
    print(f"Resultados guardados en: {csv_file}")

if __name__ == "__main__":
    auditar_contratos_mandato()