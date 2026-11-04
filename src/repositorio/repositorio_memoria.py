from copy import deepcopy

from src.repositorio.repositorio import Repositorio


class RepositorioMemoria(Repositorio):
    def __init__(self):
        self._datos = {}

    def guardar(self, clave, dato):
        self._datos[str(clave)] = deepcopy(dato)

    def obtener(self, clave):
        return deepcopy(self._datos.get(str(clave)))

    def eliminar(self, clave):
        self._datos.pop(str(clave), None)

    def listar(self):
        return deepcopy(self._datos)
