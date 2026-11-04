"""Servidor web y API del proyecto, construido solo con la biblioteca estándar."""

import json
import sqlite3
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETA_FRONT = RAIZ / "front"
ARCHIVO_BD = Path(__file__).resolve().parent / "datos.db"
ARCHIVO_ESQUEMA = Path(__file__).resolve().parent / "esquema.sql"


def inicializar_base_datos():
    """Crea las tablas definidas en el esquema cuando el servidor inicia."""
    with sqlite3.connect(ARCHIVO_BD) as conexion:
        conexion.executescript(ARCHIVO_ESQUEMA.read_text(encoding="utf-8"))


class Manejador(SimpleHTTPRequestHandler):
    """Sirve la interfaz estática y las rutas JSON que comienzan con /api/."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(CARPETA_FRONT), **kwargs)

    def enviar_json(self, datos, estado=HTTPStatus.OK):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(estado)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        if self.path == "/api/estado":
            self.enviar_json({"estado": "activo", "base_datos": "SQLite"})
            return
        if self.path.startswith("/api/"):
            self.enviar_json({"error": "Ruta de API no encontrada."}, HTTPStatus.NOT_FOUND)
            return
        super().do_GET()


def ejecutar():
    inicializar_base_datos()
    servidor = ThreadingHTTPServer(("", 8000), Manejador)
    print("Servidor disponible en http://localhost:8000")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    ejecutar()
