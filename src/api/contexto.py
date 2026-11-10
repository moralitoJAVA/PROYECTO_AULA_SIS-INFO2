import sqlite3
from datetime import datetime
from pathlib import Path

from src.constantes import CARPETA_PDF_POR_DEFECTO
from src.repositorio.almacen_pdf import AlmacenPdf
from src.repositorio.repositorio_sqlite import RepositorioSqlite


class Contexto:
    def __init__(self, ruta_bd, ahora=datetime.now, carpeta_pdf=None):
        self.conexion = sqlite3.connect(ruta_bd, check_same_thread=False)
        self.ahora = ahora
        self.carpeta_pdf = Path(carpeta_pdf) if carpeta_pdf else Path(ruta_bd).parent / CARPETA_PDF_POR_DEFECTO

    def repositorio(self, tabla):
        return RepositorioSqlite(self.conexion, tabla)

    def almacenPdf(self):
        return AlmacenPdf(self.carpeta_pdf)