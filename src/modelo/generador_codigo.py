from src.constantes import CODIGO_MATERIA, CODIGO_PARCIAL, FORMATO_CODIGO


class GeneradorCodigo:
    def __init__(self, ultimo_numero=0):
        self._ultimo = ultimo_numero

    def siguienteNumero(self):
        self._ultimo += 1
        return self._ultimo

    def generar(self, numero):
        return FORMATO_CODIGO.format(materia=CODIGO_MATERIA, parcial=CODIGO_PARCIAL, numero=numero)