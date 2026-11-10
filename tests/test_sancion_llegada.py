import sqlite3
from datetime import date, datetime, time

import pytest

from src.api.app import crear_app
from src.modelo.rubrica import Rubrica
from src.modelo.sancion_llegada import SancionLlegada
from src.modelo.tarea_individual import TareaIndividual
from src.repositorio.repositorio_sqlite import RepositorioSqlite

MATERIA = "Sistemas de Información 2"
MARTES = datetime(2026, 3, 3, 6, 50)      # clase
MIERCOLES = datetime(2026, 3, 4, 7, 10)   # clase
JUEVES = datetime(2026, 3, 5, 7, 10)      # sin clase
LIMITE_TAREA = datetime(2026, 3, 4, 6, 45)


# ---------- modelo (criterios 1 a 3) ----------
@pytest.mark.parametrize("dia, hora, esperado", [
    (1, time(7, 0), "Puntual"),
    (2, time(6, 45), "Puntual"),
    (4, time(7, 0), "Puntual"),
    (1, time(7, 1), "Debe fruta"),
    (2, time(8, 14), "Debe fruta"),
    (0, time(6, 50), "Día sin clases"),
    (3, time(7, 5), "Día sin clases"),
    (1, time(6, 44), "Fuera de horario"),
    (1, time(8, 15), "Fuera de horario"),
])
def test_evaluar_ingreso(dia, hora, esperado):
    assert SancionLlegada().evaluar_ingreso(dia, hora) == esperado


def test_proxima_clase_salta_los_dias_sin_clase():
    sancion = SancionLlegada()
    assert sancion.proxima_clase(date(2026, 3, 3)) == date(2026, 3, 4)   # martes -> miércoles
    assert sancion.proxima_clase(date(2026, 3, 4)) == date(2026, 3, 6)   # miércoles -> viernes
    assert sancion.proxima_clase(date(2026, 3, 6)) == date(2026, 3, 10)  # viernes -> martes


# ---------- API ----------
class Reloj:
    def __init__(self, ahora):
        self.ahora = ahora

    def __call__(self):
        return self.ahora


@pytest.fixture
def reloj():
    return Reloj(MARTES)


@pytest.fixture
def cliente(tmp_path, reloj):
    ruta = str(tmp_path / "prueba.db")
    rubrica = Rubrica()
    rubrica.agregarCriterio("codigo", 100)
    tarea = TareaIndividual(1, "Tarea 1", "x", LIMITE_TAREA, ruta_adjunto="g.pdf", rubrica=rubrica)
    tarea.registrar(datetime(2026, 3, 1, 10, 0))
    tarea.guardar(RepositorioSqlite(sqlite3.connect(ruta), "tareas"))
    return crear_app(ruta, ahora=reloj).test_client()


def test_ingreso_puntual_usa_la_hora_actual_y_no_genera_sancion(cliente):
    datos = cliente.post("/api/asistencia/ingreso", json={"materia": MATERIA}).get_json()
    assert datos["estado"] == "Puntual" and datos["hora_ingreso"] == "06:50:00" and datos["debe_fruta"] is False
    assert datos["fruta_para"] is None


def test_ingreso_tardio_debe_fruta_para_la_proxima_clase(cliente):
    datos = cliente.post("/api/asistencia/ingreso", json={"materia": MATERIA, "fecha": "2026-03-04T07:10:00"}).get_json()
    assert datos["estado"] == "Debe fruta" and datos["fruta_para"] == "2026-03-06"
    assert "2026" in datos["mensaje"] and "fruta" in datos["mensaje"]


def test_el_ingreso_queda_en_la_asistencia(cliente):
    cliente.post("/api/asistencia/ingreso", json={"materia": MATERIA, "fecha": "2026-03-04T07:10:00"})
    cliente.post("/api/asistencia/ingreso", json={"materia": MATERIA, "fecha": "2026-03-03T06:50:00"})
    historial = cliente.get("/api/asistencia/panel").get_json()["historial"]
    assert historial == [["2026-03-03", "Presente"], ["2026-03-04", "Atraso"]]


