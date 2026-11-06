import sqlite3
from datetime import date, datetime
from decimal import Decimal

from src.api.app import crear_app
from src.modelo.calculadora_nota_final import CalculadoraNotaFinal
from src.modelo.penalizacion import Penalizacion
from src.modelo.porcentaje import Porcentaje
from src.modelo.rubrica import Rubrica
from src.modelo.tarea_grupal import TareaGrupal
from src.modelo.tarea_individual import TareaIndividual
from src.repositorio.repositorio_memoria import RepositorioMemoria
from src.repositorio.repositorio_sqlite import RepositorioSqlite
from src.servicio.servicio_asistencia import ServicioAsistencia
from src.servicio.servicio_tareas import ServicioTareas

MATERIA = "Sistemas de Información 2"
PESOS_VALIDOS = {"asistencia": 10, "tareas": 30, "examenes": 40, "proyecto": 20}
REGISTRO = datetime(2026, 3, 1, 10, 0)
LIMITE_INDIVIDUAL = datetime(2026, 3, 4, 6, 45) 
LIMITE_GRUPAL = datetime(2026, 3, 6, 6, 45)     
ANTES_DEL_LIMITE = datetime(2026, 3, 3, 20, 0)
CLASE_1 = date(2026, 3, 3)                      
CLASE_2 = date(2026, 3, 4)                      


def crearRubrica():
    rubrica = Rubrica()
    rubrica.agregarCriterio("codigo", 100)
    return rubrica


def crearClienteApi(rutaBd):
    tarea = TareaIndividual(1, "Tarea 1", "x", LIMITE_INDIVIDUAL, ruta_adjunto="g.pdf", rubrica=crearRubrica())
    tarea.registrar(REGISTRO)
    tarea.guardar(RepositorioSqlite(sqlite3.connect(rutaBd), "tareas"))
    return crear_app(rutaBd, ahora=lambda: ANTES_DEL_LIMITE).test_client()


def crearServicios():
    servicioTareas = ServicioTareas(RepositorioMemoria(), RepositorioMemoria(),
                                    RepositorioMemoria(), RepositorioMemoria())
    individual = TareaIndividual(1, "Individual", "x", LIMITE_INDIVIDUAL,
                                 ruta_adjunto="g.pdf", rubrica=crearRubrica())
    grupal = TareaGrupal(2, "Grupal", "x", LIMITE_GRUPAL, tamano_equipo=3, penalizacion=Penalizacion(),
                         ruta_adjunto="g.pdf", rubrica=crearRubrica())
    for tarea in (individual, grupal):
        tarea.registrar(REGISTRO)
        tarea.guardar(servicioTareas._repo_tareas)
    return servicioTareas, ServicioAsistencia(RepositorioMemoria())


def crearCalculadora(servicioTareas, servicioAsistencia, pesos=PESOS_VALIDOS, otras=None):
    return CalculadoraNotaFinal(Porcentaje(pesos), servicioTareas.crearHistorial(),
                                servicioAsistencia.crearRegistro(MATERIA), otras)


def entregarYCalificarIndividual(servicioTareas, nota):
    servicioTareas.entregar(1, ["t1.zip"], [], ANTES_DEL_LIMITE)
    servicioTareas.registrarCalificacion(1, nota, "0-100", "")


def entregarYCalificarGrupal(servicioTareas, nota, incumplen):
    servicioTareas.entregarPorEquipo(2, ["Ana", "Luis", "Eva"], "Ana", incumplen,
                                     ["eq.zip"], [], ANTES_DEL_LIMITE)
    servicioTareas.registrarCalificacion(2, nota, "0-100", "")


def dec(valor):
    return Decimal(valor)
