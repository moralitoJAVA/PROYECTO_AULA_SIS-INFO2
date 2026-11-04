from src.constantes import MSG_NOMBRE_VACIO


class Estudiante:
    def __init__(self, nombre):
        if nombre is None or not str(nombre).strip():
            raise ValueError(MSG_NOMBRE_VACIO)
        self.nombre = str(nombre).strip()

    def obtenerDatos(self):
        return {"nombre": self.nombre}

    def obtenerHistorial(self, registro_asistencia):
        return registro_asistencia.obtenerHistorial()

    def obtenerDesglose(self, calculadora):
        return calculadora.obtenerDesglose()
