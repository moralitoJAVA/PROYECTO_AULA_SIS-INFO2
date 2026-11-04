from datetime import datetime

from src.constantes import (
    ESTADOS_TAREA,
    MSG_ES_GRUPAL,
    MSG_ES_INDIVIDUAL,
    MSG_TAMANO_DEL_EQUIPO,
    MSG_TAREA_NO_EXISTE,
    MSG_YA_ENTREGADA,
    TABLA_ENTREGAS,
    TABLA_EQUIPOS,
    TABLA_PENALIZACIONES,
    TABLA_TAREAS,
    TIPOS_TAREA,
)
from src.modelo.entrega import Entrega
from src.modelo.equipo import Equipo
from src.modelo.generador_codigo import GeneradorCodigo
from src.modelo.historial_tareas import HistorialTareas
from src.modelo.penalizacion import Penalizacion
from src.modelo.rubrica import Rubrica
from src.modelo.tarea_grupal import TareaGrupal
from src.modelo.tarea_individual import TareaIndividual


class ServicioTareas:
    def __init__(self, repo_tareas, repo_entregas, repo_equipos, repo_penalizaciones):
        self._repo_tareas = repo_tareas
        self._repo_entregas = repo_entregas
        self._repo_equipos = repo_equipos
        self._repo_penalizaciones = repo_penalizaciones

    @classmethod
    def desdeContexto(cls, contexto):
        return cls(
            contexto.repositorio(TABLA_TAREAS),
            contexto.repositorio(TABLA_ENTREGAS),
            contexto.repositorio(TABLA_EQUIPOS),
            contexto.repositorio(TABLA_PENALIZACIONES),
        )

    def _construirTarea(self, datos):
        clase = TareaGrupal if datos["tipo"] == TIPOS_TAREA.GRUPAL.value else TareaIndividual
        return clase.desdeDiccionario(datos)

    def _tareas(self):
        return [self._construirTarea(datos) for datos in self._repo_tareas.listar().values()]

    def _tarea(self, numero):
        datos = self._repo_tareas.obtener(numero)
        if datos is None:
            raise ValueError(MSG_TAREA_NO_EXISTE)
        return self._construirTarea(datos)

    def _entrega(self, tarea):
        datos = self._repo_entregas.obtener(tarea.numero)
        if datos is None:
            return Entrega(tarea, tarea.rubrica)
        return Entrega.desdeDiccionario(datos, tarea)

    def _entregas(self):
        entregas = {}
        for tarea in self._tareas():
            if self._repo_entregas.obtener(tarea.numero) is not None:
                entregas[tarea.numero] = self._entrega(tarea)
        return entregas

    def crearHistorial(self):
        return HistorialTareas(self._tareas(), self._entregas())

    def listarPorEstado(self, estado=None):
        filtro = ESTADOS_TAREA(estado) if estado else None
        return self.crearHistorial().listarPorEstado(filtro)

    def obtenerHistorial(self):
        return self.listarPorEstado()

    def obtenerDetalle(self, numero):
        tarea = self._tarea(numero)
        entrega = self._entrega(tarea)
        return {"tarea": tarea.aDiccionario(), "entrega": entrega.aDiccionario(),
                "puntaje_maximo": str(tarea.rubrica.obtenerPuntajeMaximo()),
                "equipo": self._repo_equipos.obtener(numero),
                "penalizacion": self._repo_penalizaciones.obtener(numero)}

    def tareasPorVencer(self, ahora):
        return [t.numero for t in self._tareas() if self._entrega(t).estaPorVencer(ahora)]

    def entregar(self, numero, archivos, enlaces, ahora):
        tarea = self._tarea(numero)
        if tarea.tipo == TIPOS_TAREA.GRUPAL:
            raise ValueError(MSG_ES_GRUPAL)
        entrega = self._entrega(tarea)
        if entrega.estado != ESTADOS_TAREA.PENDIENTE:
            raise ValueError(MSG_YA_ENTREGADA)
        entrega.archivos, entrega.enlaces = list(archivos), list(enlaces)
        mensaje = entrega.confirmar(ahora)
        entrega.guardar(self._repo_entregas)
        return mensaje

    def entregarPorEquipo(self, numero, integrantes, estudiante, incumplen, archivos, enlaces, ahora):
        tarea = self._tarea(numero)
        if tarea.tipo != TIPOS_TAREA.GRUPAL:
            raise ValueError(MSG_ES_INDIVIDUAL)
        if len(integrantes) != tarea.tamano_equipo:
            raise ValueError(MSG_TAMANO_DEL_EQUIPO.format(tamano=tarea.tamano_equipo))
        entrega = self._entrega(tarea)
        if entrega.estado != ESTADOS_TAREA.PENDIENTE:
            raise ValueError(MSG_YA_ENTREGADA)
        entrega.archivos, entrega.enlaces = list(archivos), list(enlaces)
        penalizacion = tarea.penalizacion or Penalizacion()
        equipo = Equipo(penalizacion)
        for nombre in integrantes:
            equipo.agregarIntegrante(nombre)
        mensaje = equipo.entregarPorGrupo(entrega, estudiante, ahora)
        resultado = equipo.repartirResultado(incumplen)
        entrega.descuento = resultado[estudiante]["descuento"]
        entrega.guardar(self._repo_entregas)
        self._repo_equipos.guardar(numero, {"integrantes": equipo.integrantes, "incumplen": list(incumplen)})
        penalizacion.guardarMotivo(self._repo_penalizaciones, numero, list(incumplen))
        return {"mensaje": mensaje, "descuento": str(entrega.descuento),
                "motivo": (self._repo_penalizaciones.obtener(numero) or {}).get("motivo")}

    def registrarCalificacion(self, numero, nota, escala, comentarios):
        tarea = self._tarea(numero)
        entrega = self._entrega(tarea)
        entrega.registrarCalificacion(nota, escala, comentarios)
        entrega.guardar(self._repo_entregas)

    def crearTarea(self, datos):
        numero = GeneradorCodigo(len(self._repo_tareas.listar())).siguienteNumero()
        rubrica = Rubrica()
        for criterio in datos.get("criterios", []):
            rubrica.agregarCriterio(criterio["nombre"], criterio["puntaje"])
        comunes = dict(
            ruta_adjunto=datos.get("ruta_adjunto"),
            codigo=GeneradorCodigo().generar(numero),
            rubrica=rubrica,
        )
        fecha_limite = datetime.fromisoformat(datos["fecha_limite"])
        if datos["tipo"] == TIPOS_TAREA.GRUPAL.value:
            # NUEVO: Se incluye la penalización al crear la TareaGrupal
            return TareaGrupal(numero, datos["titulo"], datos["instrucciones"], fecha_limite,
                               tamano_equipo=datos.get("tamano_equipo"), 
                               penalizacion=datos.get("penalizacion"), **comunes)
        return TareaIndividual(numero, datos["titulo"], datos["instrucciones"], fecha_limite, **comunes)

    def registrarTarea(self, tarea, ahora):
        tarea.registrar(ahora)
        tarea.rubrica.obtenerPuntajeMaximo()
        tarea.guardar(self._repo_tareas)
        return {"numero": tarea.numero, "codigo": tarea.codigo, "estado": tarea.estado.value}