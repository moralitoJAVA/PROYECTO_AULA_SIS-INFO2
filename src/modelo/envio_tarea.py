from datetime import datetime

from src.constantes import (
    ASUNTO_ENVIO_TAREA,
    ESTADOS_ENVIO,
    FORMATO_FECHA_HORA_ENVIO,
    MSG_SIN_ADJUNTOS,
    PUNTUALIDAD_ENTREGA,
)
from src.modelo.estudiante import Estudiante


class EnvioTarea:
    """Envío de una tarea de un estudiante al correo del docente. Dominio puro: valida, clasifica y arma el correo."""

    def __init__(self, materia, tarea, estudiante, correo_estudiante):
        self.materia = materia
        self.tarea = tarea
        self.estudiante = Estudiante(estudiante).nombre
        self.correo_estudiante = correo_estudiante
        self.adjuntos = []
        self.fecha_hora_envio = None
        self.puntualidad = None
        self.estado = ESTADOS_ENVIO.PENDIENTE
        self.reentrega_habilitada = False

    @staticmethod
    def _validarAdjuntos(adjuntos):
        if not adjuntos:
            raise ValueError(MSG_SIN_ADJUNTOS)
        return [dict(adjunto) for adjunto in adjuntos]

    def conEnvio(self, adjuntos, fecha_limite, ahora):
        """Devuelve el envío ya realizado SIN tocar este: un fallo al enviar no deja nada a medias."""
        nuevo = EnvioTarea(self.materia, self.tarea, self.estudiante, self.correo_estudiante)
        nuevo.adjuntos = self._validarAdjuntos(adjuntos)
        nuevo.fecha_hora_envio = ahora
        nuevo.puntualidad = self._clasificar(fecha_limite, ahora)
        nuevo.estado = ESTADOS_ENVIO.ENTREGADA
        return nuevo

    @staticmethod
    def _clasificar(fecha_limite, ahora):
        if fecha_limite is None or ahora <= fecha_limite:
            return PUNTUALIDAD_ENTREGA.A_TIEMPO
        return PUNTUALIDAD_ENTREGA.TARDE

    def asunto(self):
        return ASUNTO_ENVIO_TAREA.format(materia=self.materia, tarea=self.tarea, estudiante=self.estudiante)

    def cuerpo(self):
        fecha_hora = FORMATO_FECHA_HORA_ENVIO.format(fecha=self.fecha_hora_envio)
        return (
            f"Estudiante: {self.estudiante}\n"
            f"Correo/código del estudiante: {self.correo_estudiante}\n"
            f"Materia: {self.materia}\n"
            f"Tarea: {self.tarea}\n"
            f"Fecha y hora de envío: {fecha_hora}\n"
            f"Puntualidad: {self.puntualidad.value}"
        )

    def habilitarReentrega(self):
        self.reentrega_habilitada = True

    def aDiccionario(self):
        return {
            "materia": self.materia,
            "tarea": self.tarea,
            "estudiante": self.estudiante,
            "correo_estudiante": self.correo_estudiante,
            "adjuntos": self.adjuntos,
            "fecha_hora_envio": self.fecha_hora_envio.isoformat() if self.fecha_hora_envio else None,
            "puntualidad": self.puntualidad.value if self.puntualidad else None,
            "estado": self.estado.value,
            "reentrega_habilitada": self.reentrega_habilitada,
        }

    @classmethod
    def desdeDiccionario(cls, datos):
        envio = cls(datos["materia"], datos["tarea"], datos["estudiante"], datos["correo_estudiante"])
        envio.adjuntos = datos.get("adjuntos", [])
        if datos.get("fecha_hora_envio"):
            envio.fecha_hora_envio = datetime.fromisoformat(datos["fecha_hora_envio"])
        envio.puntualidad = PUNTUALIDAD_ENTREGA(datos["puntualidad"]) if datos.get("puntualidad") else None
        envio.estado = ESTADOS_ENVIO(datos["estado"])
        envio.reentrega_habilitada = datos.get("reentrega_habilitada", False)
        return envio
