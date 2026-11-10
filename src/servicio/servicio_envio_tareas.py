from src.constantes import (
    FORMATO_CONFIRMACION_ENVIO,
    MSG_ENVIO_NO_EXISTE,
    MSG_ERROR_ENVIO_CORREO,
    MSG_MATERIA_SIN_DOCENTE,
    MSG_REENTREGA_NO_HABILITADA,
    TABLA_ENVIOS_TAREA,
    TABLA_MATERIAS,
)
from src.modelo.envio_tarea import EnvioTarea
from src.servicio.enviador_correo import EnviadorCorreo


class ErrorEnvioCorreo(Exception):
    """El correo no se pudo enviar: la tarea no quedó registrada como entregada."""


class ServicioEnvioTareas:
    def __init__(self, repo_materias, repo_envios, enviador=None):
        self._repo_materias = repo_materias
        self._repo_envios = repo_envios
        self._enviador = enviador or EnviadorCorreo()

    @classmethod
    def desdeContexto(cls, contexto):
        return cls(contexto.repositorio(TABLA_MATERIAS), contexto.repositorio(TABLA_ENVIOS_TAREA))

    # ----- docente asignado a la materia (criterio 1) -----
    def asignarDocente(self, materia, correo_docente):
        self._repo_materias.guardar(materia, {"materia": materia, "correo_docente": correo_docente})
        return {"materia": materia, "correo_docente": correo_docente}

    def correoDocente(self, materia):
        datos = self._repo_materias.obtener(materia)
        if datos is None or not datos.get("correo_docente"):
            raise ValueError(MSG_MATERIA_SIN_DOCENTE)
        return datos["correo_docente"]

    # ----- envío de la tarea -----
    @staticmethod
    def _clave(materia, tarea, estudiante):
        return f"{materia}|{tarea}|{estudiante}"

    def _envioPrevio(self, materia, tarea, estudiante):
        datos = self._repo_envios.obtener(self._clave(materia, tarea, estudiante))
        return EnvioTarea.desdeDiccionario(datos) if datos else None

    def enviar(self, materia, tarea, estudiante, correo_estudiante, adjuntos, fecha_limite, ahora):
        correo_docente = self.correoDocente(materia)
        base = EnvioTarea(materia, tarea, estudiante, correo_estudiante)
        previo = self._envioPrevio(materia, tarea, base.estudiante)
        if previo and not previo.reentrega_habilitada:          # criterio 9: solo con reentrega habilitada
            raise ValueError(MSG_REENTREGA_NO_HABILITADA)
        enviado = base.conEnvio(adjuntos, fecha_limite, ahora)   # valida adjuntos y clasifica
        try:
            self._enviador.enviar(correo_docente, enviado.asunto(), enviado.cuerpo(), enviado.adjuntos)
        except Exception as error:                               # criterio 7: si falla, no se registra
            raise ErrorEnvioCorreo(MSG_ERROR_ENVIO_CORREO) from error
        self._repo_envios.guardar(self._clave(materia, tarea, base.estudiante), enviado.aDiccionario())
        return {
            "mensaje": FORMATO_CONFIRMACION_ENVIO.format(
                docente=correo_docente, fecha=enviado.fecha_hora_envio, estado=enviado.puntualidad.value),
            "estado": enviado.estado.value,
            "puntualidad": enviado.puntualidad.value,
            "fecha_hora_envio": enviado.fecha_hora_envio.isoformat(),
        }

    def habilitarReentrega(self, materia, tarea, estudiante):
        clave = self._clave(materia, tarea, EnvioTarea(materia, tarea, estudiante, "").estudiante)
        datos = self._repo_envios.obtener(clave)
        if datos is None:
            raise ValueError(MSG_ENVIO_NO_EXISTE)
        envio = EnvioTarea.desdeDiccionario(datos)
        envio.habilitarReentrega()
        self._repo_envios.guardar(clave, envio.aDiccionario())
        return envio.aDiccionario()

    def estadoEnvio(self, materia, tarea, estudiante):
        envio = self._envioPrevio(materia, tarea, EnvioTarea(materia, tarea, estudiante, "").estudiante)
        if envio is None:
            raise ValueError(MSG_ENVIO_NO_EXISTE)
        return envio.aDiccionario()
