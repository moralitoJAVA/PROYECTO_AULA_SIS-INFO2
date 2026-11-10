from flask import Blueprint, jsonify, request

from src.constantes import MSG_CON_ERRORES_INVALIDO
from src.servicio.servicio_revision_tareas import ServicioRevisionTareas

MSG_CUERPO_INVALIDO = "El cuerpo de la solicitud debe ser un objeto JSON"


def _cuerpo():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        raise ValueError(MSG_CUERPO_INVALIDO)
    return datos


def registrar(app, contexto):
    servicio = ServicioRevisionTareas.desdeContexto(contexto)
    api = Blueprint("revision_tareas", __name__)

    def materia():
        return request.args.get("materia")

    @api.get("/api/revision-tareas")
    def listar_revisiones():
        return jsonify({"revisiones": servicio.listarRevisiones(materia(), contexto.ahora())})

    @api.get("/api/revision-tareas/<int:numero>")
    def estado_revision(numero):
        return jsonify(servicio.obtenerEstado(numero, materia(), contexto.ahora()))

    @api.get("/api/revision-tareas/<int:numero>/historial")
    def historial_revision(numero):
        return jsonify(servicio.obtenerHistorial(numero, materia()))

    @api.post("/api/revision-tareas/<int:numero>/revision")
    def registrar_revision(numero):
        datos = _cuerpo()
        if "con_errores" not in datos:
            raise ValueError(MSG_CON_ERRORES_INVALIDO)
        return jsonify(servicio.registrarRevision(
            numero, datos["con_errores"], datos.get("observaciones", ""), contexto.ahora(), materia()))

    @api.post("/api/revision-tareas/<int:numero>/reentrega")
    def enviar_reentrega(numero):
        datos = _cuerpo()
        return jsonify(servicio.solicitarReentrega(
            numero, datos.get("archivos", []), datos.get("enlaces", []), contexto.ahora(), materia()))

    app.register_blueprint(api)
