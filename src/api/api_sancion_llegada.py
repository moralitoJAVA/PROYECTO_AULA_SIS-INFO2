from flask import Blueprint, jsonify, request

from src.constantes import MATERIA_POR_DEFECTO
from src.servicio.servicio_sancion_llegada import ServicioSancionLlegada


def registrar(app, contexto):
    servicio = ServicioSancionLlegada.desdeContexto(contexto)
    api = Blueprint("sancion_llegada", __name__)

    def momento_del_pedido(datos):
        return servicio.interpretarMomento(datos.get("fecha"), contexto.ahora())

    @api.post("/api/asistencia/ingreso")
    def registrar_ingreso():
        datos = request.get_json(silent=True) or {}
        materia = datos.get("materia") or MATERIA_POR_DEFECTO
        return jsonify(servicio.registrarIngreso(materia, momento_del_pedido(datos)))

    @api.post("/api/asistencia/evaluar-sancion")
    def evaluar_sancion():
        datos = request.get_json(silent=True) or {}
        return jsonify(servicio.evaluar(momento_del_pedido(datos)))

    @api.get("/api/asistencia/ingresos")
    def listar_ingresos():
        return jsonify(servicio.listarIngresos(request.args.get("materia", MATERIA_POR_DEFECTO), contexto.ahora()))

    app.register_blueprint(api)