import pytest

from src.constantes import MSG_NOMBRE_VACIO
from src.modelo.estudiante import Estudiante


def test_guarda_el_nombre_sin_espacios_sobrantes():
    assert Estudiante("  Julio Cesar  ").obtenerDatos() == {"nombre": "Julio Cesar"}


@pytest.mark.parametrize("nombre", ["", "   ", None])
def test_nombre_vacio_lanza_error_con_mensaje_exacto(nombre):
    with pytest.raises(ValueError) as error:
        Estudiante(nombre)
    assert str(error.value) == MSG_NOMBRE_VACIO


def test_obtener_historial_delega_en_el_registro_de_asistencia():
    class RegistroFalso:
        def obtenerHistorial(self):
            return ["clase 1"]

    assert Estudiante("Julio").obtenerHistorial(RegistroFalso()) == ["clase 1"]


def test_obtener_desglose_delega_en_la_calculadora():
    class CalculadoraFalsa:
        def obtenerDesglose(self):
            return {"asistencia": "100.00"}

    assert Estudiante("Julio").obtenerDesglose(CalculadoraFalsa()) == {"asistencia": "100.00"}
