from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

from src.constantes import CERO, ESTADOS_TAREA, TIPOS_TAREA
from src.modelo.historial_tareas import HistorialTareas


def tarea(numero, dia, tipo=TIPOS_TAREA.INDIVIDUAL):
    return SimpleNamespace(numero=numero, titulo=f"Tarea {numero}", fecha_limite=datetime(2026, 3, dia, 6, 45), tipo=tipo)


def entrega(estado, nota=None, maximo=None, descuento=CERO):
    return SimpleNamespace(estado=estado, nota=nota, puntaje_maximo=maximo, descuento=descuento)


TAREAS = [tarea(1, 6), tarea(2, 3), tarea(3, 4, TIPOS_TAREA.GRUPAL)]
ENTREGAS = {
    2: entrega(ESTADOS_TAREA.ENTREGADA),
    3: entrega(ESTADOS_TAREA.CALIFICADA, Decimal("45"), Decimal("50")),
}


def test_ordena_por_fecha_limite():
    numeros = [i["numero"] for i in HistorialTareas(TAREAS, ENTREGAS).listarPorEstado()]
    assert numeros == [2, 3, 1]


def test_filtra_por_estado():
    historial = HistorialTareas(TAREAS, ENTREGAS)
    assert [i["numero"] for i in historial.listarPorEstado(ESTADOS_TAREA.PENDIENTE)] == [1]
    assert [i["numero"] for i in historial.listarPorEstado(ESTADOS_TAREA.ENTREGADA)] == [2]
    assert [i["numero"] for i in historial.listarPorEstado(ESTADOS_TAREA.CALIFICADA)] == [3]


def test_incluye_individuales_y_grupales():
    tipos = {i["tipo"] for i in HistorialTareas(TAREAS, ENTREGAS).listarPorEstado()}
    assert tipos == {"Individual", "Grupal"}


def test_una_tarea_sin_entrega_esta_pendiente():
    assert HistorialTareas(TAREAS, {}).listarPorEstado(ESTADOS_TAREA.PENDIENTE)[0]["nota"] is None


def test_las_notas_se_llevan_a_base_100_con_su_descuento():
    entregas = {3: entrega(ESTADOS_TAREA.CALIFICADA, Decimal("45"), Decimal("50"), Decimal("10"))}
    assert HistorialTareas(TAREAS, entregas).obtenerNotas() == [
        {"numero": 3, "nota_sobre_100": Decimal("90.00"), "descuento": Decimal("10")}
    ] 


def test_solo_las_calificadas_aportan_notas():
    assert len(HistorialTareas(TAREAS, ENTREGAS).obtenerNotas()) == 1