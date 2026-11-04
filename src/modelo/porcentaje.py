from decimal import Decimal
 
from src.constantes import CERO, CLAVE_PORCENTAJES, COMPONENTES, MSG_COMPONENTE_DESCONOCIDO
 
 
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
 
    def guardar(self, repositorio):
        repositorio.guardar(CLAVE_PORCENTAJES, {c: str(p) for c, p in self._pesos.items()})
