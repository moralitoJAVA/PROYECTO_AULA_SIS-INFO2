from datetime import datetime

import pytest

from src.constantes import (
    ESTADOS_TAREA,
    MSG_DIA_NO_HABIL,
    MSG_FECHA_PASADA,
    MSG_NUMERO_INVALIDO,
    MSG_SIN_GUIA,
    MSG_TITULO_VACIO,
    TIPOS_TAREA,
)
from src.modelo.tarea import Tarea

AHORA = datetime(2026, 3, 1, 10, 0)
MIERCOLES_0645 = datetime(2026, 3, 4, 6, 45)


def crear(**cambios):
    datos = dict(numero=1, titulo="Tarea 01", instrucciones="Resolver", fecha_limite=MIERCOLES_0645)
    datos.update(cambios)
    return Tarea(**datos)


def test_guarda_los_atributos():
    tarea = crear()
    assert (tarea.numero, tarea.titulo, tarea.tipo) == (1, "Tarea 01", TIPOS_TAREA.INDIVIDUAL)
    assert tarea.estado is None
    assert tarea.ruta_adjunto is None and tarea.codigo is None


@pytest.mark.parametrize("numero", [0, -1, "1", True])
def test_numero_invalido_falla(numero):
    with pytest.raises(ValueError) as error:
        crear(numero=numero)
    assert str(error.value) == MSG_NUMERO_INVALIDO


@pytest.mark.parametrize("titulo", ["", "   ", None])
def test_titulo_vacio_falla(titulo):
    with pytest.raises(ValueError) as error:
        crear(titulo=titulo)
    assert str(error.value) == MSG_TITULO_VACIO


def test_fecha_anterior_a_la_actual_falla_con_el_mensaje_exacto():
    tarea = crear(fecha_limite=datetime(2026, 2, 25, 6, 45))
    with pytest.raises(ValueError) as error:
        tarea.validarFecha(AHORA)
    assert str(error.value) == "La fecha límite debe ser posterior a la fecha y hora actual."


def test_fecha_igual_a_la_actual_falla():
    with pytest.raises(ValueError):
        crear().validarFecha(MIERCOLES_0645)


def test_fecha_posterior_a_la_actual_es_valida():
    crear().validarFecha(AHORA)


@pytest.mark.parametrize("dia", [3, 4, 6])  # martes, miércoles, viernes de marzo de 2026
def test_martes_miercoles_y_viernes_a_las_0645_se_aceptan(dia):
    crear(fecha_limite=datetime(2026, 3, dia, 6, 45)).validarDiaHabil()


@pytest.mark.parametrize("fecha", [datetime(2026, 3, 5, 6, 45), datetime(2026, 3, 7, 6, 45), datetime(2026, 3, 4, 7, 0)])
def test_otro_dia_u_otra_hora_se_rechaza(fecha):
    with pytest.raises(ValueError) as error:
        crear(fecha_limite=fecha).validarDiaHabil()
    assert str(error.value) == MSG_DIA_NO_HABIL


def test_registrar_con_guia_pasa_a_registrada():
    tarea = crear()
    tarea.adjuntarGuia("guias/tarea01.pdf")
    tarea.registrar(AHORA)
    assert tarea.estado == ESTADOS_TAREA.REGISTRADA


def test_registrar_sin_guia_falla_y_no_cambia_el_estado():
    tarea = crear()
    with pytest.raises(ValueError) as error:
        tarea.registrar(AHORA)
    assert str(error.value) == MSG_SIN_GUIA
    assert tarea.estado is None


def test_registrar_con_fecha_pasada_muestra_el_mensaje_de_fecha():
    tarea = crear(fecha_limite=datetime(2026, 2, 25, 6, 45))
    tarea.adjuntarGuia("guia.pdf")
    with pytest.raises(ValueError) as error:
        tarea.registrar(AHORA)
    assert str(error.value) == MSG_FECHA_PASADA


def test_guia_vacia_falla():
    with pytest.raises(ValueError):
        crear().adjuntarGuia("  ")