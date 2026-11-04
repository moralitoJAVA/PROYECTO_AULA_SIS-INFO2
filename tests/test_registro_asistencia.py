from datetime import date, timedelta
from decimal import Decimal

from src.constantes import ESTADOS
from src.modelo.asistencia import Asistencia
from src.modelo.registro_asistencia import RegistroAsistencia


def registro_con(*estados):
    asistencia = Asistencia()
    for indice, estado in enumerate(estados):
        asistencia.registrar(date(2026, 1, 1) + timedelta(days=indice), estado)
    return RegistroAsistencia(asistencia)


def test_la_licencia_no_baja_el_porcentaje():
    assert registro_con(ESTADOS.PRESENTE, ESTADOS.LICENCIA, ESTADOS.PRESENTE).calcularPorcentaje() == Decimal("100.00")


def test_el_atraso_cuenta_como_asistido():
    assert registro_con(ESTADOS.ATRASO, ESTADOS.AUSENTE).calcularPorcentaje() == Decimal("50.00")


def test_79_por_ciento_con_minimo_80_lanza_alerta():
    registro = registro_con(*([ESTADOS.PRESENTE] * 79 + [ESTADOS.AUSENTE] * 21))
    assert registro.calcularPorcentaje() == Decimal("79.00")
    assert registro.hayAlerta()


def test_80_por_ciento_no_lanza_alerta():
    assert not registro_con(*([ESTADOS.PRESENTE] * 80 + [ESTADOS.AUSENTE] * 20)).hayAlerta()


def test_sin_sesiones_no_divide_por_cero_y_queda_pendiente():
    registro = registro_con()
    assert registro.calcularPorcentaje() is None
    assert not registro.hayAlerta()


def test_solo_licencias_tambien_queda_pendiente():
    assert registro_con(ESTADOS.LICENCIA).calcularPorcentaje() is None


def test_el_historial_sale_ordenado_por_fecha():
    assert [estado for _, estado in registro_con(ESTADOS.PRESENTE, ESTADOS.AUSENTE).obtenerHistorial()] == [ESTADOS.PRESENTE, ESTADOS.AUSENTE]
