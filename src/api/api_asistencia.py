from datetime import date, datetime
from flask import Blueprint, jsonify, request
from src.constantes import MATERIA_POR_DEFECTO, TABLA_ASISTENCIAS
from src.servicio.servicio_asistencia import ServicioAsistencia
from src.modelo.sancion_llegada import SancionLlegada

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

    @api.post("/api/asistencia/evaluar-sancion")
    def evaluar_sancion():
        sancionador = SancionLlegada()
        datos = request.get_json() or {}
        
        fecha_str = datos.get("fecha")
        if fecha_str:
            fecha_obj = datetime.fromisoformat(fecha_str)
        else:
            fecha_obj = datetime.now()
            
        dia_semana = fecha_obj.weekday() # 1: Martes, 2: Miércoles, 4: Viernes
        hora_ingreso = fecha_obj.time()
        
        estado_sancion = sancionador.evaluar_ingreso(dia_semana, hora_ingreso)
        
        return jsonify({
            "estado": estado_sancion,
            "hora_ingreso": fecha_obj.strftime("%H:%M:%S"),
            "fecha_completa": fecha_obj.strftime("%d/%m/%Y %H:%M:%S"),
            "dia_semana": dia_semana
        }), 200

    app.register_blueprint(api)