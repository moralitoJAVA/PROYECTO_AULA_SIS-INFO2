import sqlite3
from datetime import datetime

from src.repositorio.repositorio_sqlite import RepositorioSqlite


class Contexto:
    def __init__(self, ruta_bd, ahora=datetime.now):
        self.conexion = sqlite3.connect(ruta_bd, check_same_thread=False)
        self.ahora = ahora

    def repositorio(self, tabla):
        return RepositorioSqlite(self.conexion, tabla)
