from collections import Counter

from src.constantes import DIAS_DE_CLASE, ESTADOS, FORMATO_LICENCIAS, FORMATO_RESUMEN


class Sesion:
    def __init__(self, materia, fecha, asistencia):
        self.materia = materia
        self.fecha = fecha
        self.asistencia = asistencia

    def esDiaDeClase(self):
        return self.fecha.weekday() in DIAS_DE_CLASE

    def listarAsistencia(self):
        return sorted(self.asistencia.registros.items())

    def obtenerResumen(self):
        conteo = Counter(self.asistencia.registros.values())
        resumen = FORMATO_RESUMEN.format(
            presentes=conteo[ESTADOS.PRESENTE],
            atrasos=conteo[ESTADOS.ATRASO],
            ausentes=conteo[ESTADOS.AUSENTE],
        )
        if conteo[ESTADOS.LICENCIA]:
            resumen += FORMATO_LICENCIAS.format(licencias=conteo[ESTADOS.LICENCIA])
        return resumen
