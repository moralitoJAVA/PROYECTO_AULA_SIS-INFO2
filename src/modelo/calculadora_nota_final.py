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
 
    def _notas(self):
        notas = [n["nota_sobre_100"] for n in self._historial.obtenerNotas()]
        return {
            ASISTENCIA: self._registro.calcularPorcentaje(),
            TAREAS: sum(notas) / len(notas),
            EXAMENES: self._otras[EXAMENES],
            PROYECTO: self._otras[PROYECTO],
        }
 
    def calcular(self):
        total = sum(nota * self._porcentaje.obtenerPeso(c) / CIEN for c, nota in self._notas().items())
        return total.quantize(CENTESIMOS, rounding=ROUND_HALF_UP)
