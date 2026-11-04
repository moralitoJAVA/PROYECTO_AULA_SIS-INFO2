from decimal import Decimal
 
import pytest
 
from src.constantes import COMPONENTES, MSG_COMPONENTE_DESCONOCIDO
from src.modelo.porcentaje import Porcentaje
from src.repositorio.repositorio_memoria import RepositorioMemoria
 
PESOS = {"asistencia": 10, "tareas": 30, "examenes": 40, "proyecto": 20}
 
 
def test_los_componentes_son_asistencia_tareas_examenes_y_proyecto():
    assert COMPONENTES == ("asistencia", "tareas", "examenes", "proyecto")
 
 
def test_obtener_peso_devuelve_decimal():
    assert Porcentaje(PESOS).obtenerPeso("tareas") == Decimal("30")
 
 
def test_un_componente_sin_peso_vale_cero():
    assert Porcentaje({"asistencia": 100}).obtenerPeso("proyecto") == Decimal("0")
 
 
def test_un_componente_desconocido_falla():
    with pytest.raises(ValueError) as error:
        Porcentaje({"deportes": 10})
    assert str(error.value) == MSG_COMPONENTE_DESCONOCIDO
 
 
def test_guardar_escribe_los_pesos_en_el_repositorio():
    repositorio = RepositorioMemoria()
    Porcentaje(PESOS).guardar(repositorio)
    assert repositorio.obtener("pesos") == {"asistencia": "10", "tareas": "30", "examenes": "40", "proyecto": "20"}
 from src.constantes import MSG_PESO_NEGATIVO, MSG_PESOS_NO_SUMAN_100
 
 
def test_10_30_40_20_se_acepta():
    Porcentaje(PESOS).validarSuma()
 
 
def test_33_3_mas_33_3_mas_33_4_se_acepta_sin_error_de_float():
    Porcentaje({"asistencia": "33.3", "tareas": "33.3", "examenes": "33.4"}).validarSuma()
 
 
@pytest.mark.parametrize("pesos", [
    {"asistencia": 10, "tareas": 30, "examenes": 30, "proyecto": 20},
    {"asistencia": 10, "tareas": 30, "examenes": 50, "proyecto": 20},
])
def test_suma_90_o_110_falla_con_el_mensaje_exacto(pesos):
    with pytest.raises(ValueError) as error:
        Porcentaje(pesos).validarSuma()
    assert str(error.value) == "Los pesos deben sumar 100%"
 
 
def test_un_peso_negativo_falla_aunque_la_suma_sea_100():
    with pytest.raises(ValueError) as error:
        Porcentaje({"asistencia": -10, "tareas": 60, "examenes": 50}).validarSuma()
    assert str(error.value) == MSG_PESO_NEGATIVO
 
 
def test_guardar_rechaza_pesos_invalidos_y_no_escribe():
    repositorio = RepositorioMemoria()
    with pytest.raises(ValueError) as error:
        Porcentaje({"asistencia": 50}).guardar(repositorio)
    assert str(error.value) == MSG_PESOS_NO_SUMAN_100
    assert repositorio.listar() == {}

