"""
Servicio de Dominio: Calculadora de Contratos
Centraliza la lógica de cálculo de duraciones y validaciones de fechas.
"""

from datetime import date, datetime, timedelta
import calendar
from typing import Union, Tuple, Optional

# Constantes de tramos operativos V2 (Spec §FR-001..FR-003, contracts/contratos-dominio.md)
DIA_CORTE_GRUPO_1_INICIO: int = 28
DIA_CORTE_GRUPO_1_FIN: int = 7
DIA_CORTE_GRUPO_2_INICIO: int = 8
DIA_CORTE_GRUPO_2_FIN: int = 17
DIA_CORTE_GRUPO_3_INICIO: int = 18
DIA_CORTE_GRUPO_3_FIN: int = 27

DIA_PAGO_MANDATO_GRUPO_1: int = 10
DIA_PAGO_MANDATO_GRUPO_2: int = 20
DIA_PAGO_MANDATO_GRUPO_3: int = 30


class CalculadoraContratos:
    @staticmethod
    def _parsear_fecha(fecha: Union[date, str]) -> date:
        """
        Parsea una fecha a objeto date de forma segura.

        Args:
            fecha: Objeto date o cadena ISO (YYYY-MM-DD).

        Returns:
            date: Objeto date parseado.

        Raises:
            ValueError: Si la cadena no corresponde a un formato válido.
        """
        if isinstance(fecha, date):
            return fecha
        if isinstance(fecha, str):
            return datetime.strptime(fecha[:10], "%Y-%m-%d").date()
        raise ValueError(f"Tipo de fecha no soportado: {type(fecha)}")

    @staticmethod
    def calcular_duracion_meses(
        fecha_inicio: Union[date, str], fecha_fin: Union[date, str]
    ) -> int:
        """
        Calcula la duración en meses entre dos fechas de forma comercial.

        Reglas:
        - 01-Ene a 31-Ene = 1 mes.
        - 15-Ene a 14-Feb = 1 mes.
        - 15-Ene a 15-Feb = 1 mes (redondeado hacia abajo comercialmente, o inicio del segundo).

        Args:
            fecha_inicio: Fecha de inicio (date o string YYYY-MM-DD).
            fecha_fin: Fecha de fin (date o string YYYY-MM-DD).

        Returns:
            Entero con la cantidad de meses.
        """
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio[:10], "%Y-%m-%d").date()
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.strptime(fecha_fin[:10], "%Y-%m-%d").date()

        if fecha_fin < fecha_inicio:
            return 0

        years = fecha_fin.year - fecha_inicio.year
        months = fecha_fin.month - fecha_inicio.month
        total = years * 12 + months

        # Día del mes para comparación
        d1 = fecha_inicio.day
        d2 = fecha_fin.day

        # Último día del mes de fin
        _, last_day_fin = calendar.monthrange(fecha_fin.year, fecha_fin.month)

        if d1 == 1:
            # Si inicia el día 1, el mes se completa si llega a fin de mes
            if d2 >= last_day_fin - 1:
                return total + 1
            else:
                return total
        else:
            # Si inicia otro día, ej: 15, el mes se completa si llega al 14
            if d2 >= d1 - 1:
                return total
            else:
                # Si termina a fin de mes pero el mes tiene menos días (ej: 31-Ene a 28-Feb)
                if d2 == last_day_fin:
                    return total
                return max(0, total - 1)

    @staticmethod
    def validar_coherencia(
        fecha_inicio: str, fecha_fin: str, duracion_meses: int
    ) -> Tuple[bool, str]:
        """
        Valida si la duración coincide con el rango de fechas.
        """
        try:
            calc = CalculadoraContratos.calcular_duracion_meses(fecha_inicio, fecha_fin)
            if calc != duracion_meses:
                return (
                    False,
                    f"Discrepancia detectada: Las fechas indican {calc} meses, pero se registraron {duracion_meses}.",
                )
            return True, ""
        except Exception as e:
            return False, f"Error en validación: {str(e)}"

    @staticmethod
    def obtener_siguiente_dia_habil(fecha: date) -> date:
        """
        Calcula el siguiente día hábil en Colombia.
        Si la fecha cae en fin de semana (sábado/domingo) o en festivo,
        retorna el día hábil inmediatamente siguiente.
        """
        import holidays

        festivos_col = holidays.Colombia()
        dia = fecha
        # 5 es sábado, 6 es domingo en weekday()
        while dia.weekday() >= 5 or dia in festivos_col:
            from datetime import timedelta

            dia += timedelta(days=1)
        return dia

    @staticmethod
    def calcular_grupo_operativo(fecha: Union[date, str]) -> int:
        """
        Retorna 1, 2 o 3 según el tramo V2 del día de la fecha (28-7, 8-17, 18-27).

        Args:
            fecha: Objeto date o string YYYY-MM-DD.

        Returns:
            int: 1, 2 o 3 según el tramo del día.
        """
        fecha_obj = CalculadoraContratos._parsear_fecha(fecha)
        dia = fecha_obj.day
        if dia >= DIA_CORTE_GRUPO_1_INICIO or dia <= DIA_CORTE_GRUPO_1_FIN:
            return 1
        elif DIA_CORTE_GRUPO_2_INICIO <= dia <= DIA_CORTE_GRUPO_2_FIN:
            return 2
        else:
            return 3

    @staticmethod
    def calcular_dia_pago_mandato(fecha_inicio: Union[date, str]) -> int:
        """
        Retorna el día de pago para mandato según el nuevo grupo operativo V2.
        G1 (Inicios 28 al 7) -> Paga el 10
        G2 (Inicios 8 al 17) -> Paga el 20
        G3 (Inicios 18 al 27) -> Paga el 30

        Args:
            fecha_inicio: Objeto date o string YYYY-MM-DD.

        Returns:
            int: 10 para Grupo 1, 20 para Grupo 2, 30 para Grupo 3.
        """
        grupo = CalculadoraContratos.calcular_grupo_operativo(fecha_inicio)
        if grupo == 1:
            return DIA_PAGO_MANDATO_GRUPO_1
        elif grupo == 2:
            return DIA_PAGO_MANDATO_GRUPO_2
        else:
            return DIA_PAGO_MANDATO_GRUPO_3

    @staticmethod
    def calcular_ciclo_pago_mandato(fecha_inicio: Union[date, str]) -> Tuple[int, int]:
        """
        Calcula el grupo operativo y día de pago para mandato (Versión 2).
        Reglas Operativas:
        - 28 al 7: Grupo 1, Paga 10
        - 8 al 17: Grupo 2, Paga 20
        - 18 al 27: Grupo 3, Paga 30

        Args:
            fecha_inicio: Objeto date o string YYYY-MM-DD.

        Returns:
            Tuple[int, int]: (grupo_operativo, dia_pago_mandato).
        """
        return (
            CalculadoraContratos.calcular_grupo_operativo(fecha_inicio),
            CalculadoraContratos.calcular_dia_pago_mandato(fecha_inicio),
        )

    @staticmethod
    def resolver_dia_pago_real(
        fecha_pago: Optional[int], grupo_operativo: int, mes: int, año: int
    ) -> int:
        """
        Resuelve el día de pago real según el grupo, truncando al fin de mes
        si es necesario (ej: febrero) y ajustando por días hábiles.
        Retorna el día (int) o la fecha completa si se desea, pero por contrato actual
        debe retornar el día.
        Nota: Devuelve el día calculado. Para mayor exactitud financiera,
        se sugiere usar resolver_fecha_pago_habil.
        """
        dia_base = fecha_pago if fecha_pago is not None and fecha_pago != -1 else 30

        # Validar si el mes tiene menos días que el día de pago (ej. Febrero 30 -> 28/29)
        import calendar

        _, ultimo_dia_mes = calendar.monthrange(año, mes)
        if dia_base > ultimo_dia_mes:
            dia_base = ultimo_dia_mes

        fecha_ideal = date(año, mes, dia_base)
        fecha_habil = CalculadoraContratos.obtener_siguiente_dia_habil(fecha_ideal)

        return fecha_habil.day

    @staticmethod
    def resolver_fecha_pago_habil(fecha_pago: int, mes: int, año: int) -> date:
        """
        Retorna un objeto date validado y trasladado al siguiente día hábil en caso
        de fines de semana o festivos, truncando al último día del mes si aplica.
        """
        import calendar

        _, ultimo_dia_mes = calendar.monthrange(año, mes)
        dia_base = fecha_pago if fecha_pago > 0 else 30
        if dia_base > ultimo_dia_mes:
            dia_base = ultimo_dia_mes

        fecha_ideal = date(año, mes, dia_base)
        return CalculadoraContratos.obtener_siguiente_dia_habil(fecha_ideal)

    @staticmethod
    def calcular_dia_pago_arrendamiento(fecha_inicio: Union[date, str]) -> int:
        """
        Arrendamiento: la fecha de pago es EXACTAMENTE el mismo día de la fecha efectiva.

        Args:
            fecha_inicio: Objeto date o string YYYY-MM-DD.

        Returns:
            int: Día exacto de la fecha (1..31).
        """
        fecha_obj = CalculadoraContratos._parsear_fecha(fecha_inicio)
        return fecha_obj.day

    @staticmethod
    def sumar_meses(fecha: Union[date, str], meses: int) -> date:
        """
        Suma N meses a una fecha manejando bordes de fin de mes.

        Convención fin-de-mes: si la fecha origen es el último día de su mes,
        el resultado es el último día del mes destino (30-Nov -> 31-Dic).
        Si no, conserva el día, truncándolo al último día del mes destino si
        hace falta (31-Ene -> 28/29-Feb). Único punto de verdad para lógica
        de renovación.
        """
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha[:10], "%Y-%m-%d").date()
        año = fecha.year + (fecha.month + meses - 1) // 12
        mes = (fecha.month + meses - 1) % 12 + 1
        ultimo_dia_destino = calendar.monthrange(año, mes)[1]
        ultimo_dia_origen = calendar.monthrange(fecha.year, fecha.month)[1]
        if fecha.day == ultimo_dia_origen:
            return fecha.replace(year=año, month=mes, day=ultimo_dia_destino)
        try:
            return fecha.replace(year=año, month=mes)
        except ValueError:
            return fecha.replace(year=año, month=mes, day=ultimo_dia_destino)

    @staticmethod
    def calcular_fecha_inicio_renovacion(fecha_fin_original: str) -> str:
        """
        Calcula la fecha de inicio de la renovación: fecha_fin_original + 1 día.

        Fuente única de verdad para este campo (FR-001, CHK006). NO usar
        `sumar_meses` aquí, que suma meses calendario y rompe casos límite
        (quickstart E5: 2026-12-31 -> 2027-01-01).

        Args:
            fecha_fin_original: Fecha de fin del contrato (YYYY-MM-DD).

        Returns:
            Fecha ISO (YYYY-MM-DD) del día siguiente.
        """
        fecha_fin = datetime.strptime(fecha_fin_original[:10], "%Y-%m-%d").date()
        return (fecha_fin + timedelta(days=1)).isoformat()
