from decimal import Decimal
 
from src.constantes import (
    CERO,
    CLAVE_PORCENTAJES,
    COMPONENTES,
    MSG_COMPONENTE_DESCONOCIDO,
    MSG_PESO_NEGATIVO,
    MSG_PESOS_NO_SUMAN_100,
    TOTAL_PESOS,
)
 
 
class Porcentaje:
    def __init__(self, pesos=None):
        self._pesos = {componente: CERO for componente in COMPONENTES}
        for componente, peso in (pesos or {}).items():
            if componente not in COMPONENTES:
                raise ValueError(MSG_COMPONENTE_DESCONOCIDO)
            self._pesos[componente] = Decimal(str(peso))
 
    def obtenerPeso(self, componente):
        if componente not in COMPONENTES:
            raise ValueError(MSG_COMPONENTE_DESCONOCIDO)
        return self._pesos[componente]
 
    def validarSuma(self):
        if any(peso < CERO for peso in self._pesos.values()):
            raise ValueError(MSG_PESO_NEGATIVO)
        if sum(self._pesos.values()).compare(TOTAL_PESOS) != 0:
            raise ValueError(MSG_PESOS_NO_SUMAN_100)
 
    def guardar(self, repositorio):
        self.validarSuma()
        repositorio.guardar(CLAVE_PORCENTAJES, {c: str(p) for c, p in self._pesos.items()})