def test_rechaza_dia_sin_clase_fuera_de_horario_y_fecha_invalida(cliente):
    sin_clase = cliente.post("/api/asistencia/ingreso", json={"fecha": JUEVES.isoformat()})
    assert sin_clase.status_code == 400 and "día de clase" in sin_clase.get_json()["error"]
    tarde = cliente.post("/api/asistencia/ingreso", json={"fecha": "2026-03-03T09:00:00"})
    assert tarde.status_code == 400 and "06:45 a 08:14" in tarde.get_json()["error"]
    invalida = cliente.post("/api/asistencia/ingreso", json={"fecha": "ayer"})
    assert invalida.status_code == 400 and "no son válidas" in invalida.get_json()["error"]
    assert cliente.get("/api/asistencia/ingresos").get_json()["ingresos"] == []


def test_no_se_puede_registrar_dos_veces_el_ingreso_de_una_clase(cliente):
    assert cliente.post("/api/asistencia/ingreso", json={}).status_code == 200
    segundo = cliente.post("/api/asistencia/ingreso", json={"fecha": "2026-03-03T07:30:00"})
    assert segundo.status_code == 400 and "Ya registraste" in segundo.get_json()["error"]
    assert cliente.get("/api/asistencia/ingresos").get_json()["ingresos"][0]["estado"] == "Puntual"


def test_ingresos_lista_el_historial_y_la_fruta_pendiente(cliente, reloj):
    cliente.post("/api/asistencia/ingreso", json={"fecha": "2026-03-03T06:50:00"})
    cliente.post("/api/asistencia/ingreso", json={"fecha": "2026-03-04T07:10:00"})
    reloj.ahora = datetime(2026, 3, 5, 12, 0)
    datos = cliente.get("/api/asistencia/ingresos").get_json()
    assert [i["fecha"] for i in datos["ingresos"]] == ["2026-03-04", "2026-03-03"]
    assert datos["fruta_pendiente"]["fruta_para"] == "2026-03-06"
    reloj.ahora = datetime(2026, 3, 7, 12, 0)
    assert cliente.get("/api/asistencia/ingresos").get_json()["fruta_pendiente"] is None


def test_evaluar_sancion_no_guarda_nada(cliente):
    datos = cliente.post("/api/asistencia/evaluar-sancion", json={"fecha": JUEVES.isoformat()}).get_json()
    assert datos["estado"] == "Día sin clases"
    assert cliente.post("/api/asistencia/evaluar-sancion", json={"fecha": "2026-03-04T07:30:00"}).get_json()["estado"] == "Debe fruta"
    assert cliente.get("/api/asistencia/ingresos").get_json()["ingresos"] == []


# ---------- criterio 4: el estado lo usa la HU4 ----------
def test_la_hu4_usa_el_estado_de_puntualidad_de_la_hu1(cliente, reloj):
    reloj.ahora = datetime(2026, 3, 3, 20, 0)
    assert cliente.post("/api/tareas/1/entrega", json={"archivos": ["a.pdf"]}).status_code == 200
    cliente.post("/api/asistencia/ingreso", json={"fecha": "2026-03-04T07:10:00"})
    reloj.ahora = datetime(2026, 3, 4, 7, 30)
    revision = cliente.get("/api/revision-tareas/1").get_json()
    assert revision["puntualidad"] == "Tardío" and revision["estado"] == "No revisada"
    assert "llegada tardía" in revision["motivo"]


def test_la_hu4_revisa_cuando_el_ingreso_fue_puntual(cliente, reloj):
    reloj.ahora = datetime(2026, 3, 3, 20, 0)
    cliente.post("/api/tareas/1/entrega", json={"archivos": ["a.pdf"]})
    cliente.post("/api/asistencia/ingreso", json={"fecha": "2026-03-04T07:00:00"})
    reloj.ahora = datetime(2026, 3, 4, 7, 30)
    revision = cliente.get("/api/revision-tareas/1").get_json()
    assert revision["puntualidad"] == "Puntual" and revision["estado"] == "Pendiente de revisión"