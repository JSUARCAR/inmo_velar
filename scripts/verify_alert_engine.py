"""
Script de verificación para el Motor de Alertas Tempranas.
Valida la sincronización, persistencia e idempotencia.
"""
import sys
import os
from pathlib import Path

# Añadir raíz al path
sys.path.append(os.getcwd())

def verify_alert_engine():
    from src.infraestructura.persistencia.database import db_manager
    from src.aplicacion.servicios.servicio_alertas import ServicioAlertas
    
    print("🚀 Iniciando Verificación de Motor de Alertas...")
    
    # 1. Preparar repositorio y servicio
    if db_manager.use_postgresql:
        from src.infraestructura.persistencia.repositorio_alerta_postgres import RepositorioAlertaPostgres
        repo = RepositorioAlertaPostgres(db_manager)
        print("🔗 Conectado a POSTGRESQL")
    else:
        from src.infraestructura.persistencia.repositorio_alerta_postgres import RepositorioAlertaPostgres
        repo = RepositorioAlertaPostgres(db_manager)
        print("🔗 Conectado a SQLITE")
        
    servicio = ServicioAlertas(db_manager, repo)
    
    # 2. Sincronizar
    print("⏳ Ejecutando sincronización inicial...")
    nuevas_1 = servicio.sincronizar_alertas(usuario_sistema="test_verify")
    print(f"✅ Sincronización 1: {nuevas_1} alertas creadas.")
    
    # 3. Validar Idempotencia
    print("⏳ Ejecutando sincronización inmediata (idempotencia)...")
    nuevas_2 = servicio.sincronizar_alertas(usuario_sistema="test_verify")
    print(f"✅ Sincronización 2: {nuevas_2} alertas creadas (Esperado: 0 si nada cambió).")
    
    # 4. Listar persistidas
    print("⏳ Consultando alertas persistidas...")
    alertas = servicio.obtener_alertas(estado="Pendiente")
    print(f"📊 Total alertas pendientes en DB: {len(alertas)}")
    
    for a in alertas[:3]:
        print(f"  - [{a['tipo_alerta']}] {a['descripcion_alerta'][:50]}...")
        
    print("\n✅ Verificación del Motor finalizada.")

if __name__ == "__main__":
    verify_alert_engine()
