from datetime import date

from flask import Blueprint, jsonify, request

from src.constantes import MATERIA_POR_DEFECTO, TABLA_ASISTENCIAS
from src.servicio.servicio_asistencia import ServicioAsistencia


def registrar(app, contexto):
    servicio = ServicioAsistencia(contexto.repositorio(TABLA_ASISTENCIAS))
    api = Blueprint("asistencia", __name__)

    def materia():
        return request.args.get("materia", MATERIA_POR_DEFECTO)

    @api.post("/api/asistencia")
    def registrar_asistencia():
        datos = request.get_json()
        fecha = date.fromisoformat(datos["fecha"])
        if servicio.abrirSesion(datos["materia"], fecha).asistencia.existePara(fecha):
            resumen = servicio.editarAsistencia(datos["materia"], fecha, datos["estado"])
        else:
            resumen = servicio.registrarAsistencia(datos["materia"], fecha, datos["estado"])
        return jsonify({"resumen": resumen})

    @api.get("/api/asistencia/panel")
    def panel():
        porcentaje = servicio.obtenerPorcentaje(materia())
        return jsonify({
            "resumen": servicio.obtenerResumen(materia()),
            "historial": [[fecha.isoformat(), estado.value] for fecha, estado in servicio.obtenerHistorial(materia())],
            "porcentaje": None if porcentaje is None else str(porcentaje),
            "alerta": servicio.hayAlerta(materia()),
        })

    app.register_blueprint(api)