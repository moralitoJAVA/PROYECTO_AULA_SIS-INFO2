from flask import Blueprint, jsonify, request
 
from src.constantes import MATERIA_POR_DEFECTO, TABLA_ASISTENCIAS, TABLA_PORCENTAJES
from src.modelo.calculadora_nota_final import CalculadoraNotaFinal
from src.modelo.porcentaje import Porcentaje
from src.servicio.servicio_asistencia import ServicioAsistencia
from src.servicio.servicio_tareas import ServicioTareas
 
 
def _texto(valor):
    return None if valor is None else str(valor)
 
 
def registrar(app, contexto):
    repo_porcentajes = contexto.repositorio(TABLA_PORCENTAJES)
    asistencia = ServicioAsistencia(contexto.repositorio(TABLA_ASISTENCIAS))
    tareas = ServicioTareas.desdeContexto(contexto)
    api = Blueprint("nota_final", __name__)
 
    @api.get("/api/pesos")
    def obtener_pesos():
        return jsonify(Porcentaje.cargar(repo_porcentajes).aDiccionario())
 
    @api.put("/api/pesos")
    def guardar_pesos():
        porcentaje = Porcentaje(request.get_json())
        porcentaje.guardar(repo_porcentajes)
        return jsonify(porcentaje.aDiccionario())
 
    @api.get("/api/nota-final")
    def nota_final():
        calculadora = CalculadoraNotaFinal(
            Porcentaje.cargar(repo_porcentajes),
            tareas.crearHistorial(),
            asistencia.crearRegistro(request.args.get("materia", MATERIA_POR_DEFECTO)),
        )
        desglose = calculadora.obtenerDesglose()
        componentes = {
            nombre: {clave: (valor if isinstance(valor, bool) else _texto(valor)) for clave, valor in dato.items()}
            for nombre, dato in desglose["componentes"].items()
        }
        return jsonify({"componentes": componentes, "nota_final": _texto(desglose["nota_final"]),
                        "parcial": desglose["parcial"]})
 
    app.register_blueprint(api)
