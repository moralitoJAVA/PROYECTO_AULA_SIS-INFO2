import importlib
import pkgutil
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, send_from_directory

import src.api
from src.api.contexto import Contexto
from src.constantes import RUTA_BD

CARPETA_WEB = Path(__file__).resolve().parents[2] / "web"
CARPETA_FRONT = Path(__file__).resolve().parents[2] / "front"
PREFIJO_MODULOS_API = "api_"
CODIGO_ERROR_DE_DATOS = 400


def crear_app(ruta_bd=RUTA_BD, ahora=datetime.now, carpeta_pdf=None):
    app = Flask(__name__, static_folder=str(CARPETA_WEB), static_url_path="")
    contexto = Contexto(ruta_bd, ahora, carpeta_pdf)

    @app.errorhandler(ValueError)
    def mostrar_error_de_datos(error):
        return jsonify({"error": str(error)}), CODIGO_ERROR_DE_DATOS

    @app.get("/")
    def inicio():
        return send_from_directory(CARPETA_WEB, "index.html")

    @app.get("/front/<path:archivo>")
    def archivos_front(archivo):
        return send_from_directory(CARPETA_FRONT, archivo)

    for modulo in pkgutil.iter_modules(src.api.__path__):
        if modulo.name.startswith(PREFIJO_MODULOS_API):
            importlib.import_module(f"src.api.{modulo.name}").registrar(app, contexto)
    return app
