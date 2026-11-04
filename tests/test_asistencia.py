from datetime import date

import pytest

from src.constantes import ESTADOS, MSG_ESTADO_INVALIDO, MSG_NO_REGISTRADA, MSG_YA_REGISTRADA
from src.modelo.asistencia import Asistencia

CLASE = date(2026, 3, 4)


def test_marcar_presente_se_guarda():
    asistencia = Asistencia()
    asistencia.registrar(CLASE, ESTADOS.PRESENTE)
    assert asistencia.registros[CLASE] == ESTADOS.PRESENTE


def test_estado_invalido_falla_con_mensaje_exacto():
    with pytest.raises(ValueError) as error:
        Asistencia().registrar(CLASE, "Faltó")
    assert str(error.value) == MSG_ESTADO_INVALIDO


def test_registrar_dos_veces_la_misma_clase_falla():
    asistencia = Asistencia()
    asistencia.registrar(CLASE, ESTADOS.PRESENTE)
    with pytest.raises(ValueError) as error:
        asistencia.registrar(CLASE, ESTADOS.ATRASO)
    assert str(error.value) == MSG_YA_REGISTRADA


def test_editar_de_atraso_a_presente_no_duplica():
    asistencia = Asistencia()
    asistencia.registrar(CLASE, ESTADOS.ATRASO)
    asistencia.editar(CLASE, ESTADOS.PRESENTE)
    assert asistencia.registros == {CLASE: ESTADOS.PRESENTE}


def test_editar_una_clase_sin_registro_falla():
    with pytest.raises(ValueError) as error:
        Asistencia().editar(CLASE, ESTADOS.PRESENTE)
    assert str(error.value) == MSG_NO_REGISTRADA


def test_existe_para_indica_si_la_clase_ya_tiene_asistencia():
    asistencia = Asistencia()
    assert not asistencia.existePara(CLASE)
    asistencia.registrar(CLASE, ESTADOS.AUSENTE)
    assert asistencia.existePara(CLASE)
