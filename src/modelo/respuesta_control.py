from datetime import datetime
from decimal import Decimal

from src.constantes import (
    CERO,
    ESTADO_REVISION_TARDE,
    ESTADOS_CONTROL,
    FORMATO_CONFIRMACION_CONTROL,
    MSG_CONTROL_NO_HABILITADO,
    MSG_CONTROL_YA_ENVIADO,
    MSG_NOTA_CONTROL_FUERA_DE_RANGO,
    MSG_SOLO_RESPONDIDOS,
    PUNTUALIDAD,
)


class RespuestaControl:
    """Envío de un estudiante a un control de lectura (un registro por estudiante y control)."""

    def __init__(self, id_control, estudiante):
        self.id_control = id_control
        self.estudiante = estudiante
        self.id_lectura = None
        self.titulo_lectura = None
        self.respuestas = []
        self.fecha_hora_envio = None
        self.puntualidad = None
        self.estado = ESTADOS_CONTROL.PENDIENTE
        self.intento_habilitado = False
        self.intentos = 0
        self.nota = None
        self.retroalimentacion = None
        self.calificacion_publicada = False

    def puedeResponder(self, control, ahora):
        if self.estado == ESTADOS_CONTROL.RESPONDIDO and not self.intento_habilitado:
            return False
        return self.intento_habilitado or control.estaHabilitado(ahora)

    def enviar(self, control, lectura, respuestas, ahora):
        if self.estado == ESTADOS_CONTROL.RESPONDIDO and not self.intento_habilitado:
            raise ValueError(MSG_CONTROL_YA_ENVIADO)
        if not self.puedeResponder(control, ahora):
            raise ValueError(MSG_CONTROL_NO_HABILITADO)
        control.validarRespuestas(respuestas)
        self.id_lectura = lectura.id
        self.titulo_lectura = lectura.titulo
        self.respuestas = [str(respuesta or "").strip() for respuesta in respuestas]
        self.fecha_hora_envio = ahora
        self.puntualidad = control.clasificarEnvio(ahora)
        self.estado = ESTADOS_CONTROL.RESPONDIDO
        self.intento_habilitado = False
        self.intentos += 1
        self.nota = None
        self.retroalimentacion = None
        self.calificacion_publicada = False
        return FORMATO_CONFIRMACION_CONTROL.format(fecha=ahora)

    def habilitarNuevoIntento(self):
        self.intento_habilitado = True

    def calificar(self, nota, retroalimentacion, publicar, puntaje_maximo):
        if self.estado != ESTADOS_CONTROL.RESPONDIDO:
            raise ValueError(MSG_SOLO_RESPONDIDOS)
        try:
            nota = Decimal(str(nota))
        except ArithmeticError:
            raise ValueError(MSG_NOTA_CONTROL_FUERA_DE_RANGO) from None
        if not nota.is_finite() or nota < CERO or nota > puntaje_maximo:
            raise ValueError(MSG_NOTA_CONTROL_FUERA_DE_RANGO)
        self.nota = nota
        self.retroalimentacion = (retroalimentacion or "").strip()
        self.calificacion_publicada = bool(publicar)

    def estadoRevision(self):
        if self.estado == ESTADOS_CONTROL.PENDIENTE:
            return ESTADOS_CONTROL.PENDIENTE.value
        if self.puntualidad == PUNTUALIDAD.TARDE:
            return ESTADO_REVISION_TARDE
        return ESTADOS_CONTROL.RESPONDIDO.value

    def aDiccionario(self):
        return {
            "id_control": self.id_control,
            "estudiante": self.estudiante,
            "id_lectura": self.id_lectura,
            "titulo_lectura": self.titulo_lectura,
            "respuestas": self.respuestas,
            "fecha_hora_envio": self.fecha_hora_envio.isoformat() if self.fecha_hora_envio else None,
            "puntualidad": self.puntualidad.value if self.puntualidad else None,
            "estado": self.estado.value,
            "intento_habilitado": self.intento_habilitado,
            "intentos": self.intentos,
            "nota": None if self.nota is None else str(self.nota),
            "retroalimentacion": self.retroalimentacion,
            "calificacion_publicada": self.calificacion_publicada,
        }

    @classmethod
    def desdeDiccionario(cls, datos):
        respuesta = cls(datos["id_control"], datos["estudiante"])
        respuesta.id_lectura = datos["id_lectura"]
        respuesta.titulo_lectura = datos["titulo_lectura"]
        respuesta.respuestas = datos["respuestas"]
        if datos["fecha_hora_envio"]:
            respuesta.fecha_hora_envio = datetime.fromisoformat(datos["fecha_hora_envio"])
        respuesta.puntualidad = PUNTUALIDAD(datos["puntualidad"]) if datos["puntualidad"] else None
        respuesta.estado = ESTADOS_CONTROL(datos["estado"])
        respuesta.intento_habilitado = datos["intento_habilitado"]
        respuesta.intentos = datos["intentos"]
        respuesta.nota = None if datos["nota"] is None else Decimal(datos["nota"])
        respuesta.retroalimentacion = datos["retroalimentacion"]
        respuesta.calificacion_publicada = datos["calificacion_publicada"]
        return respuesta