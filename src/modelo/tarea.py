from datetime import datetime

from src.constantes import (
    DIAS_DE_CLASE,
    ESTADOS_TAREA,
    HORA_LIMITE,
    MSG_DIA_NO_HABIL,
    MSG_FECHA_PASADA,
    MSG_NUMERO_INVALIDO,
    MSG_SIN_GUIA,
    MSG_TITULO_VACIO,
    TIPOS_TAREA,
)
from src.modelo.rubrica import Rubrica


class Tarea:
    def __init__(self, numero, titulo, instrucciones, fecha_limite,
                 tipo=TIPOS_TAREA.INDIVIDUAL, ruta_adjunto=None, codigo=None, rubrica=None):
        if not isinstance(numero, int) or isinstance(numero, bool) or numero <= 0:
            raise ValueError(MSG_NUMERO_INVALIDO)
        if titulo is None or not str(titulo).strip():
            raise ValueError(MSG_TITULO_VACIO)
        self.numero = numero
        self.titulo = str(titulo).strip()
        self.instrucciones = instrucciones
        self.fecha_limite = fecha_limite
        self.tipo = tipo
        self.ruta_adjunto = ruta_adjunto
        self.codigo = codigo
        self.rubrica = rubrica
        self.estado = None

    def validarFecha(self, ahora):
        if self.fecha_limite <= ahora:
            raise ValueError(MSG_FECHA_PASADA)

    def validarDiaHabil(self):
        es_dia_de_clase = self.fecha_limite.weekday() in DIAS_DE_CLASE
        if not es_dia_de_clase or self.fecha_limite.time() != HORA_LIMITE:
            raise ValueError(MSG_DIA_NO_HABIL)

    def adjuntarGuia(self, ruta):
        if ruta is None or not str(ruta).strip():
            raise ValueError(MSG_SIN_GUIA)
        self.ruta_adjunto = str(ruta).strip()

    def registrar(self, ahora):
        self.validarFecha(ahora)
        self.validarDiaHabil()
        if not self.ruta_adjunto:
            raise ValueError(MSG_SIN_GUIA)
        self.estado = ESTADOS_TAREA.REGISTRADA

    def guardar(self, repositorio):
        repositorio.guardar(self.numero, self.aDiccionario())

    def aDiccionario(self):
        return {
            "numero": self.numero,
            "titulo": self.titulo,
            "instrucciones": self.instrucciones,
            "fecha_limite": self.fecha_limite.isoformat(),
            "tipo": self.tipo.value,
            "ruta_adjunto": self.ruta_adjunto,
            "codigo": self.codigo,
            "estado": self.estado.value if self.estado else None,
            "criterios": self.rubrica.aDiccionario() if self.rubrica else None,
            "tamano_equipo": None,
        }

    @classmethod
    def desdeDiccionario(cls, datos):
        rubrica = Rubrica.desdeDiccionario(datos["criterios"]) if datos["criterios"] is not None else None
        tarea = cls(
            datos["numero"],
            datos["titulo"],
            datos["instrucciones"],
            datetime.fromisoformat(datos["fecha_limite"]),
            ruta_adjunto=datos["ruta_adjunto"],
            codigo=datos["codigo"],
            rubrica=rubrica,
        )
        tarea.estado = ESTADOS_TAREA(datos["estado"]) if datos["estado"] else None
        return tarea