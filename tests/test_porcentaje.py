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
