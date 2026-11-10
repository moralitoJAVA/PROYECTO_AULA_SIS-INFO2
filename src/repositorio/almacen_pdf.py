from pathlib import Path


class AlmacenPdf:
    """Guarda en disco los PDF de respuesta. No contiene reglas de negocio."""

    def __init__(self, carpeta):
        self._carpeta = Path(carpeta)

    def guardar(self, nombre, contenido):
        self._carpeta.mkdir(parents=True, exist_ok=True)
        destino = self._carpeta / nombre
        temporal = destino.with_suffix(".tmp")
        temporal.write_bytes(contenido)
        temporal.replace(destino)       # el PDF aparece completo o no aparece
        return nombre

    def ruta(self, nombre):
        ruta = self._carpeta / nombre
        return ruta if ruta.is_file() else None

    def eliminar(self, nombre):
        if nombre:
            (self._carpeta / nombre).unlink(missing_ok=True)