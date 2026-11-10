from src.constantes import MSG_LECTURA_SIN_RECURSO, MSG_LECTURA_SIN_TITULO


def _limpiar(texto):
    return str(texto).strip() if texto is not None else ""


class Lectura:
    """Texto de la bibliografía que envía el docente: título y archivo o enlace (autor opcional)."""

    def __init__(self, id_lectura, titulo, autor=None, archivo=None, enlace=None):
        if not _limpiar(titulo):
            raise ValueError(MSG_LECTURA_SIN_TITULO)
        if not _limpiar(archivo) and not _limpiar(enlace):
            raise ValueError(MSG_LECTURA_SIN_RECURSO)
        self.id = id_lectura
        self.titulo = _limpiar(titulo)
        self.autor = _limpiar(autor) or None
        self.archivo = _limpiar(archivo) or None
        self.enlace = _limpiar(enlace) or None

    def guardar(self, repositorio):
        repositorio.guardar(self.id, self.aDiccionario())

    def aDiccionario(self):
        return {"id": self.id, "titulo": self.titulo, "autor": self.autor,
                "archivo": self.archivo, "enlace": self.enlace}

    @classmethod
    def desdeDiccionario(cls, datos):
        return cls(datos["id"], datos["titulo"], datos.get("autor"), datos.get("archivo"), datos.get("enlace"))