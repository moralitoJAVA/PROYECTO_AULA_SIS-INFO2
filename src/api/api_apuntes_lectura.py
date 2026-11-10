from flask import Blueprint, jsonify, request, send_file

from src.servicio.servicio_apuntes_lectura import ErrorGuardado, ServicioApuntesLectura

CODIGO_CREADO = 201
CODIGO_NO_ENCONTRADO = 404
CODIGO_ERROR_DE_SERVIDOR = 500


def registrar(app, contexto):
    servicio = ServicioApuntesLectura.desdeContexto(contexto)
    api = Blueprint("apuntes_lectura", __name__)

    @api.errorhandler(ErrorGuardado)
    def mostrar_error_de_guardado(error):
        return jsonify({"error": str(error)}), CODIGO_ERROR_DE_SERVIDOR

    def cuerpo():
        return request.get_json(silent=True) or {}

    # ---------- docente: bibliografía, clases y revisión ----------
    @api.get("/api/lecturas")
    def listar_lecturas():
        return jsonify(servicio.listarLecturas())

    @api.post("/api/lecturas")
    def registrar_lectura():
        return jsonify(servicio.registrarLectura(cuerpo())), CODIGO_CREADO

    @api.post("/api/clases-lectura")
    def publicar_clase():
        return jsonify(servicio.publicarClase(cuerpo())), CODIGO_CREADO

    @api.get("/api/clases-lectura/<int:id_clase>/respuestas")
    def respuestas_de_la_clase(id_clase):
        return jsonify(servicio.listarRespuestas(id_clase))

    @api.post("/api/clases-lectura/<int:id_clase>/calificacion")
    def calificar(id_clase):
        datos = cuerpo()
        servicio.calificar(id_clase, datos.get("estudiante"), datos.get("nota"),
                           datos.get("retroalimentacion", ""), datos.get("publicar", False))
        return jsonify({"mensaje": "Calificación guardada"})

    @api.post("/api/clases-lectura/<int:id_clase>/nuevo-intento")
    def nuevo_intento(id_clase):
        servicio.habilitarNuevoIntento(id_clase, cuerpo().get("estudiante"))
        return jsonify({"mensaje": "Nuevo intento habilitado"})

    # ---------- estudiante ----------
    @api.post("/api/clases-lectura/estudiantes")
    def identificar_estudiante():
        return jsonify({"nombre": servicio.registrarEstudiante(cuerpo().get("nombre"))})

    @api.get("/api/clases-lectura")
    def listar_clases():
        return jsonify(servicio.listarClases(request.args.get("estudiante"), contexto.ahora()))

    @api.get("/api/clases-lectura/<int:id_clase>")
    def detalle_clase(id_clase):
        return jsonify(servicio.obtenerClase(id_clase, request.args.get("estudiante"), contexto.ahora()))

    @api.post("/api/clases-lectura/<int:id_clase>/apuntes")
    def crear_apunte(id_clase):
        datos = cuerpo()
        apunte = servicio.agregarApunte(id_clase, datos.get("estudiante"), datos.get("id_lectura"),
                                        datos.get("texto"), contexto.ahora(), datos.get("id_fuente"))
        return jsonify(apunte), CODIGO_CREADO

    @api.put("/api/clases-lectura/<int:id_clase>/apuntes/<int:id_apunte>")
    def editar_apunte(id_clase, id_apunte):
        datos = cuerpo()
        return jsonify(servicio.editarApunte(id_clase, datos.get("estudiante"), id_apunte, datos.get("texto"),
                                             contexto.ahora(), datos.get("id_lectura"), datos.get("id_fuente")))

    @api.post("/api/clases-lectura/<int:id_clase>/fuentes")
    def crear_fuente(id_clase):
        datos = cuerpo()
        return jsonify(servicio.agregarFuente(id_clase, datos.get("estudiante"), datos.get("titulo"),
                                              datos.get("enlace"), contexto.ahora())), CODIGO_CREADO

    @api.put("/api/clases-lectura/<int:id_clase>/fuentes/<int:id_fuente>")
    def editar_fuente(id_clase, id_fuente):
        datos = cuerpo()
        return jsonify(servicio.editarFuente(id_clase, datos.get("estudiante"), id_fuente, datos.get("titulo"),
                                             datos.get("enlace")))

    @api.post("/api/clases-lectura/<int:id_clase>/dudas")
    def crear_duda(id_clase):
        datos = cuerpo()
        return jsonify(servicio.agregarDuda(id_clase, datos.get("estudiante"), datos.get("texto"),
                                            contexto.ahora())), CODIGO_CREADO

    @api.put("/api/clases-lectura/<int:id_clase>/dudas/<int:id_duda>")
    def editar_duda(id_clase, id_duda):
        datos = cuerpo()
        return jsonify(servicio.editarDuda(id_clase, datos.get("estudiante"), id_duda, datos.get("texto"),
                                           contexto.ahora()))

    @api.post("/api/clases-lectura/<int:id_clase>/respuesta")
    def enviar_respuesta(id_clase):
        datos = cuerpo()
        return jsonify(servicio.enviarRespuesta(id_clase, datos.get("estudiante"), datos.get("titulo"),
                                                datos.get("respuesta"), contexto.ahora()))

    @api.get("/api/clases-lectura/<int:id_clase>/respuesta/pdf")
    def descargar_pdf(id_clase):
        try:
            ruta = servicio.rutaPdf(id_clase, request.args.get("estudiante"))
        except FileNotFoundError as error:
            return jsonify({"error": str(error)}), CODIGO_NO_ENCONTRADO
        return send_file(ruta, mimetype="application/pdf", download_name=ruta.name)

    app.register_blueprint(api)