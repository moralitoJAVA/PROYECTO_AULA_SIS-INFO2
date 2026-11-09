from datetime import datetime
from decimal import Decimal, InvalidOperation

from src.constantes import (
    CERO,
    MSG_CIERRE_INVALIDO,
    MSG_CONTROL_SIN_LECTURA,
    MSG_CONTROL_SIN_PREGUNTAS,
    MSG_CONTROL_SIN_TITULO,
    MSG_PREGUNTA_OBLIGATORIA,
    MSG_PUNTAJE_CONTROL_INVALIDO,
    MSG_RESPUESTAS_INCOMPLETAS,
    PUNTAJE_CONTROL_POR_DEFECTO,
    PUNTUALIDAD,
)
from src.modelo.pregunta import Pregunta


class ControlLectura:
    def __init__(self, id_control, titulo, id_lectura, preguntas, apertura, cierre,
                 puntaje_maximo=PUNTAJE_CONTROL_POR_DEFECTO):
        if titulo is None or not str(titulo).strip():
            raise ValueError(MSG_CONTROL_SIN_TITULO)
        if id_lectura is None:
            raise ValueError(MSG_CONTROL_SIN_LECTURA)
        if not preguntas:
            raise ValueError(MSG_CONTROL_SIN_PREGUNTAS)
        if cierre <= apertura:
            raise ValueError(MSG_CIERRE_INVALIDO)
        try:
            puntaje_maximo = Decimal(str(puntaje_maximo))
        except InvalidOperation:
            raise ValueError(MSG_PUNTAJE_CONTROL_INVALIDO) from None
        if puntaje_maximo <= CERO:
            raise ValueError(MSG_PUNTAJE_CONTROL_INVALIDO)
        self.id = id_control
        self.titulo = str(titulo).strip()
        self.id_lectura = id_lectura
        self.preguntas = list(preguntas)
        self.apertura = apertura
        self.cierre = cierre
        self.puntaje_maximo = puntaje_maximo

    def estaHabilitado(self, ahora):
        return self.apertura <= ahora <= self.cierre

    def validarRespuestas(self, respuestas):
        if not isinstance(respuestas, list) or len(respuestas) != len(self.preguntas):
            raise ValueError(MSG_RESPUESTAS_INCOMPLETAS)
        for numero, (pregunta, respuesta) in enumerate(zip(self.preguntas, respuestas), start=1):
            if pregunta.obligatoria and not str(respuesta or "").strip():
                raise ValueError(MSG_PREGUNTA_OBLIGATORIA.format(numero=numero))

    def clasificarEnvio(self, fecha_hora_envio):
        return PUNTUALIDAD.A_TIEMPO if fecha_hora_envio <= self.cierre else PUNTUALIDAD.TARDE

    def guardar(self, repositorio):
        repositorio.guardar(self.id, self.aDiccionario())

    def aDiccionario(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "id_lectura": self.id_lectura,
            "preguntas": [pregunta.aDiccionario() for pregunta in self.preguntas],
            "apertura": self.apertura.isoformat(),
            "cierre": self.cierre.isoformat(),
            "puntaje_maximo": str(self.puntaje_maximo),
        }

    @classmethod
    def desdeDiccionario(cls, datos):
        return cls(
            datos["id"],
            datos["titulo"],
            datos["id_lectura"],
            [Pregunta.desdeDiccionario(pregunta) for pregunta in datos["preguntas"]],
            datetime.fromisoformat(datos["apertura"]),
            datetime.fromisoformat(datos["cierre"]),
            datos["puntaje_maximo"],
        )