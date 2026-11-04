import json

from src.constantes import MSG_TABLA_INVALIDA
from src.repositorio.repositorio import Repositorio


class RepositorioSqlite(Repositorio):
    def __init__(self, conexion, tabla):
        if not tabla.isidentifier():
            raise ValueError(MSG_TABLA_INVALIDA)
        self._conexion = conexion
        self._tabla = tabla
        self._conexion.execute(f"CREATE TABLE IF NOT EXISTS {tabla} (clave TEXT PRIMARY KEY, datos TEXT NOT NULL)")

    def guardar(self, clave, dato):
        self._conexion.execute(
            f"INSERT OR REPLACE INTO {self._tabla} (clave, datos) VALUES (?, ?)",
            (str(clave), json.dumps(dato)),
        )
        self._conexion.commit()

    def obtener(self, clave):
        fila = self._conexion.execute(f"SELECT datos FROM {self._tabla} WHERE clave = ?", (str(clave),)).fetchone()
        return json.loads(fila[0]) if fila else None

    def eliminar(self, clave):
        self._conexion.execute(f"DELETE FROM {self._tabla} WHERE clave = ?", (str(clave),))
        self._conexion.commit()

    def listar(self):
        filas = self._conexion.execute(f"SELECT clave, datos FROM {self._tabla}").fetchall()
        return {clave: json.loads(datos) for clave, datos in filas}
