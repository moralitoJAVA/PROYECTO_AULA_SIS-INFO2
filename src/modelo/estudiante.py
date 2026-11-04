from src.constantes import MSG_NOMBRE_VACIO


class Estudiante:
    def __init__(self, nombre):
        if nombre is None or not str(nombre).strip():
            raise ValueError(MSG_NOMBRE_VACIO)
        self.nombre = str(nombre).strip()

    def obtenerDatos(self):
        return {"nombre": self.nombre}
