from decimal import Decimal

from src.constantes import CERO, MSG_CRITERIO_VACIO, MSG_PUNTAJE_INVALIDO, MSG_RUBRICA_VACIA


class Rubrica:
    def __init__(self):
        self._criterios = {}

    @property
    def criterios(self):
        return dict(self._criterios)

    def agregarCriterio(self, nombre, puntaje):
        if nombre is None or not str(nombre).strip():
            raise ValueError(MSG_CRITERIO_VACIO)
        puntaje = Decimal(str(puntaje))
        if puntaje <= CERO:
            raise ValueError(MSG_PUNTAJE_INVALIDO)
        self._criterios[str(nombre).strip()] = puntaje

    def obtenerPuntajeMaximo(self):
        if not self._criterios:
            raise ValueError(MSG_RUBRICA_VACIA)
        return sum(self._criterios.values())

    def aDiccionario(self):
        return {nombre: str(puntaje) for nombre, puntaje in self._criterios.items()}

    @classmethod
    def desdeDiccionario(cls, datos):
        rubrica = cls()
        for nombre, puntaje in datos.items():
            rubrica.agregarCriterio(nombre, puntaje)
        return rubrica 