import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict
from src.dominio.interfaces.repositorio_idempotencia import IRepositorioIdempotencia
from src.infraestructura.persistencia.database import db_manager


class RepositorioIdempotenciaPostgres(IRepositorioIdempotencia):
    """
    Implementación nativa PostgreSQL para gestión de claves de idempotencia.
    """

    def existe(self, key: str) -> bool:
        sql = "SELECT 1 FROM IDEMPOTENCY_KEYS WHERE KEY = %s AND FECHA_EXPIRA > NOW()"
        result = db_manager.execute_query_one(sql, (key,))
        return result is not None

    def bloquear(
        self,
        key: str,
        operacion: str,
        parametros: Dict[str, Any],
        usuario_id: int,
        ttl_hours: int = 1,
    ) -> bool:
        fecha_expira = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
        params_json = json.dumps(parametros, default=str)
        sql = """
            INSERT INTO IDEMPOTENCY_KEYS (
                KEY, OPERACION, PARAMETROS, RESULTADO, USUARIO_ID, FECHA_EXPIRA, ESTADO, INTENTOS
            ) VALUES (%s, %s, %s, %s::jsonb, %s, %s, 'processing', 0)
            ON CONFLICT (KEY) DO NOTHING
            RETURNING ID_KEY
        """
        with db_manager.transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                sql,
                (
                    key,
                    operacion,
                    params_json,
                    '{"status": "processing"}',
                    usuario_id,
                    fecha_expira,
                ),
            )
            return cursor.fetchone() is not None

    def registrar(
        self,
        key: str,
        operacion: str,
        resultado: Any,
        parametros: Dict[str, Any],
        usuario_id: int,
        ttl_hours: int = 24,
    ) -> None:
        fecha_expira = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
        params_json = json.dumps(parametros, default=str)
        result_json = json.dumps(resultado, default=str)

        sql = """
            INSERT INTO IDEMPOTENCY_KEYS (
                KEY, OPERACION, PARAMETROS, RESULTADO, USUARIO_ID, FECHA_EXPIRA, ESTADO
            ) VALUES (%s, %s, %s, %s::jsonb, %s, %s, 'completed')
            ON CONFLICT (KEY) DO UPDATE SET
                RESULTADO = EXCLUDED.RESULTADO,
                ESTADO = 'completed',
                FECHA_EXPIRA = EXCLUDED.FECHA_EXPIRA,
                INTENTOS = IDEMPOTENCY_KEYS.INTENTOS + 1
        """
        db_manager.execute_write(
            sql, (key, operacion, params_json, result_json, usuario_id, fecha_expira)
        )

    def obtener_resultado(self, key: str) -> Optional[Any]:
        sql = "SELECT RESULTADO FROM IDEMPOTENCY_KEYS WHERE KEY = %s AND FECHA_EXPIRA > NOW()"
        row = db_manager.execute_query_one(sql, (key,))
        if row:
            resultado = row.get("RESULTADO")
            if isinstance(resultado, str):
                try:
                    return json.loads(resultado)
                except json.JSONDecodeError:
                    return resultado
            return resultado
        return None

    def registrar_evento(
        self,
        entidad_tipo: str,
        entidad_id: int,
        tipo_evento: str,
        idempotency_key: str,
        payload: Dict[str, Any],
        usuario_id: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        sql = """
            INSERT INTO EVENTOS_IDEMPOTENCIA (
                ENTIDAD_TIPO, ENTIDAD_ID, TIPO_EVENTO, IDEMPOTENCY_KEY, 
                PAYLOAD, METADATA, USUARIO_ID
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ENTIDAD_TIPO, ENTIDAD_ID, TIPO_EVENTO) DO NOTHING
        """
        payload_json = json.dumps(payload, default=str)
        metadata_json = json.dumps(metadata or {}, default=str)

        db_manager.execute_write(
            sql,
            (
                entidad_tipo,
                entidad_id,
                tipo_evento,
                idempotency_key,
                payload_json,
                metadata_json,
                usuario_id,
            ),
        )

    def limpiar_expirados(self) -> int:
        sql = "DELETE FROM IDEMPOTENCY_KEYS WHERE FECHA_EXPIRA < NOW()"
        return db_manager.execute_write(sql)
