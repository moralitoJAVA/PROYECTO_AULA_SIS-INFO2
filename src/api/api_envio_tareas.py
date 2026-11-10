from datetime import datetime

from flask import Blueprint, jsonify, request

from src.servicio.servicio_envio_tareas import ErrorEnvioCorreo, ServicioEnvioTareas

CODIGO_CREADO = 201
CODIGO_NO_ENCONTRADO = 404
CODIGO_ERROR_DE_SERVIDOR = 500


def _fecha(valor):
    return datetime.fromisoformat(valor) if valor else None


def registrar(app, contexto):
    servicio = ServicioEnvioTareas.desdeContexto(contexto)
    api = Blueprint("envio_tareas", __name__)

    @api.errorhandler(ErrorEnvioCorreo)
    def mostrar_error_de_envio(error):
        return jsonify({"error": str(error)}), CODIGO_ERROR_DE_SERVIDOR

    @api.errorhandler(FileNotFoundError)
    def mostrar_no_encontrado(error):
        return jsonify({"error": str(error)}), CODIGO_NO_ENCONTRADO

    def cuerpo():
        return request.get_json(silent=True) or {}

    @api.post("/api/materias")
    def asignar_docente():
        datos = cuerpo()
        return jsonify(servicio.asignarDocente(datos["materia"], datos["correo_docente"])), CODIGO_CREADO

    @api.get("/api/materias/<materia>/docente")
    def docente(materia):
        return jsonify({"materia": materia, "correo_docente": servicio.correoDocente(materia)})

    @api.post("/api/materias/<materia>/tareas/<tarea>/envio")
    def enviar(materia, tarea):
        datos = cuerpo()
        return jsonify(servicio.enviar(
            materia, tarea, datos["estudiante"], datos.get("correo_estudiante"),
            datos.get("adjuntos", []), _fecha(datos.get("fecha_limite")), contexto.ahora())), CODIGO_CREADO

    @api.get("/api/materias/<materia>/tareas/<tarea>/envio")
    def estado(materia, tarea):
        return jsonify(servicio.estadoEnvio(materia, tarea, request.args.get("estudiante")))

    @api.post("/api/materias/<materia>/tareas/<tarea>/reentrega")
    def habilitar_reentrega(materia, tarea):
        return jsonify(servicio.habilitarReentrega(materia, tarea, cuerpo()["estudiante"]))

    app.register_blueprint(api)
