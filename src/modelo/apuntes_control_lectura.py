from src.constantes import (
    MSG_APUNTE_DOS_ORIGENES,
    MSG_APUNTE_NO_EXISTE,
    MSG_APUNTE_SIN_LECTURA,
    MSG_APUNTE_VACIO,
    MSG_DUDA_NO_EXISTE,
    MSG_DUDA_VACIA,
    MSG_FUENTE_NO_EXISTE,
    MSG_FUENTE_SIN_TITULO,
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
    """Cuaderno de un estudiante en una clase: fuentes que buscó, apuntes por fuente y dudas para la explicación.

    Un apunte pertenece a un texto de la bibliografía del docente (id_lectura) o a una fuente propia del estudiante (id_fuente).
    """

    def __init__(self, id_clase, estudiante):
        self.id_clase = id_clase
        self.estudiante = estudiante
        self.apuntes = []
        self.dudas = []
        self.fuentes = []

    # ----- fuentes propias -----
    def agregarFuente(self, titulo, enlace, ahora):
        fuente = {"id": _siguiente(self.fuentes), "titulo": _texto(titulo, MSG_FUENTE_SIN_TITULO),
                  "enlace": str(enlace or "").strip() or None, "creado": ahora.isoformat()}
        self.fuentes.append(fuente)
        return dict(fuente)

    def editarFuente(self, id_fuente, titulo, enlace):
        fuente = _buscar(self.fuentes, id_fuente, MSG_FUENTE_NO_EXISTE)
        fuente["titulo"] = _texto(titulo, MSG_FUENTE_SIN_TITULO)
        fuente["enlace"] = str(enlace or "").strip() or None
        return dict(fuente)

    def tituloDeFuente(self, id_fuente):
        return _buscar(self.fuentes, id_fuente, MSG_FUENTE_NO_EXISTE)["titulo"]

    # ----- apuntes -----
    def _validarOrigen(self, id_lectura, id_fuente):
        if id_lectura is None and id_fuente is None:
            raise ValueError(MSG_APUNTE_SIN_LECTURA)
        if id_lectura is not None and id_fuente is not None:
            raise ValueError(MSG_APUNTE_DOS_ORIGENES)
        if id_fuente is not None:
            _buscar(self.fuentes, id_fuente, MSG_FUENTE_NO_EXISTE)

    def agregarApunte(self, id_lectura, texto, ahora, id_fuente=None):
        self._validarOrigen(id_lectura, id_fuente)
        apunte = {"id": _siguiente(self.apuntes), "id_lectura": id_lectura, "id_fuente": id_fuente,
                  "texto": _texto(texto, MSG_APUNTE_VACIO),
                  "creado": ahora.isoformat(), "actualizado": ahora.isoformat()}
        self.apuntes.append(apunte)
        return dict(apunte)

    def editarApunte(self, id_apunte, texto, ahora, id_lectura=None, id_fuente=None):
        apunte = _buscar(self.apuntes, id_apunte, MSG_APUNTE_NO_EXISTE)
        apunte["texto"] = _texto(texto, MSG_APUNTE_VACIO)
        if id_lectura is not None or id_fuente is not None:
            self._validarOrigen(id_lectura, id_fuente)
            apunte["id_lectura"], apunte["id_fuente"] = id_lectura, id_fuente
        apunte["actualizado"] = ahora.isoformat()
        return dict(apunte)

    # ----- dudas -----
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
                "apuntes": [dict(a) for a in self.apuntes], "dudas": [dict(d) for d in self.dudas],
                "fuentes": [dict(f) for f in self.fuentes]}

    @classmethod
    def desdeDiccionario(cls, datos):
        cuaderno = cls(datos["id_clase"], datos["estudiante"])
        cuaderno.apuntes = [{"id_fuente": None, **a} for a in datos["apuntes"]]
        cuaderno.dudas = [dict(d) for d in datos["dudas"]]
        cuaderno.fuentes = [dict(f) for f in datos.get("fuentes", [])]
        return cuaderno
