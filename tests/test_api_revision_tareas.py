import sqlite3
from datetime import datetime

import pytest

from src.api.app import crear_app
from src.modelo.rubrica import Rubrica
from src.modelo.tarea_individual import TareaIndividual
from src.repositorio.repositorio_sqlite import RepositorioSqlite

MATERIA = "Sistemas de Información 2"
REGISTRO = datetime(2026, 3, 1, 10, 0)
LIMITE = datetime(2026, 3, 4, 6, 45)
ANTES = datetime(2026, 3, 3, 20, 0)
CLASE = datetime(2026, 3, 4, 7, 30)
REENTREGA = datetime(2026, 3, 4, 8, 0)


class Reloj:
    def __init__(self, ahora):
        self.ahora = ahora

    def __call__(self):
        return self.ahora


def crear_bd(ruta):
    rubrica = Rubrica()
    rubrica.agregarCriterio("codigo", 100)
    tarea = TareaIndividual(1, "Tarea 1", "x", LIMITE, ruta_adjunto="g.pdf", rubrica=rubrica)
    tarea.registrar(REGISTRO)
    tarea.guardar(RepositorioSqlite(sqlite3.connect(ruta), "tareas"))


@pytest.fixture
def ruta(tmp_path):
    ruta = str(tmp_path / "prueba.db")
    crear_bd(ruta)
    return ruta


@pytest.fixture
def reloj():
    return Reloj(ANTES)


@pytest.fixture
def cliente(ruta, reloj):
    return crear_app(ruta, ahora=reloj).test_client()


def entregar_y_asistir(cliente, reloj, asistencia="Presente"):
    assert cliente.post("/api/tareas/1/entrega", json={"archivos": ["a.pdf"]}).status_code == 200
    reloj.ahora = CLASE
    cliente.post("/api/asistencia", json={"materia": MATERIA, "fecha": "2026-03-04", "estado": asistencia})


def revisar(cliente, **datos):
    return cliente.post("/api/revision-tareas/1/revision", json=datos)


def test_listar_muestra_pendiente_cuando_no_hay_entrega(cliente):
    datos = cliente.get("/api/revision-tareas").get_json()
    assert [(r["numero"], r["estado"], r["fecha_entrega"]) for r in datos["revisiones"]] == [(1, "Pendiente", None)]


def test_estado_de_una_tarea_a_tiempo_y_puntual(cliente, reloj):
    entregar_y_asistir(cliente, reloj)
    datos = cliente.get("/api/revision-tareas/1").get_json()
    assert datos["estado"] == "Pendiente de revisión" and datos["puntualidad"] == "Puntual"
    assert datos["fecha_entrega"] == ANTES.isoformat() and datos["a_tiempo"] is True


def test_estado_con_llegada_tardia_explica_el_motivo(cliente, reloj):
    entregar_y_asistir(cliente, reloj, "Atraso")
    datos = cliente.get("/api/revision-tareas/1").get_json()
    assert datos["estado"] == "No revisada" and datos["motivo"] == "No revisada: llegada tardía"


def test_la_fecha_de_entrega_no_se_puede_enviar_desde_el_frontend(cliente, reloj):
    entregar_y_asistir(cliente, reloj)
    revisar(cliente, con_errores=True, observaciones="Falta", fecha_entrega="2020-01-01T00:00:00")
    cliente.post("/api/revision-tareas/1/reentrega", json={"archivos": ["b.pdf"], "fecha_hora_entrega": "2020-01-01T00:00:00"})
    assert cliente.get("/api/revision-tareas/1").get_json()["fecha_entrega"] == CLASE.isoformat()


def test_revision_sin_errores(cliente, reloj):
    entregar_y_asistir(cliente, reloj)
    datos = revisar(cliente, con_errores=False, observaciones="Muy bien").get_json()
    assert datos["estado"] == "Revisada" and datos["reentrega_habilitada"] is False


def test_revision_con_errores_habilita_la_reentrega(cliente, reloj):
    entregar_y_asistir(cliente, reloj)
    datos = revisar(cliente, con_errores=True, observaciones="Falta el punto 2").get_json()
    assert datos["estado"] == "Reentrega" and datos["reentrega_habilitada"] is True
    assert datos["observaciones"] == "Falta el punto 2"


def test_revisar_una_tarea_no_revisable_da_error(cliente, reloj):
    entregar_y_asistir(cliente, reloj, "Atraso")
    respuesta = revisar(cliente, con_errores=False)
    assert respuesta.status_code == 400 and "no se puede revisar" in respuesta.get_json()["error"]


@pytest.mark.parametrize("cuerpo", [{}, {"con_errores": "si"}, {"con_errores": True}, {"con_errores": True, "observaciones": 5}])
def test_revision_valida_los_datos_recibidos(cliente, reloj, cuerpo):
    entregar_y_asistir(cliente, reloj)
    assert cliente.post("/api/revision-tareas/1/revision", json=cuerpo).status_code == 400


def test_cuerpo_que_no_es_json_da_error_de_datos(cliente):
    assert cliente.post("/api/revision-tareas/1/revision", data="no es json").status_code == 400
    assert cliente.post("/api/revision-tareas/1/reentrega", data="no es json").status_code == 400


def test_tarea_inexistente_da_error(cliente):
    assert cliente.get("/api/revision-tareas/99").status_code == 400
    assert cliente.get("/api/revision-tareas/99/historial").status_code == 400


