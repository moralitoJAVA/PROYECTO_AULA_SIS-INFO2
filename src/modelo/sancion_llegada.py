from datetime import date, datetime, time, timedelta

from src.constantes import (
    DIAS_DE_CLASE,
    HORA_FIN_CLASE,
    HORA_INICIO_CLASE,
    HORA_LIMITE_SIN_SANCION,
    SANCION_DEBE_FRUTA,
    SANCION_DIA_SIN_CLASES,
    SANCION_FUERA_DE_HORARIO,
    SANCION_PUNTUAL,
)


class SancionLlegada:
    """HU1: compara la hora de ingreso con el límite de las 07:00 y decide si el estudiante debe fruta."""

    def __init__(self):
        self.dias_clase = DIAS_DE_CLASE
        self.hora_inicio = HORA_INICIO_CLASE
        self.hora_fin = HORA_FIN_CLASE
        self.hora_limite_sin_sancion = HORA_LIMITE_SIN_SANCION

    def evaluar_ingreso(self, dia_semana: int, hora_ingreso: time) -> str:
        if dia_semana not in self.dias_clase:
            return SANCION_DIA_SIN_CLASES
        if not (self.hora_inicio <= hora_ingreso <= self.hora_fin):
            return SANCION_FUERA_DE_HORARIO
        if hora_ingreso > self.hora_limite_sin_sancion:
            return SANCION_DEBE_FRUTA
        return SANCION_PUNTUAL

    def evaluar_momento(self, momento: datetime) -> str:
        return self.evaluar_ingreso(momento.weekday(), momento.time())

    def proxima_clase(self, fecha: date) -> date:
        """Primer martes, miércoles o viernes posterior a la fecha: la clase en la que se lleva la fruta."""
        dia = fecha + timedelta(days=1)
        while dia.weekday() not in self.dias_clase:
            dia += timedelta(days=1)
        return dia