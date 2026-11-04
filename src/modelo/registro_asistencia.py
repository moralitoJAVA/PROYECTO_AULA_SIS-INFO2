from decimal import ROUND_HALF_UP, Decimal

from src.constantes import CENTESIMOS, CIEN, ESTADOS, ESTADOS_QUE_ASISTEN, MINIMO_ASISTENCIA


class RegistroAsistencia:
    def __init__(self, asistencia, minimo=MINIMO_ASISTENCIA):
        self._asistencia = asistencia
        self._minimo = minimo

    def calcularPorcentaje(self):
        evaluables = [estado for estado in self._asistencia.registros.values() if estado != ESTADOS.LICENCIA]
        if not evaluables:
            return None
        asistidos = sum(1 for estado in evaluables if estado in ESTADOS_QUE_ASISTEN)
        porcentaje = Decimal(asistidos) * CIEN / Decimal(len(evaluables))
        return porcentaje.quantize(CENTESIMOS, rounding=ROUND_HALF_UP)

    def hayAlerta(self):
        porcentaje = self.calcularPorcentaje()
        return porcentaje is not None and porcentaje < self._minimo

    def obtenerHistorial(self):
        return sorted(self._asistencia.registros.items())
