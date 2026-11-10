from datetime import datetime

from src.constantes import (
    MSG_CLASE_CIERRE_INVALIDO,
    MSG_CLASE_SIN_BIBLIOGRAFIA,
    MSG_CLASE_SIN_TEMA,
    PUNTUALIDAD,
    VENTANA_CLASE,
)


class ClaseLectura:
    """Clase con su bibliografía y el plazo para responder la pregunta que el docente plantea en clase.

    La pregunta NO forma parte de la clase: es aleatoria y la plantea el docente en voz alta.
    """

    def __init__(self, id_clase, tema, inicio, cierre_respuesta, ids_lecturas, investigacion_libre=False):
        if tema is None or not str(tema).strip():
            raise ValueError(MSG_CLASE_SIN_TEMA)
        if not ids_lecturas and not investigacion_libre:
            raise ValueError(MSG_CLASE_SIN_BIBLIOGRAFIA)
        if cierre_respuesta <= inicio:
            raise ValueError(MSG_CLASE_CIERRE_INVALIDO)
        self.id = id_clase
        self.tema = str(tema).strip()
        self.inicio = inicio
        self.cierre_respuesta = cierre_respuesta
        self.ids_lecturas = list(dict.fromkeys(ids_lecturas))
        self.investigacion_libre = bool(investigacion_libre)      # el docente no envía textos: cada estudiante busca sus fuentes

    def incluyeLectura(self, id_lectura):
        return id_lectura in self.ids_lecturas

    def haComenzado(self, ahora):
        return ahora >= self.inicio

    def ventana(self, ahora):
        if ahora < self.inicio:
            return VENTANA_CLASE.ANTES_DE_CLASE
        return VENTANA_CLASE.DENTRO_DEL_PLAZO if ahora <= self.cierre_respuesta else VENTANA_CLASE.PLAZO_VENCIDO

    def clasificarEnvio(self, fecha_hora_envio):
        return PUNTUALIDAD.A_TIEMPO if fecha_hora_envio <= self.cierre_respuesta else PUNTUALIDAD.TARDE

    def guardar(self, repositorio):
        repositorio.guardar(self.id, self.aDiccionario())

    def aDiccionario(self):
        return {"id": self.id, "tema": self.tema, "inicio": self.inicio.isoformat(),
                "cierre_respuesta": self.cierre_respuesta.isoformat(), "ids_lecturas": self.ids_lecturas,
                "investigacion_libre": self.investigacion_libre}

    @classmethod
    def desdeDiccionario(cls, datos):
        return cls(datos["id"], datos["tema"], datetime.fromisoformat(datos["inicio"]),
                   datetime.fromisoformat(datos["cierre_respuesta"]), datos["ids_lecturas"],
                   datos.get("investigacion_libre", False))