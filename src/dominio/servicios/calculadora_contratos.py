"""
Servicio de Dominio: Calculadora de Contratos
Centraliza la lógica de cálculo de duraciones y validaciones de fechas.
"""

from datetime import date, datetime
import calendar
from typing import Union, Tuple


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

        # Caso base: Mismo mes
        if total == 0:
            if d1 == 1 and d2 >= last_day_fin - 1:
                return 1
            if d2 >= d1 - 1 and d1 > 1:
                # Ej: 15-Ene a 14-Ene? No pasa por el if fecha_fin < fecha_inicio
                # Pero 15-Ene a 15-Ene es 0 meses.
                return 0
            return 0

        # Caso meses distintos
        if d2 >= d1 - 1:
            # Ej: 15-Ene a 14-Feb. total=1. 14 >= 14. Retorna 1.
            # Ej: 01-Ene a 31-Dic. total=11. 31 >= 0.
            # Si inició el 1, sumamos 1 para completar el ciclo.
            return total + (1 if d1 == 1 else 0)
        else:
            # No alcanzó el día umbral
            # Ej: 15-Ene a 10-Feb. total=1. 10 < 14. Retorna 0.
            # Excepción: si terminó el último día del mes (ej. 31-Ene a 28-Feb)
            if d2 == last_day_fin and d1 >= last_day_fin:
                return total
            
            # Si inició el 1 y no terminó el último día, pero llegó cerca
            if d1 == 1 and d2 < last_day_fin - 1:
                return total # Ej: 1-Ene a 15-Feb. total=1. Retorna 1.

            return total - 1 if total > 0 else 0

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
    def calcular_ciclo_pago_arrendamiento(fecha_inicio: Union[date, str]) -> int:
        """
        Calcula el día de pago para arrendamiento (mismo día de inicio).
        """
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio[:10], "%Y-%m-%d").date()
        return fecha_inicio.day

    @staticmethod
    def calcular_ciclo_pago_mandato(fecha_inicio: Union[date, str]) -> Tuple[int, int]:
        """
        Calcula el grupo operativo y día de pago para mandato.
        Reglas:
        1-5: Grupo 1, Paga 10
        6-15: Grupo 2, Paga 20
        16-24: Grupo 3, Paga 30
        25-31: Grupo 4, Paga 10 (sig mes)
        """
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio[:10], "%Y-%m-%d").date()
        
        dia = fecha_inicio.day
        if 1 <= dia <= 5:
            return 1, 10
        elif 6 <= dia <= 15:
            return 2, 20
        elif 16 <= dia <= 24:
            return 3, 30
        else:
            return 4, 10
