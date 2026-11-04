from datetime import datetime, timedelta
from decimal import Decimal

from src.constantes import (
    CERO,
    ESTADOS_TAREA,
    FORMATO_CONFIRMACION,
    HORAS_AVISO,
    MSG_FUERA_DE_PLAZO,
    MSG_NOTA_FUERA_DE_RANGO,
    MSG_SIN_ENTREGA,
    MSG_SOLO_ENTREGADAS,
)


class Entrega:
    def __init__(self, tarea, rubrica, archivos=None, enlaces=None):
        self.tarea = tarea
        self.rubrica = rubrica
        self.archivos = list(archivos or [])
        self.enlaces = list(enlaces or [])
        self.fecha_hora_entrega = None
        self.estado = ESTADOS_TAREA.PENDIENTE
        self.nota = None
        self.escala = None
        self.comentarios = None
        self.puntaje_maximo = None
        self.descuento = CERO

    def validar(self, ahora):
        if ahora > self.tarea.fecha_limite:
            raise ValueError(MSG_FUERA_DE_PLAZO)
        if not self.archivos and not self.enlaces:
            raise ValueError(MSG_SIN_ENTREGA)

    def confirmar(self, ahora):
        self.validar(ahora)
        self.fecha_hora_entrega = ahora
        self.estado = ESTADOS_TAREA.ENTREGADA
        return FORMATO_CONFIRMACION.format(fecha=ahora)

    def estaPorVencer(self, ahora):
        if self.estado != ESTADOS_TAREA.PENDIENTE:
            return False
        restante = self.tarea.fecha_limite - ahora
        return timedelta(0) <= restante < timedelta(hours=HORAS_AVISO)

    def registrarCalificacion(self, nota, escala, comentarios):
        if self.estado != ESTADOS_TAREA.ENTREGADA:
            raise ValueError(MSG_SOLO_ENTREGADAS)
        maximo = self.rubrica.obtenerPuntajeMaximo()
        nota = Decimal(str(nota))
        if nota < CERO or nota > maximo:
            raise ValueError(MSG_NOTA_FUERA_DE_RANGO)
        self.nota = nota
        self.escala = escala
        self.comentarios = comentarios
        self.puntaje_maximo = Decimal(str(maximo))
        self.estado = ESTADOS_TAREA.CALIFICADA

    def guardar(self, repositorio):
        repositorio.guardar(self.tarea.numero, self.aDiccionario())

    def aDiccionario(self):
        return {
            "archivos": self.archivos,
            "enlaces": self.enlaces,
            "fecha_hora_entrega": self.fecha_hora_entrega.isoformat() if self.fecha_hora_entrega else None,
            "estado": self.estado.value,
            "nota": None if self.nota is None else str(self.nota),
            "escala": self.escala,
            "comentarios": self.comentarios,
            "puntaje_maximo": None if self.puntaje_maximo is None else str(self.puntaje_maximo),
            "descuento": str(self.descuento),
        }

    @classmethod
    def desdeDiccionario(cls, datos, tarea):
        entrega = cls(tarea, tarea.rubrica, datos["archivos"], datos["enlaces"])
        if datos["fecha_hora_entrega"]:
            entrega.fecha_hora_entrega = datetime.fromisoformat(datos["fecha_hora_entrega"])
        entrega.estado = ESTADOS_TAREA(datos["estado"])
        entrega.nota = None if datos["nota"] is None else Decimal(datos["nota"])
        entrega.escala = datos["escala"]
        entrega.comentarios = datos["comentarios"]
        entrega.puntaje_maximo = None if datos["puntaje_maximo"] is None else Decimal(datos["puntaje_maximo"])
        entrega.descuento = Decimal(datos["descuento"])
        return entrega