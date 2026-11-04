from datetime import date, timedelta

from src.constantes import ESTADOS
from src.modelo.asistencia import Asistencia
from src.modelo.sesion import Sesion

MARTES, JUEVES = date(2026, 3, 3), date(2026, 3, 5)


def asistencia_con(*estados):
    asistencia = Asistencia()
    for indice, estado in enumerate(estados):
        asistencia.registrar(date(2026, 1, 1) + timedelta(days=indice), estado)
    return asistencia


def test_un_martes_es_dia_de_clase():
    assert Sesion("SIS2", MARTES, Asistencia()).esDiaDeClase()


def test_un_jueves_no_es_dia_de_clase():
    assert not Sesion("SIS2", JUEVES, Asistencia()).esDiaDeClase()


def test_el_resumen_cuenta_presentes_atrasos_y_ausentes():
    estados = [ESTADOS.PRESENTE] * 25 + [ESTADOS.ATRASO] * 3 + [ESTADOS.AUSENTE] * 2
    sesion = Sesion("SIS2", MARTES, asistencia_con(*estados))
    assert sesion.obtenerResumen() == "25 presentes, 3 atrasos, 2 ausentes"


def test_el_resumen_agrega_las_licencias_solo_si_hay():
    sesion = Sesion("SIS2", MARTES, asistencia_con(ESTADOS.PRESENTE, ESTADOS.LICENCIA))
    assert sesion.obtenerResumen() == "1 presentes, 0 atrasos, 0 ausentes, 1 licencias"


def test_listar_asistencia_ordena_por_fecha():
    asistencia = Asistencia()
    asistencia.registrar(date(2026, 3, 6), ESTADOS.AUSENTE)
    asistencia.registrar(date(2026, 3, 3), ESTADOS.PRESENTE)
    assert [fecha for fecha, _ in Sesion("SIS2", MARTES, asistencia).listarAsistencia()] == [date(2026, 3, 3), date(2026, 3, 6)]
