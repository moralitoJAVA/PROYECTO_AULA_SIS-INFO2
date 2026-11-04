from datetime import datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

from src.constantes import (
    ESTADOS_TAREA,
    MSG_FUERA_DE_PLAZO,
    MSG_NOTA_FUERA_DE_RANGO,
    MSG_SIN_ENTREGA,
    MSG_SOLO_ENTREGADAS,
)
from src.modelo.entrega import Entrega

LIMITE = datetime(2026, 3, 4, 6, 45)
TAREA = SimpleNamespace(numero=1, fecha_limite=LIMITE)


class RubricaFalsa:
    def __init__(self, maximo=100):
        self._maximo = maximo

    def obtenerPuntajeMaximo(self):
        return self._maximo


def entrega(**datos):
    datos.setdefault("archivos", ["tarea01.zip"])
    return Entrega(TAREA, RubricaFalsa(), **datos)


def test_antes_del_plazo_se_acepta_y_queda_entregada():
    nueva = entrega()
    nueva.confirmar(LIMITE - timedelta(hours=1))
    assert nueva.estado == ESTADOS_TAREA.ENTREGADA


def test_a_la_hora_limite_exacta_todavia_se_acepta():
    entrega().validar(LIMITE)


def test_un_segundo_despues_del_plazo_se_rechaza():
    with pytest.raises(ValueError) as error:
        entrega().validar(LIMITE + timedelta(seconds=1))
    assert str(error.value) == MSG_FUERA_DE_PLAZO


def test_sin_archivos_ni_enlaces_falla():
    with pytest.raises(ValueError) as error:
        entrega(archivos=[]).validar(LIMITE - timedelta(hours=1))
    assert str(error.value) == MSG_SIN_ENTREGA


def test_con_solo_un_enlace_se_acepta():
    entrega(archivos=[], enlaces=["https://ejemplo.com/tarea"]).validar(LIMITE - timedelta(hours=1))


def test_confirmar_guarda_la_hora_exacta_y_la_devuelve_en_el_mensaje():
    nueva = entrega()
    ahora = datetime(2026, 3, 3, 21, 30, 15)
    assert nueva.confirmar(ahora) == "Entrega confirmada el 03/03/2026 a las 21:30:15"
    assert nueva.fecha_hora_entrega == ahora


def test_si_falla_la_validacion_no_cambia_el_estado():
    nueva = entrega(archivos=[])
    with pytest.raises(ValueError):
        nueva.confirmar(LIMITE - timedelta(hours=1))
    assert nueva.estado == ESTADOS_TAREA.PENDIENTE


def test_a_menos_de_24_horas_avisa():
    assert entrega().estaPorVencer(LIMITE - timedelta(hours=23, minutes=59))


def test_a_24_horas_exactas_o_mas_no_avisa():
    assert not entrega().estaPorVencer(LIMITE - timedelta(hours=24))
    assert not entrega().estaPorVencer(LIMITE - timedelta(hours=30))


def test_una_tarea_vencida_no_avisa():
    assert not entrega().estaPorVencer(LIMITE + timedelta(minutes=1))


def test_una_tarea_ya_entregada_no_avisa():
    nueva = entrega()
    nueva.confirmar(LIMITE - timedelta(hours=2))
    assert not nueva.estaPorVencer(LIMITE - timedelta(hours=1))


def entregada():
    nueva = entrega()
    nueva.confirmar(LIMITE - timedelta(hours=2))
    return nueva


def test_registrar_calificacion_guarda_nota_escala_y_comentarios():
    nueva = entregada()
    nueva.registrarCalificacion("85.5", "0-100", "Buen trabajo")
    assert (nueva.nota, nueva.escala, nueva.comentarios) == (Decimal("85.5"), "0-100", "Buen trabajo")
    assert nueva.puntaje_maximo == Decimal("100")
    assert nueva.estado == ESTADOS_TAREA.CALIFICADA


@pytest.mark.parametrize("nota", ["100.01", "-1"])
def test_una_nota_fuera_del_rango_falla(nota):
    with pytest.raises(ValueError) as error:
        entregada().registrarCalificacion(nota, "0-100", "")
    assert str(error.value) == MSG_NOTA_FUERA_DE_RANGO


def test_la_nota_igual_al_maximo_se_acepta():
    entregada().registrarCalificacion("100", "0-100", "")


def test_no_se_califica_una_tarea_que_no_se_entrego():
    with pytest.raises(ValueError) as error:
        entrega().registrarCalificacion("80", "0-100", "")
    assert str(error.value) == MSG_SOLO_ENTREGADAS