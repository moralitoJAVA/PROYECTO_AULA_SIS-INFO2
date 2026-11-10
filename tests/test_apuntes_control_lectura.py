from datetime import datetime, timedelta

import pytest

from src.constantes import PUNTUALIDAD, VENTANA_CLASE
from src.modelo.apuntes_control_lectura import ApuntesControlLectura
from src.modelo.clase_lectura import ClaseLectura
from src.modelo.lectura import Lectura

AHORA = datetime(2026, 3, 3, 7, 0)
INICIO = datetime(2026, 3, 3, 6, 45)
CIERRE = datetime(2026, 3, 4, 6, 45)


def test_lectura_solo_exige_titulo_y_archivo_o_enlace():
    assert Lectura(1, "Libro", archivo="a.pdf").autor is None
    for datos in ({"titulo": "", "enlace": "x"}, {"titulo": "Libro"}):
        with pytest.raises(ValueError):
            Lectura(1, **datos)


def test_la_clase_clasifica_a_tiempo_hasta_el_plazo_inclusive_y_tarde_despues():
    clase = ClaseLectura(1, "Tema", INICIO, CIERRE, [1, 1, 2])
    assert clase.ids_lecturas == [1, 2]
    assert clase.clasificarEnvio(CIERRE) == PUNTUALIDAD.A_TIEMPO
    assert clase.clasificarEnvio(CIERRE + timedelta(seconds=1)) == PUNTUALIDAD.TARDE
    assert clase.ventana(INICIO - timedelta(minutes=1)) == VENTANA_CLASE.ANTES_DE_CLASE
    assert clase.ventana(AHORA) == VENTANA_CLASE.DENTRO_DEL_PLAZO
    assert clase.ventana(CIERRE + timedelta(minutes=1)) == VENTANA_CLASE.PLAZO_VENCIDO


@pytest.mark.parametrize("datos", [("", INICIO, CIERRE, [1]), ("T", INICIO, CIERRE, []), ("T", CIERRE, INICIO, [1])])
def test_la_clase_valida_tema_bibliografia_y_plazo(datos):
    with pytest.raises(ValueError):
        ClaseLectura(1, *datos)


def test_el_cuaderno_guarda_apuntes_y_dudas_y_sobrevive_a_la_serializacion():
    cuaderno = ApuntesControlLectura(1, "Ana")
    cuaderno.agregarApunte(2, " idea ", AHORA)
    cuaderno.agregarDuda("¿por qué?", AHORA)
    cuaderno.editarApunte(1, "idea 2", AHORA + timedelta(minutes=5), id_lectura=1)
    copia = ApuntesControlLectura.desdeDiccionario(cuaderno.aDiccionario())
    assert copia.apuntes[0]["texto"] == "idea 2" and copia.apuntes[0]["id_lectura"] == 1
    assert copia.apuntes[0]["creado"] != copia.apuntes[0]["actualizado"]
    assert copia.dudas[0]["texto"] == "¿por qué?"
    assert copia.agregarApunte(1, "otra", AHORA)["id"] == 2