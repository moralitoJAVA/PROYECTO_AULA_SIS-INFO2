from datetime import date
from decimal import Decimal

import pytest

from src.constantes import MSG_ESTADO_INVALIDO, MSG_NO_ES_DIA_DE_CLASE, MSG_YA_REGISTRADA
from src.repositorio.repositorio_memoria import RepositorioMemoria
from src.servicio.servicio_asistencia import ServicioAsistencia

MATERIA = "Sistemas de Información 2"
MARTES, MIERCOLES, JUEVES = date(2026, 3, 3), date(2026, 3, 4), date(2026, 3, 5)


@pytest.fixture
def servicio():
    return ServicioAsistencia(RepositorioMemoria())


def test_registrar_devuelve_el_resumen(servicio):
    assert servicio.registrarAsistencia(MATERIA, MARTES, "Presente") == "1 presentes, 0 atrasos, 0 ausentes"


def test_registrar_una_fecha_que_no_es_dia_de_clase_falla(servicio):
    with pytest.raises(ValueError) as error:
        servicio.registrarAsistencia(MATERIA, JUEVES, "Presente")
    assert str(error.value) == MSG_NO_ES_DIA_DE_CLASE


def test_estado_desconocido_falla(servicio):
    with pytest.raises(ValueError) as error:
        servicio.registrarAsistencia(MATERIA, MARTES, "Faltó")
    assert str(error.value) == MSG_ESTADO_INVALIDO


def test_registrar_dos_veces_la_misma_clase_falla(servicio):
    servicio.registrarAsistencia(MATERIA, MARTES, "Presente")
    with pytest.raises(ValueError) as error:
        servicio.registrarAsistencia(MATERIA, MARTES, "Atraso")
    assert str(error.value) == MSG_YA_REGISTRADA


def test_abrir_una_fecha_ya_registrada_devuelve_la_asistencia_existente(servicio):
    servicio.registrarAsistencia(MATERIA, MARTES, "Presente")
    assert len(servicio.abrirSesion(MATERIA, MARTES).listarAsistencia()) == 1


def test_editar_cambia_el_estado_sin_duplicar(servicio):
    servicio.registrarAsistencia(MATERIA, MARTES, "Atraso")
    servicio.editarAsistencia(MATERIA, MARTES, "Presente")
    assert len(servicio.obtenerHistorial(MATERIA)) == 1


def test_porcentaje_y_alerta(servicio):
    servicio.registrarAsistencia(MATERIA, MARTES, "Presente")
    servicio.registrarAsistencia(MATERIA, MIERCOLES, "Ausente")
    assert servicio.obtenerPorcentaje(MATERIA) == Decimal("50.00")
    assert servicio.hayAlerta(MATERIA)


def test_los_datos_sobreviven_en_el_repositorio():
    repositorio = RepositorioMemoria()
    ServicioAsistencia(repositorio).registrarAsistencia(MATERIA, MARTES, "Presente")
    assert len(ServicioAsistencia(repositorio).obtenerHistorial(MATERIA)) == 1
