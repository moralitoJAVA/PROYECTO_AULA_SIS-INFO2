from src.constantes import (
    MSG_APUNTE_NO_EXISTE,
    MSG_APUNTE_SIN_LECTURA,
    MSG_APUNTE_VACIO,
    MSG_DUDA_NO_EXISTE,
    MSG_DUDA_VACIA,
)


def _texto(valor, mensaje):
    if valor is None or not str(valor).strip():
        raise ValueError(mensaje)
    return str(valor).strip()


def _siguiente(items):
    return max([item["id"] for item in items] + [0]) + 1


def _buscar(items, id_item, mensaje):
    for item in items:
        if item["id"] == id_item:
            return item
    raise ValueError(mensaje)


class ApuntesControlLectura:
    """Cuaderno de un estudiante en una clase: apuntes por texto de la bibliografía y dudas para después de la explicación."""

    def __init__(self, id_clase, estudiante):
        self.id_clase = id_clase
        self.estudiante = estudiante
        self.apuntes = []
        self.dudas = []

    def agregarApunte(self, id_lectura, texto, ahora):
        if id_lectura is None:
            raise ValueError(MSG_APUNTE_SIN_LECTURA)
        apunte = {"id": _siguiente(self.apuntes), "id_lectura": id_lectura,
                  "texto": _texto(texto, MSG_APUNTE_VACIO),
                  "creado": ahora.isoformat(), "actualizado": ahora.isoformat()}
        self.apuntes.append(apunte)
        return dict(apunte)

    def editarApunte(self, id_apunte, texto, ahora, id_lectura=None):
        apunte = _buscar(self.apuntes, id_apunte, MSG_APUNTE_NO_EXISTE)
        apunte["texto"] = _texto(texto, MSG_APUNTE_VACIO)
        if id_lectura is not None:
            apunte["id_lectura"] = id_lectura
        apunte["actualizado"] = ahora.isoformat()
        return dict(apunte)

    def agregarDuda(self, texto, ahora):
        duda = {"id": _siguiente(self.dudas), "texto": _texto(texto, MSG_DUDA_VACIA),
                "creado": ahora.isoformat(), "actualizado": ahora.isoformat()}
        self.dudas.append(duda)
        return dict(duda)

    def editarDuda(self, id_duda, texto, ahora):
        duda = _buscar(self.dudas, id_duda, MSG_DUDA_NO_EXISTE)
        duda["texto"] = _texto(texto, MSG_DUDA_VACIA)
        duda["actualizado"] = ahora.isoformat()
        return dict(duda)

    def aDiccionario(self):
        return {"id_clase": self.id_clase, "estudiante": self.estudiante,
                "apuntes": [dict(a) for a in self.apuntes], "dudas": [dict(d) for d in self.dudas]}

    @classmethod
    def desdeDiccionario(cls, datos):
        cuaderno = cls(datos["id_clase"], datos["estudiante"])
        cuaderno.apuntes = [dict(a) for a in datos["apuntes"]]
        cuaderno.dudas = [dict(d) for d in datos["dudas"]]
        return cuaderno