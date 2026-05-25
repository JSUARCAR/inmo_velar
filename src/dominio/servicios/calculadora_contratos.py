"""
Servicio de Dominio: Calculadora de Contratos
Centraliza la lógica de cálculo de duraciones y validaciones de fechas.
"""

from datetime import date, datetime
import calendar
from typing import Union, Tuple, Optional


class CalculadoraContratos:
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
    def calcular_dia_pago_mandato(fecha_inicio: Union[date, str]) -> int:
        """
        Retorna el día de pago para mandato según grupo operativo.
        G1 (1-10) -> 10
        G2 (11-20) -> 20
        G3 (21-31) -> -1 (sentinel: último día del mes)
        """
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio[:10], "%Y-%m-%d").date()
        dia = fecha_inicio.day
        if 1 <= dia <= 10:
            return 10
        elif 11 <= dia <= 20:
            return 20
        else:
            return -1  # Sentinel: Último día del mes

    @staticmethod
    def calcular_ciclo_pago_mandato(fecha_inicio: Union[date, str]) -> Tuple[int, int]:
        """
        Calcula el grupo operativo y día de pago para mandato.
        Reglas Operativas (Nuevo Esquema):
        1-10: Grupo 1, Paga 10
        11-20: Grupo 2, Paga 20
        21-31: Grupo 3, Paga -1 (Último día del mes)
        """
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio[:10], "%Y-%m-%d").date()
        
        dia = fecha_inicio.day
        if 1 <= dia <= 10:
            return 1, 10
        elif 11 <= dia <= 20:
            return 2, 20
        else:
            return 3, -1

    @staticmethod
    def resolver_dia_pago_real(fecha_pago: Optional[int], grupo_operativo: int, mes: int, año: int) -> int:
        """
        Resuelve el día de pago real según el grupo.
        Para G1/G2: retorna el día almacenado (10 o 20).
        Para G3 (fecha_pago=-1 o None): retorna el último día calendario del (mes, año).
        """
        if grupo_operativo == 3 or fecha_pago == -1 or fecha_pago is None:
            import calendar
            return calendar.monthrange(año, mes)[1]
        return fecha_pago if fecha_pago is not None else 1

    @staticmethod
    def calcular_dia_pago_arrendamiento(fecha_inicio: Union[date, str]) -> int:
        """
        Arrendamiento: la fecha de pago es EXACTAMENTE el mismo día de la fecha de inicio.
        """
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio[:10], "%Y-%m-%d").date()
        return fecha_inicio.day

    @staticmethod
    def sumar_meses(fecha: Union[date, str], meses: int) -> date:
        """
        Suma N meses a una fecha manejando bordes (31 -> último día del mes destino).
        Único punto de verdad para lógica de renovación.
        """
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha[:10], "%Y-%m-%d").date()
        año = fecha.year + (fecha.month + meses - 1) // 12
        mes = (fecha.month + meses - 1) % 12 + 1
        try:
            return fecha.replace(year=año, month=mes)
        except ValueError:
            import calendar
            ultimo_dia = calendar.monthrange(año, mes)[1]
            return fecha.replace(year=año, month=mes, day=ultimo_dia)
