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
