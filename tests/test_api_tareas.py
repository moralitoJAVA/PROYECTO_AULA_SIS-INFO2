import sqlite3
from datetime import datetime

import pytest

from src.api.app import crear_app
from src.modelo.rubrica import Rubrica
from src.modelo.tarea_individual import TareaIndividual
from src.repositorio.repositorio_sqlite import RepositorioSqlite

REGISTRO = datetime(2026, 3, 1, 10, 0)
LIMITE = datetime(2026, 3, 4, 6, 45)
ANTES = datetime(2026, 3, 3, 20, 0)


@pytest.fixture
def cliente(tmp_path):
    ruta = str(tmp_path / "prueba.db")
    rubrica = Rubrica()
    rubrica.agregarCriterio("codigo", 100)
    tarea = TareaIndividual(1, "Tarea 1", "x", LIMITE, ruta_adjunto="g.pdf", rubrica=rubrica)
    tarea.registrar(REGISTRO)
    tarea.guardar(RepositorioSqlite(sqlite3.connect(ruta), "tareas"))
    return crear_app(ruta, ahora=lambda: ANTES).test_client()


def test_el_panel_lista_pendientes_y_marca_las_que_vencen_pronto(cliente):
    datos = cliente.get("/api/tareas?estado=Pendiente").get_json()
    assert [t["numero"] for t in datos["tareas"]] == [1]
    assert datos["por_vencer"] == [1]


def test_entregar_y_calificar(cliente):
    respuesta = cliente.post("/api/tareas/1/entrega", json={"archivos": ["t1.zip"]})
    assert respuesta.status_code == 200
    assert cliente.post("/api/tareas/1/calificacion", json={"nota": "90", "escala": "0-100"}).status_code == 200
    assert cliente.get("/api/tareas?estado=Calificada").get_json()["tareas"][0]["nota"] == "90"


def test_entregar_sin_nada_devuelve_el_error(cliente):
    respuesta = cliente.post("/api/tareas/1/entrega", json={})
    assert respuesta.status_code == 400
    assert respuesta.get_json() == {"error": "Debes adjuntar al menos un archivo o enlace"}


def test_apuntes_crear_editar_listar_y_borrar(cliente):
    clave = cliente.post("/api/apuntes", json={"vinculo": "tarea-1", "texto": "uno"}).get_json()["clave"]
    cliente.put(f"/api/apuntes/{clave}", json={"texto": "dos"})
    assert cliente.get("/api/apuntes?vinculo=tarea-1").get_json()[0]["texto"] == "dos"
    cliente.delete(f"/api/apuntes/{clave}")
    assert cliente.get("/api/apuntes").get_json() == []