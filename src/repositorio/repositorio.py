from abc import ABC, abstractmethod


class Repositorio(ABC):
    @abstractmethod
    def guardar(self, clave, dato):
        """Guarda un diccionario bajo la clave."""

    @abstractmethod
    def obtener(self, clave):
        """Devuelve el diccionario guardado o None."""

    @abstractmethod
    def eliminar(self, clave):
        """Borra la clave si existe."""

    @abstractmethod
    def listar(self):
        """Devuelve un diccionario clave -> dato."""
