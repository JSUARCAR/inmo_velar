from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion
from src.infraestructura.persistencia.database import db_manager

servicio = ServicioConfiguracion(db_manager)
logs = servicio.listar_auditoria(limit=5)
print(f"Total logs: {len(logs)}")
for log in logs:
    print(f"ID: {log.id_auditoria}, Tabla: {log.tabla}, Accion: {log.accion}")
