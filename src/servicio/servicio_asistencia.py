from datetime import date

from src.constantes import ESTADOS, MSG_ESTADO_INVALIDO, MSG_NO_ES_DIA_DE_CLASE
from src.modelo.asistencia import Asistencia
from src.modelo.registro_asistencia import RegistroAsistencia
from src.modelo.sesion import Sesion


class ServicioAsistencia:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    def _convertirEstado(self, valor):
        try:
            return ESTADOS(valor)
        except ValueError:
            raise ValueError(MSG_ESTADO_INVALIDO) from None

    def _cargar(self, materia):
        asistencia = Asistencia()
        guardado = self._repositorio.obtener(materia) or {}
        for fecha, estado in guardado.items():
            asistencia.registrar(date.fromisoformat(fecha), ESTADOS(estado))
        return asistencia

    def _guardar(self, materia, asistencia):
        self._repositorio.guardar(materia, {fecha.isoformat(): estado.value for fecha, estado in asistencia.registros.items()})

    def abrirSesion(self, materia, fecha):
        sesion = Sesion(materia, fecha, self._cargar(materia))
        if not sesion.esDiaDeClase():
            raise ValueError(MSG_NO_ES_DIA_DE_CLASE)
        return sesion

    def registrarAsistencia(self, materia, fecha, estado):
        sesion = self.abrirSesion(materia, fecha)
        sesion.asistencia.registrar(fecha, self._convertirEstado(estado))
        self._guardar(materia, sesion.asistencia)
        return sesion.obtenerResumen()

    def editarAsistencia(self, materia, fecha, estado):
        sesion = self.abrirSesion(materia, fecha)
        sesion.asistencia.editar(fecha, self._convertirEstado(estado))
        self._guardar(materia, sesion.asistencia)
        return sesion.obtenerResumen()

    def obtenerResumen(self, materia):
        return Sesion(materia, None, self._cargar(materia)).obtenerResumen()

    def crearRegistro(self, materia):
        return RegistroAsistencia(self._cargar(materia))

    def obtenerHistorial(self, materia):
        return self.crearRegistro(materia).obtenerHistorial()

    def obtenerPorcentaje(self, materia):
        return self.crearRegistro(materia).calcularPorcentaje()

    def hayAlerta(self, materia):
        return self.crearRegistro(materia).hayAlerta()
