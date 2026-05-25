import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from migraciones.database_config import get_database_connection
c = get_database_connection().cursor()
c.execute("SELECT ESTADO_CONTRATO_A, COUNT(*) FROM CONTRATOS_ARRENDAMIENTOS GROUP BY ESTADO_CONTRATO_A")
print("ARRIENDOS:", c.fetchall())
c.execute("SELECT ESTADO_CONTRATO_M, COUNT(*) FROM CONTRATOS_MANDATOS GROUP BY ESTADO_CONTRATO_M")
print("MANDATOS:", c.fetchall())