def test_reentrega_con_pdf_reemplaza_la_entrega_y_pasa_a_pendiente_de_revision(cliente, reloj):
    entregar_y_asistir(cliente, reloj)
    revisar(cliente, con_errores=True, observaciones="Falta el punto 2")
    reloj.ahora = REENTREGA
    respuesta = cliente.post("/api/revision-tareas/1/reentrega", json={"archivos": ["b.pdf"]})
    assert respuesta.status_code == 200
    datos = respuesta.get_json()["revision"]
    assert datos["estado"] == "Pendiente de revisión" and datos["archivos"] == ["b.pdf"]
    assert datos["fecha_entrega"] == REENTREGA.isoformat() and datos["version"] == 2
    assert cliente.get("/api/tareas/1").get_json()["entrega"]["archivos"] == ["b.pdf"]


def test_reentrega_rechaza_archivos_que_no_son_pdf(cliente, reloj):
    entregar_y_asistir(cliente, reloj)
    revisar(cliente, con_errores=True, observaciones="Falta")
    respuesta = cliente.post("/api/revision-tareas/1/reentrega", json={"archivos": ["b.zip"]})
    assert respuesta.status_code == 400 and "PDF" in respuesta.get_json()["error"]
    assert cliente.get("/api/revision-tareas/1").get_json()["archivos"] == ["a.pdf"]


def test_reentrega_bloqueada_si_el_estudiante_esta_ausente(cliente, reloj):
    entregar_y_asistir(cliente, reloj)
    revisar(cliente, con_errores=True, observaciones="Falta")
    cliente.post("/api/asistencia", json={"materia": MATERIA, "fecha": "2026-03-04", "estado": "Ausente"})
    respuesta = cliente.post("/api/revision-tareas/1/reentrega", json={"archivos": ["b.pdf"]})
    assert respuesta.status_code == 400 and "no tienes asistencia registrada como presente" in respuesta.get_json()["error"]


def test_reentrega_de_una_tarea_sin_errores_no_se_permite(cliente, reloj):
    entregar_y_asistir(cliente, reloj)
    revisar(cliente, con_errores=False)
    assert cliente.post("/api/revision-tareas/1/reentrega", json={"archivos": ["b.pdf"]}).status_code == 400


def test_historial_devuelve_las_versiones(cliente, reloj):
    entregar_y_asistir(cliente, reloj)
    revisar(cliente, con_errores=True, observaciones="Falta el punto 2")
    cliente.post("/api/revision-tareas/1/reentrega", json={"archivos": ["b.pdf"]})
    versiones = cliente.get("/api/revision-tareas/1/historial").get_json()["versiones"]
    assert [(v["version"], v["archivos"], v["vigente"]) for v in versiones] == [(1, ["a.pdf"], False), (2, ["b.pdf"], True)]
    assert versiones[0]["observaciones"] == "Falta el punto 2"


def test_el_estado_se_actualiza_solo_cuando_cambia_la_asistencia(cliente, reloj):
    entregar_y_asistir(cliente, reloj)
    assert cliente.get("/api/revision-tareas/1").get_json()["estado"] == "Pendiente de revisión"
    cliente.post("/api/asistencia", json={"materia": MATERIA, "fecha": "2026-03-04", "estado": "Atraso"})
    assert cliente.get("/api/revision-tareas/1").get_json()["estado"] == "No revisada"


def test_los_datos_persisten_al_reiniciar_la_aplicacion(ruta, reloj):
    primera = crear_app(ruta, ahora=reloj).test_client()
    entregar_y_asistir(primera, reloj)
    revisar(primera, con_errores=True, observaciones="Falta el punto 2")
    primera.post("/api/revision-tareas/1/reentrega", json={"archivos": ["b.pdf"]})
    revisar(primera, con_errores=True, observaciones="Otro detalle")
    segunda = crear_app(ruta, ahora=reloj).test_client()
    datos = segunda.get("/api/revision-tareas/1").get_json()
    assert (datos["estado"], datos["observaciones"], datos["archivos"]) == ("Reentrega", "Otro detalle", ["b.pdf"])
    assert len(segunda.get("/api/revision-tareas/1/historial").get_json()["versiones"]) == 2


def test_la_pagina_de_revision_se_sirve(cliente):
    respuesta = cliente.get("/revision_tareas.html")
    assert respuesta.status_code == 200 and "Revisión de tareas" in respuesta.get_data(as_text=True)


def test_se_puede_reenviar_varias_veces_hasta_la_siguiente_clase(cliente, reloj):
    entregar_y_asistir(cliente, reloj)
    revisar(cliente, con_errores=True, observaciones="Falta")
    for dia, hora, nombre in ((5, 8, "b.pdf"), (5, 9, "c.pdf"), (6, 6, "d.pdf")):
        reloj.ahora = datetime(2026, 3, dia, hora, 0)
        assert cliente.post("/api/revision-tareas/1/reentrega", json={"archivos": [nombre]}).status_code == 200
    datos = cliente.get("/api/revision-tareas/1").get_json()
    assert datos["archivos"] == ["d.pdf"] and datos["version"] == 4 and datos["reentrega_habilitada"] is True


def test_en_la_siguiente_clase_la_reentrega_se_cierra(cliente, reloj):
    entregar_y_asistir(cliente, reloj)
    revisar(cliente, con_errores=True, observaciones="Falta")
    reloj.ahora = datetime(2026, 3, 6, 6, 45)
    respuesta = cliente.post("/api/revision-tareas/1/reentrega", json={"archivos": ["b.pdf"]})
    assert respuesta.status_code == 400 and "plazo terminó" in respuesta.get_json()["error"]
    datos = cliente.get("/api/revision-tareas/1").get_json()
    assert datos["reentrega_habilitada"] is False and "plazo terminó" in datos["mensaje_reentrega"]
    assert datos["plazo_reentrega"] == "2026-03-06T06:45:00"
