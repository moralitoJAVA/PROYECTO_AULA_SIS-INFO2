import pytest

from src.api.app import crear_app

MATERIA = "Sistemas de Información 2"


@pytest.fixture
def cliente():
    return crear_app(":memory:").test_client()


def registrar(cliente, fecha, estado):
    return cliente.post("/api/asistencia", json={"materia": MATERIA, "fecha": fecha, "estado": estado})


def test_registrar_devuelve_el_resumen(cliente):
    respuesta = registrar(cliente, "2026-03-03", "Presente")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["resumen"] == "1 presentes, 0 atrasos, 0 ausentes"


def test_registrar_otra_vez_la_misma_clase_la_edita_sin_duplicar(cliente):
    registrar(cliente, "2026-03-03", "Atraso")
    registrar(cliente, "2026-03-03", "Presente")
    assert len(cliente.get("/api/asistencia/panel").get_json()["historial"]) == 1


def test_un_dia_que_no_es_de_clase_devuelve_el_error(cliente):
    respuesta = registrar(cliente, "2026-03-05", "Presente")
    assert respuesta.status_code == 400
    assert respuesta.get_json() == {"error": "La fecha no es un día de clase"}


def test_el_panel_muestra_porcentaje_y_alerta(cliente):
    registrar(cliente, "2026-03-03", "Presente")
    registrar(cliente, "2026-03-04", "Ausente")
    panel = cliente.get("/api/asistencia/panel").get_json()
    assert panel["porcentaje"] == "50.00"
    assert panel["alerta"] is True


def test_la_pagina_de_inicio_se_sirve(cliente):
    assert cliente.get("/").status_code == 200
