from datetime import datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

from src.constantes import (
    ESTADOS_TAREA,
    MSG_INTEGRANTE_REPETIDO,
    MSG_NO_ES_INTEGRANTE,
    MSG_SIN_ENTREGA_EQUIPO,
)
from src.modelo.entrega import Entrega
from src.modelo.equipo import Equipo

LIMITE = datetime(2026, 3, 4, 6, 45)
ANTES = LIMITE - timedelta(hours=2)


def entrega():
    tarea = SimpleNamespace(numero=1, fecha_limite=LIMITE)
    return Entrega(tarea, None, archivos=["informe.pdf"])


def equipo_de(*nombres):
    equipo = Equipo()
    for nombre in nombres:
        equipo.agregarIntegrante(nombre)
    return equipo


def test_un_integrante_entrega_por_todo_el_equipo():
    equipo = equipo_de("Ana", "Luis", "Eva")
    equipo.entregarPorGrupo(entrega(), "Ana", ANTES)
    resultado = equipo.repartirResultado()
    assert set(resultado) == {"Ana", "Luis", "Eva"}
    assert all(r["entrega"].estado == ESTADOS_TAREA.ENTREGADA for r in resultado.values())


def test_un_estudiante_fuera_del_equipo_no_puede_entregar():
    with pytest.raises(ValueError) as error:
        equipo_de("Ana").entregarPorGrupo(entrega(), "Pedro", ANTES)
    assert str(error.value) == MSG_NO_ES_INTEGRANTE


def test_integrante_repetido_falla():
    with pytest.raises(ValueError) as error:
        equipo_de("Ana", "Ana")
    assert str(error.value) == MSG_INTEGRANTE_REPETIDO


def test_un_incumplimiento_baja_10_solo_a_quien_incumple():
    equipo = equipo_de("Ana", "Luis")
    equipo.entregarPorGrupo(entrega(), "Ana", ANTES)
    resultado = equipo.repartirResultado(incumplen=["Luis"])
    assert resultado["Luis"]["descuento"] == Decimal("10")
    assert resultado["Ana"]["descuento"] == Decimal("0")


def test_dos_incumplimientos_bajan_el_doble():
    equipo = equipo_de("Ana", "Luis", "Eva")
    equipo.entregarPorGrupo(entrega(), "Ana", ANTES)
    assert equipo.repartirResultado(incumplen=["Luis", "Eva"])["Luis"]["descuento"] == Decimal("20")


def test_nadie_incumple_sin_descuento():
    equipo = equipo_de("Ana")
    equipo.entregarPorGrupo(entrega(), "Ana", ANTES)
    assert equipo.repartirResultado()["Ana"]["descuento"] == Decimal("0")


def test_repartir_antes_de_entregar_falla():
    with pytest.raises(ValueError) as error:
        equipo_de("Ana").repartirResultado()
    assert str(error.value) == MSG_SIN_ENTREGA_EQUIPO
    