from flask import Blueprint, jsonify, request

from src.constantes import TABLA_APUNTES
from src.modelo.gestor_apuntes import GestorApuntes
from src.servicio.servicio_tareas import ServicioTareas

CODIGO_CREADO = 201


def _fila(item):
    return {**item, "fecha_limite": item["fecha_limite"].isoformat(), "estado": item["estado"].value,
            "nota": None if item["nota"] is None else str(item["nota"]),
            "descuento": str(item["descuento"]),
            "nota_final": None if item["nota_final"] is None else str(item["nota_final"])}


def registrar(app, contexto):
    servicio = ServicioTareas.desdeContexto(contexto)
    apuntes = GestorApuntes(contexto.repositorio(TABLA_APUNTES))
    api = Blueprint("tareas", __name__)

    @api.get("/api/tareas")
    def listar_tareas():
        filas = [_fila(i) for i in servicio.listarPorEstado(request.args.get("estado"))]
        por_vencer = servicio.tareasPorVencer(contexto.ahora())
        return jsonify({"tareas": filas, "por_vencer": por_vencer})

    @api.get("/api/tareas/<int:numero>")
    def detalle(numero):
        return jsonify(servicio.obtenerDetalle(numero))

    @api.post("/api/tareas/<int:numero>/entrega")
    def entregar(numero):
        datos = request.get_json()
        mensaje = servicio.entregar(numero, datos.get("archivos", []), datos.get("enlaces", []), contexto.ahora())
        return jsonify({"mensaje": mensaje})

    @api.post("/api/tareas/<int:numero>/entrega-equipo")
    def entregar_por_equipo(numero):
        datos = request.get_json()
        return jsonify(servicio.entregarPorEquipo(
            numero, datos["integrantes"], datos["estudiante"], datos.get("incumplen", []),
            datos.get("archivos", []), datos.get("enlaces", []), contexto.ahora()))

    @api.post("/api/tareas/<int:numero>/calificacion")
    def calificar(numero):
        datos = request.get_json()
        servicio.registrarCalificacion(numero, datos["nota"], datos["escala"], datos.get("comentarios", ""))
        return jsonify({"mensaje": "Calificación registrada"})

    @api.get("/api/apuntes")
    def listar_apuntes():
        return jsonify(apuntes.listarApuntes(request.args.get("vinculo")))

    @api.post("/api/apuntes")
    def crear_apunte():
        datos = request.get_json()
        return jsonify({"clave": apuntes.crear(datos["vinculo"], datos["texto"])}), CODIGO_CREADO

    @api.put("/api/apuntes/<clave>")
    def editar_apunte(clave):
        apuntes.editar(clave, request.get_json()["texto"])
        return jsonify({"clave": clave})

    @api.delete("/api/apuntes/<clave>")
    def borrar_apunte(clave):
        apuntes.borrar(clave)
        return jsonify({"clave": clave})

    app.register_blueprint(api)