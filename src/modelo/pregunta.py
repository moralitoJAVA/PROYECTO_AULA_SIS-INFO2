from src.constantes import MSG_PREGUNTA_VACIA


class Pregunta:
    def __init__(self, enunciado, obligatoria=True):
        if enunciado is None or not str(enunciado).strip():
            raise ValueError(MSG_PREGUNTA_VACIA)
        self.enunciado = str(enunciado).strip()
        self.obligatoria = bool(obligatoria)

    def aDiccionario(self):
        return {"enunciado": self.enunciado, "obligatoria": self.obligatoria}

    @classmethod
    def desdeDiccionario(cls, datos):
        return cls(datos["enunciado"], datos.get("obligatoria", True))