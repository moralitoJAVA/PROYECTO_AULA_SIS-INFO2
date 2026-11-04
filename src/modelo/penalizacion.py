from src.constantes import FORMATO_MOTIVO, PORCENTAJE_POR_INCUMPLIMIENTO, TOPE


class Penalizacion:
    def __init__(self, porcentaje=PORCENTAJE_POR_INCUMPLIMIENTO, tope=TOPE):
        self._porcentaje = porcentaje
        self._tope = tope

    def aplicarTope(self, valor):
        return min(valor, self._tope)

    def calcularDescuento(self, incumplimientos):
        return self.aplicarTope(self._porcentaje * incumplimientos)

    def guardarMotivo(self, repositorio, clave, incumplen):
        if not incumplen:
            return
        descuento = self.calcularDescuento(len(incumplen))
        motivo = FORMATO_MOTIVO.format(nombres=", ".join(incumplen), descuento=descuento)
        repositorio.guardar(clave, {"motivo": motivo, "descuento": str(descuento)})