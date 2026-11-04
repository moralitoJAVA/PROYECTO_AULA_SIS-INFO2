from datetime import datetime

import pytest

from src.constantes import ESTADOS_TAREA, MSG_SIN_TAMANO, MSG_TAMANO_EQUIPO, TIPOS_TAREA
from src.modelo.rubrica import Rubrica
from src.modelo.tarea_grupal import TareaGrupal
from src.modelo.tarea_individual import TareaIndividual
from src.repositorio.repositorio_memoria import RepositorioMemoria

AHORA = datetime(2026, 3, 1, 10, 0)
LIMITE = datetime(2026, 3, 4, 6, 45)


def rubrica():
    r = Rubrica()
    r.agregarCriterio("codigo", 100)
    return r


def test_la_individual_tiene_tipo_individual_y_asigna_a_todos():
    tarea = TareaIndividual(1, "T1", "x", LIMITE)
    assert tarea.tipo == TIPOS_TAREA.INDIVIDUAL
    assert tarea.asignarATodos(["Ana"]) == ["Ana"]


def test_la_grupal_sin_tamano_de_equipo_falla_al_registrar():
    tarea = TareaGrupal(2, "T2", "x", LIMITE, ruta_adjunto="guia.pdf")
    with pytest.raises(ValueError) as error:
        tarea.registrar(AHORA)
    assert str(error.value) == MSG_SIN_TAMANO
    assert tarea.estado is None


@pytest.mark.parametrize("tamano", [1, 0, "3", True])
def test_tamano_de_equipo_invalido_falla(tamano):
    with pytest.raises(ValueError) as error:
        TareaGrupal(2, "T2", "x", LIMITE).definirTamano(tamano)
    assert str(error.value) == MSG_TAMANO_EQUIPO


def test_la_grupal_con_tamano_se_registra():
    tarea = TareaGrupal(2, "T2", "x", LIMITE, tamano_equipo=3, ruta_adjunto="guia.pdf")
    tarea.registrar(AHORA)
    assert tarea.estado == ESTADOS_TAREA.REGISTRADA


def test_definir_penalizacion_la_guarda():
    tarea = TareaGrupal(2, "T2", "x", LIMITE)
    tarea.definirPenalizacion("penalizacion")
    assert tarea.penalizacion == "penalizacion"


def test_guardar_y_reconstruir_una_individual():
    repositorio = RepositorioMemoria()
    tarea = TareaIndividual(1, "T1", "x", LIMITE, ruta_adjunto="guia.pdf", codigo="[IS-2026][P1] Tarea 01", rubrica=rubrica())
    tarea.registrar(AHORA)
    tarea.guardar(repositorio)
    copia = TareaIndividual.desdeDiccionario(repositorio.obtener(1))
    assert (copia.numero, copia.titulo, copia.fecha_limite, copia.estado, copia.codigo) == (
        1, "T1", LIMITE, ESTADOS_TAREA.REGISTRADA, "[IS-2026][P1] Tarea 01")
    assert copia.rubrica.obtenerPuntajeMaximo() == 100


def test_guardar_y_reconstruir_una_grupal_conserva_el_tamano():
    repositorio = RepositorioMemoria()
    TareaGrupal(2, "T2", "x", LIMITE, tamano_equipo=4, rubrica=rubrica()).guardar(repositorio)
    copia = TareaGrupal.desdeDiccionario(repositorio.obtener(2))
    assert copia.tamano_equipo == 4 and copia.tipo == TIPOS_TAREA.GRUPAL