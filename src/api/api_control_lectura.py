from flask import Blueprint, jsonify, request

from src.servicio.servicio_control_lectura import ErrorGuardado, ServicioControlLectura

CODIGO_CREADO = 201
CODIGO_ERROR_DE_SERVIDOR = 500


def registrar(app, contexto):
    servicio = ServicioControlLectura.desdeContexto(contexto)
    api = Blueprint("control_lectura", __name__)

    @api.errorhandler(ErrorGuardado)
    def mostrar_error_de_guardado(error):
        return jsonify({"error": str(error)}), CODIGO_ERROR_DE_SERVIDOR

    # ---------- docente ----------
    @api.get("/api/lecturas")
    def listar_lecturas():
        return jsonify(servicio.listarLecturas())

    @api.post("/api/lecturas")
    def registrar_lectura():
        return jsonify(servicio.registrarLectura(request.get_json() or {})), CODIGO_CREADO

    @api.post("/api/controles-lectura")
    def publicar_control():
        return jsonify(servicio.publicarControl(request.get_json() or {})), CODIGO_CREADO

    @api.get("/api/controles-lectura/<int:id_control>/revision")
    def revision(id_control):
        return jsonify(servicio.listarRevision(id_control))

    @api.post("/api/controles-lectura/<int:id_control>/calificacion")
    def calificar(id_control):
        datos = request.get_json() or {}
        servicio.calificar(id_control, datos.get("estudiante"), datos.get("nota"),
                           datos.get("retroalimentacion", ""), datos.get("publicar", False))
        return jsonify({"mensaje": "Calificación guardada"})

    @api.post("/api/controles-lectura/<int:id_control>/nuevo-intento")
    def nuevo_intento(id_control):
        servicio.habilitarNuevoIntento(id_control, (request.get_json() or {}).get("estudiante"))
        return jsonify({"mensaje": "Nuevo intento habilitado"})

    # ---------- estudiante ----------
    @api.get("/api/controles-lectura")
    def listar_controles():
        return jsonify(servicio.listarControles(request.args.get("estudiante"), contexto.ahora()))

    @api.get("/api/controles-lectura/<int:id_control>")
    def detalle_control(id_control):
        return jsonify(servicio.obtenerControl(id_control, request.args.get("estudiante"), contexto.ahora()))

    @api.post("/api/controles-lectura/estudiantes")
    def identificar_estudiante():
        return jsonify({"nombre": servicio.registrarEstudiante((request.get_json() or {}).get("nombre"))})

    @api.post("/api/controles-lectura/<int:id_control>/respuestas")
    def enviar_respuestas(id_control):
        datos = request.get_json() or {}
        return jsonify(servicio.enviarRespuestas(id_control, datos.get("estudiante"),
                                                 datos.get("respuestas"), contexto.ahora()))

    app.register_blueprint(api)