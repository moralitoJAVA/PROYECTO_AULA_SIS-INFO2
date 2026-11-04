import sqlite3
from datetime import datetime
 
import pytest
 
from src.api.app import crear_app
from src.modelo.rubrica import Rubrica
from src.modelo.tarea_individual import TareaIndividual
from src.repositorio.repositorio_sqlite import RepositorioSqlite
 
ANTES = datetime(2026, 3, 3, 20, 0)
 
 
@pytest.fixture
def cliente(tmp_path):
    ruta = str(tmp_path / "prueba.db")
    rubrica = Rubrica()
    rubrica.agregarCriterio("codigo", 100)
    tarea = TareaIndividual(1, "Tarea 1", "x", datetime(2026, 3, 4, 6, 45), ruta_adjunto="g.pdf", rubrica=rubrica)
    tarea.registrar(datetime(2026, 3, 1, 10, 0))
    tarea.guardar(RepositorioSqlite(sqlite3.connect(ruta), "tareas"))
    return crear_app(ruta, ahora=lambda: ANTES).test_client()
 
 
def test_los_pesos_por_defecto(cliente):
    assert cliente.get("/api/pesos").get_json() == {"asistencia": "10", "tareas": "30", "examenes": "40", "proyecto": "20"}
 
 
def test_guardar_pesos_que_no_suman_100_devuelve_el_mensaje_exacto(cliente):
    respuesta = cliente.put("/api/pesos", json={"asistencia": 50})
    assert respuesta.status_code == 400
    assert respuesta.get_json() == {"error": "Los pesos deben sumar 100%"}
 
 
def test_guardar_pesos_validos_los_conserva(cliente):
    cliente.put("/api/pesos", json={"asistencia": 20, "tareas": 30, "examenes": 30, "proyecto": 20})
    assert cliente.get("/api/pesos").get_json()["asistencia"] == "20"
 
 
def test_sin_notas_todo_queda_pendiente(cliente):
    datos = cliente.get("/api/nota-final").get_json()
    assert datos["nota_final"] is None
    assert datos["parcial"] is True
 
 
def test_la_nota_final_se_recalcula_sola_al_cambiar_una_nota_y_la_asistencia(cliente):
    cliente.post("/api/asistencia", json={"materia": "Sistemas de Información 2", "fecha": "2026-03-03", "estado": "Presente"})
    cliente.post("/api/tareas/1/entrega", json={"archivos": ["t.zip"]})
    cliente.post("/api/tareas/1/calificacion", json={"nota": "80", "escala": "0-100"})
    primera = cliente.get("/api/nota-final").get_json()
    assert primera["componentes"]["tareas"]["nota"] == "80.00"
    assert primera["nota_final"] == "34.00"  # 100*10% + 80*30%
    cliente.post("/api/asistencia", json={"materia": "Sistemas de Información 2", "fecha": "2026-03-04", "estado": "Ausente"})
    assert cliente.get("/api/nota-final").get_json()["nota_final"] == "29.00"  # 50*10% + 80*30%
