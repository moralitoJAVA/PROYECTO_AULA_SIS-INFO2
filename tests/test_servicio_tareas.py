from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from src.constantes import (
    MSG_ES_GRUPAL,
    MSG_ES_INDIVIDUAL,
    MSG_FUERA_DE_PLAZO,
    MSG_TAREA_NO_EXISTE,
    MSG_YA_ENTREGADA,
)
from src.modelo.rubrica import Rubrica
from src.modelo.tarea_grupal import TareaGrupal
from src.modelo.tarea_individual import TareaIndividual
from src.repositorio.repositorio_memoria import RepositorioMemoria
from src.servicio.servicio_tareas import ServicioTareas

REGISTRO = datetime(2026, 3, 1, 10, 0)
LIMITE = datetime(2026, 3, 4, 6, 45)
ANTES = LIMITE - timedelta(hours=3)


def rubrica():
    r = Rubrica()
    r.agregarCriterio("codigo", 100)
    return r


@pytest.fixture
def servicio():
    repo_tareas = RepositorioMemoria()
    individual = TareaIndividual(1, "Tarea 1", "x", LIMITE, ruta_adjunto="g.pdf", rubrica=rubrica())
    grupal = TareaGrupal(2, "Tarea 2", "x", datetime(2026, 3, 6, 6, 45), tamano_equipo=3,
                         ruta_adjunto="g.pdf", rubrica=rubrica())
    for tarea in (individual, grupal):
        tarea.registrar(REGISTRO)
        tarea.guardar(repo_tareas)
    return ServicioTareas(repo_tareas, RepositorioMemoria(), RepositorioMemoria(), RepositorioMemoria())


def test_lista_las_tareas_pendientes_ordenadas_por_fecha(servicio):
    assert [t["numero"] for t in servicio.listarPorEstado("Pendiente")] == [1, 2]


def test_entregar_confirma_y_cambia_el_estado(servicio):
    assert servicio.entregar(1, ["t1.zip"], [], ANTES).startswith("Entrega confirmada el 04/03/2026")
    assert [t["numero"] for t in servicio.listarPorEstado("Entregada")] == [1]


def test_entregar_fuera_de_plazo_falla_y_no_guarda(servicio):
    with pytest.raises(ValueError) as error:
        servicio.entregar(1, ["t1.zip"], [], LIMITE + timedelta(minutes=1))
    assert str(error.value) == MSG_FUERA_DE_PLAZO
    assert servicio.listarPorEstado("Entregada") == []


def test_no_se_entrega_dos_veces(servicio):
    servicio.entregar(1, ["t1.zip"], [], ANTES)
    with pytest.raises(ValueError) as error:
        servicio.entregar(1, ["otra.zip"], [], ANTES)
    assert str(error.value) == MSG_YA_ENTREGADA


def test_una_tarea_inexistente_falla(servicio):
    with pytest.raises(ValueError) as error:
        servicio.entregar(99, ["x"], [], ANTES)
    assert str(error.value) == MSG_TAREA_NO_EXISTE


def test_una_grupal_no_se_entrega_como_individual(servicio):
    with pytest.raises(ValueError) as error:
        servicio.entregar(2, ["x"], [], ANTES)
    assert str(error.value) == MSG_ES_GRUPAL


def test_una_individual_no_se_entrega_por_equipo(servicio):
    with pytest.raises(ValueError) as error:
        servicio.entregarPorEquipo(1, ["Ana", "Luis", "Eva"], "Ana", [], ["x"], [], ANTES)
    assert str(error.value) == MSG_ES_INDIVIDUAL


def test_entrega_por_equipo_con_penalizacion_y_motivo(servicio):
    resultado = servicio.entregarPorEquipo(2, ["Ana", "Luis", "Eva"], "Luis", ["Luis"], ["x.zip"], [], ANTES)
    assert resultado["descuento"] == "10"
    assert resultado["motivo"] == "Incumplieron: Luis. Descuento aplicado: 10%"


def test_el_equipo_debe_tener_el_tamano_de_la_tarea(servicio):
    with pytest.raises(ValueError) as error:
        servicio.entregarPorEquipo(2, ["Ana", "Luis"], "Ana", [], ["x"], [], ANTES)
    assert str(error.value) == "El equipo debe tener exactamente 3 integrantes"


def test_registrar_calificacion_y_notas_para_la_nota_final(servicio):
    servicio.entregar(1, ["t1.zip"], [], ANTES)
    servicio.registrarCalificacion(1, "80", "0-100", "Bien")
    assert [t["numero"] for t in servicio.listarPorEstado("Calificada")] == [1]
    assert servicio.crearHistorial().obtenerNotas()[0]["nota_sobre_100"] == Decimal("80.00")


def test_la_penalizacion_llega_a_las_notas(servicio):
    servicio.entregarPorEquipo(2, ["Ana", "Luis", "Eva"], "Luis", ["Luis"], ["x.zip"], [], ANTES)
    servicio.registrarCalificacion(2, "100", "0-100", "")
    assert servicio.crearHistorial().obtenerNotas()[0]["descuento"] == Decimal("10")


def test_avisa_las_tareas_que_vencen_en_menos_de_24_horas(servicio):
    assert servicio.tareasPorVencer(LIMITE - timedelta(hours=5)) == [1]


def test_el_detalle_incluye_el_puntaje_maximo(servicio):
    assert servicio.obtenerDetalle(1)["puntaje_maximo"] == "100"