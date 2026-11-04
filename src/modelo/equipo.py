from src.constantes import (
    CERO,
    MSG_INTEGRANTE_REPETIDO,
    MSG_INTEGRANTE_VACIO,
    MSG_NO_ES_INTEGRANTE,
    MSG_SIN_ENTREGA_EQUIPO,
)
from src.modelo.penalizacion import Penalizacion


class Equipo:
    def __init__(self, penalizacion=None):
        self.integrantes = []
        self.entrega = None
        self._penalizacion = penalizacion or Penalizacion()

    def agregarIntegrante(self, nombre):
        if nombre is None or not str(nombre).strip():
            raise ValueError(MSG_INTEGRANTE_VACIO)
        nombre = str(nombre).strip()
        if nombre in self.integrantes:
            raise ValueError(MSG_INTEGRANTE_REPETIDO)
        self.integrantes.append(nombre)

    def entregarPorGrupo(self, entrega, integrante, ahora):
        if integrante not in self.integrantes:
            raise ValueError(MSG_NO_ES_INTEGRANTE)
        mensaje = entrega.confirmar(ahora)
        self.entrega = entrega
        return mensaje

    def repartirResultado(self, incumplen=()):
        if self.entrega is None:
            raise ValueError(MSG_SIN_ENTREGA_EQUIPO)
        if any(nombre not in self.integrantes for nombre in incumplen):
            raise ValueError(MSG_NO_ES_INTEGRANTE)
        descuento = self._penalizacion.calcularDescuento(len(incumplen))
        return {
            nombre: {"entrega": self.entrega, "descuento": descuento if nombre in incumplen else CERO}
            for nombre in self.integrantes
        }