from datetime import datetime
from decimal import Decimal

from src.constantes import (
    CERO,
    ESTADOS_RESPUESTA,
    FORMATO_CONFIRMACION_RESPUESTA,
    MSG_CAMPOS_OBLIGATORIOS,
    MSG_CLASE_NO_INICIADA,
    MSG_NOTA_RESPUESTA_FUERA_DE_RANGO,
    MSG_RESPUESTA_YA_ENVIADA,
    MSG_SOLO_RESPONDIDOS,
    PUNTUALIDAD,
)

CAMPO_TITULO = "título"
CAMPO_RESPUESTA = "respuesta"


class RespuestaClase:
    """Respuesta de un estudiante a la pregunta planteada en clase: título derivado + respuesta, entregada en PDF."""

    def __init__(self, id_clase, estudiante):
        self.id_clase = id_clase
        self.estudiante = estudiante
        self.titulo = None
        self.respuesta = None
        self.archivo_pdf = None
        self.fecha_hora_envio = None
        self.puntualidad = None
        self.estado = ESTADOS_RESPUESTA.PENDIENTE
        self.intento_habilitado = False
        self.intentos = 0
        self.nota = None
        self.retroalimentacion = None
        self.calificacion_publicada = False

    def puedeResponder(self, clase, ahora):
        if self.intento_habilitado:
            return True
        return self.estado == ESTADOS_RESPUESTA.PENDIENTE and clase.haComenzado(ahora)

    @staticmethod
    def validarCampos(titulo, respuesta):
        faltan = [campo for campo, valor in ((CAMPO_TITULO, titulo), (CAMPO_RESPUESTA, respuesta))
                  if not str(valor or "").strip()]
        if faltan:
            raise ValueError(MSG_CAMPOS_OBLIGATORIOS.format(campos=" y ".join(faltan)))

    def conEnvio(self, clase, titulo, respuesta, ahora):
        """Devuelve la respuesta ya enviada SIN modificar esta: así un fallo al guardar no deja nada a medias."""
        if self.estado == ESTADOS_RESPUESTA.RESPONDIDO and not self.intento_habilitado:
            raise ValueError(MSG_RESPUESTA_YA_ENVIADA)
        if not self.puedeResponder(clase, ahora):
            raise ValueError(MSG_CLASE_NO_INICIADA)
        self.validarCampos(titulo, respuesta)
        nueva = RespuestaClase(self.id_clase, self.estudiante)
        nueva.titulo = str(titulo).strip()
        nueva.respuesta = str(respuesta).strip()
        nueva.fecha_hora_envio = ahora
        nueva.puntualidad = clase.clasificarEnvio(ahora)
        nueva.estado = ESTADOS_RESPUESTA.RESPONDIDO
        nueva.intentos = self.intentos + 1          # el nuevo intento reemplaza al anterior por completo
        return nueva

    def mensajeConfirmacion(self):
        return FORMATO_CONFIRMACION_RESPUESTA.format(fecha=self.fecha_hora_envio)

    def habilitarNuevoIntento(self):
        self.intento_habilitado = True

    def calificar(self, nota, retroalimentacion, publicar, puntaje_maximo):
        if self.estado != ESTADOS_RESPUESTA.RESPONDIDO:
            raise ValueError(MSG_SOLO_RESPONDIDOS)
        try:
            nota = Decimal(str(nota))
        except ArithmeticError:
            raise ValueError(MSG_NOTA_RESPUESTA_FUERA_DE_RANGO) from None
        if not nota.is_finite() or nota < CERO or nota > puntaje_maximo:
            raise ValueError(MSG_NOTA_RESPUESTA_FUERA_DE_RANGO)
        self.nota = nota
        self.retroalimentacion = (retroalimentacion or "").strip()
        self.calificacion_publicada = bool(publicar)

    def estadoVisible(self):
        """Estado que ve el docente en la revisión: Pendiente, Respondido o Tarde."""
        if self.estado == ESTADOS_RESPUESTA.PENDIENTE:
            return ESTADOS_RESPUESTA.PENDIENTE.value
        return PUNTUALIDAD.TARDE.value if self.puntualidad == PUNTUALIDAD.TARDE else ESTADOS_RESPUESTA.RESPONDIDO.value

    def aDiccionario(self):
        return {
            "id_clase": self.id_clase,
            "estudiante": self.estudiante,
            "titulo": self.titulo,
            "respuesta": self.respuesta,
            "archivo_pdf": self.archivo_pdf,
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
        r = cls(datos["id_clase"], datos["estudiante"])
        r.titulo = datos["titulo"]
        r.respuesta = datos["respuesta"]
        r.archivo_pdf = datos["archivo_pdf"]
        if datos["fecha_hora_envio"]:
            r.fecha_hora_envio = datetime.fromisoformat(datos["fecha_hora_envio"])
        r.puntualidad = PUNTUALIDAD(datos["puntualidad"]) if datos["puntualidad"] else None
        r.estado = ESTADOS_RESPUESTA(datos["estado"])
        r.intento_habilitado = datos["intento_habilitado"]
        r.intentos = datos["intentos"]
        r.nota = None if datos["nota"] is None else Decimal(datos["nota"])
        r.retroalimentacion = datos["retroalimentacion"]
        r.calificacion_publicada = datos["calificacion_publicada"]
        return r