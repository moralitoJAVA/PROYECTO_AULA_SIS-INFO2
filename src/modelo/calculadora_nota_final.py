from decimal import ROUND_HALF_UP
 
from src.constantes import ASISTENCIA, CENTESIMOS, CIEN, COMPONENTES, EXAMENES, PROYECTO, TAREAS
 
 
class CalculadoraNotaFinal:
    def __init__(self, porcentaje, historial_tareas, registro_asistencia, otras_notas=None):
        self._porcentaje = porcentaje
        self._historial = historial_tareas
        self._registro = registro_asistencia
        self._otras = dict(otras_notas or {})
 
    def configurarPesos(self, porcentaje):
        self._porcentaje = porcentaje
 
    def obtenerPesos(self):
        return {componente: self._porcentaje.obtenerPeso(componente) for componente in COMPONENTES}
 
    def _redondear(self, valor):
        return valor.quantize(CENTESIMOS, rounding=ROUND_HALF_UP)
 
    def _notaTareas(self):
        notas = self._historial.obtenerNotas()
        if not notas:
            return None
        sin_penalizacion = sum(n["nota_sobre_100"] for n in notas) / len(notas)
        con_penalizacion = sum(n["nota_sobre_100"] * (CIEN - n["descuento"]) / CIEN for n in notas) / len(notas)
        return self._redondear(con_penalizacion), self._redondear(sin_penalizacion)
 
    def _notas(self):
        asistencia = self._registro.calcularPorcentaje()
        notas = {
            ASISTENCIA: None if asistencia is None else (asistencia, asistencia),
            TAREAS: self._notaTareas(),
        }
        for componente in (EXAMENES, PROYECTO):
            nota = self._otras.get(componente)
            notas[componente] = None if nota is None else (nota, nota)
        return notas
 
    def _aporte(self, componente, nota):
        return nota[0] * self._porcentaje.obtenerPeso(componente) / CIEN
 
    def calcular(self):
        aportes = [self._aporte(c, nota) for c, nota in self._notas().items() if nota is not None]
        if not aportes:
            return None
        return self._redondear(sum(aportes))
