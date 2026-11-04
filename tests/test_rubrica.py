from decimal import Decimal

import pytest

from src.constantes import MSG_CRITERIO_VACIO, MSG_PUNTAJE_INVALIDO, MSG_RUBRICA_VACIA
from src.modelo.rubrica import Rubrica


def rubrica_de(**criterios):
    rubrica = Rubrica()
    for nombre, puntaje in criterios.items():
        rubrica.agregarCriterio(nombre, puntaje)
    return rubrica


def test_el_puntaje_maximo_es_la_suma_de_los_criterios():
    assert rubrica_de(codigo=60, informe=40).obtenerPuntajeMaximo() == Decimal("100")


def test_acepta_decimales_sin_error_de_float():
    assert rubrica_de(a="0.1", b="0.2").obtenerPuntajeMaximo() == Decimal("0.3")


def test_una_rubrica_vacia_no_tiene_puntaje_maximo():
    with pytest.raises(ValueError) as error:
        Rubrica().obtenerPuntajeMaximo()
    assert str(error.value) == MSG_RUBRICA_VACIA


def test_criterio_sin_nombre_falla():
    with pytest.raises(ValueError) as error:
        Rubrica().agregarCriterio(" ", 10)
    assert str(error.value) == MSG_CRITERIO_VACIO


@pytest.mark.parametrize("puntaje", [0, -5])
def test_puntaje_cero_o_negativo_falla(puntaje):
    with pytest.raises(ValueError) as error:
        Rubrica().agregarCriterio("codigo", puntaje)
    assert str(error.value) == MSG_PUNTAJE_INVALIDO


def test_ida_y_vuelta_a_diccionario():
    rubrica = rubrica_de(codigo=60, informe=40)
    copia = Rubrica.desdeDiccionario(rubrica.aDiccionario())
    assert copia.criterios == rubrica.criterios