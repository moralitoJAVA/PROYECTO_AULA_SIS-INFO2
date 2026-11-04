"""HU2 - Entrega de tareas y consulta de calificaciones: un test por criterio de aceptación."""
import sqlite3
from datetime import datetime

import pytest

from src.api.app import crear_app
from src.modelo.rubrica import Rubrica
from src.modelo.tarea_grupal import TareaGrupal
from src.modelo.tarea_individual import TareaIndividual
from src.repositorio.repositorio_sqlite import RepositorioSqlite

REGISTRO = datetime(2026, 3, 1, 10, 0)
LIMITE_1 = datetime(2026, 3, 4, 6, 45)    # miércoles
LIMITE_2 = datetime(2026, 3, 6, 6, 45)    # viernes
LIMITE_3 = datetime(2026, 3, 10, 6, 45)   # martes
AHORA = datetime(2026, 3, 2, 12, 0)


def _rubrica():
    rubrica = Rubrica()
    rubrica.agregarCriterio("codigo", 60)
    rubrica.agregarCriterio("informe", 40)
    return rubrica


@pytest.fixture
def entorno(tmp_path):
    ruta = str(tmp_path / "hu2.db")
    repo = RepositorioSqlite(sqlite3.connect(ruta), "tareas")
    tareas = [
        TareaIndividual(1, "Individual A", "Resolver", LIMITE_2, ruta_adjunto="/guias/t1.pdf", rubrica=_rubrica()),
        TareaGrupal(2, "Grupal B", "En equipo", LIMITE_3, tamano_equipo=3, ruta_adjunto="/guias/t2.pdf", rubrica=_rubrica()),
        TareaIndividual(3, "Individual C", "Urgente", LIMITE_1, ruta_adjunto="/guias/t3.pdf", rubrica=_rubrica()),
    ]
    for tarea in tareas:
        tarea.registrar(REGISTRO)
        tarea.guardar(repo)
    reloj = {"ahora": AHORA}
    cliente = crear_app(ruta, ahora=lambda: reloj["ahora"]).test_client()
    return cliente, reloj


def test_c1_panel_por_estado_ordenado_por_fecha_limite(entorno):
    cliente, _ = entorno
    cliente.post("/api/tareas/1/entrega", json={"archivos": ["a.zip"]})
    cliente.post("/api/tareas/1/calificacion", json={"nota": "80", "escala": "0-100"})
    pendientes = cliente.get("/api/tareas?estado=Pendiente").get_json()["tareas"]
    assert [t["numero"] for t in pendientes] == [3, 2]          # miércoles 4 antes que martes 10
    assert [t["numero"] for t in cliente.get("/api/tareas?estado=Calificada").get_json()["tareas"]] == [1]
    assert cliente.get("/api/tareas?estado=Entregada").get_json()["tareas"] == []


def test_c2_detalle_con_puntaje_maximo_y_recurso_adjunto(entorno):
    cliente, _ = entorno
    detalle = cliente.get("/api/tareas/1").get_json()
    assert detalle["puntaje_maximo"] == "100"
    assert detalle["tarea"]["ruta_adjunto"] == "/guias/t1.pdf"
    assert detalle["tarea"]["instrucciones"] == "Resolver"


def test_c3_subir_varios_archivos_y_enlaces_antes_del_limite(entorno):
    cliente, _ = entorno
    r = cliente.post("/api/tareas/1/entrega", json={"archivos": ["a.zip", "b.pdf"], "enlaces": ["https://git.example/x"]})
    assert r.status_code == 200
    entrega = cliente.get("/api/tareas/1").get_json()["entrega"]
    assert entrega["archivos"] == ["a.zip", "b.pdf"] and entrega["enlaces"] == ["https://git.example/x"]


def test_c3_rechaza_fuera_de_plazo_y_sin_adjuntos(entorno):
    cliente, reloj = entorno
    assert cliente.post("/api/tareas/1/entrega", json={}).status_code == 400
    reloj["ahora"] = datetime(2026, 3, 6, 6, 46)
    r = cliente.post("/api/tareas/1/entrega", json={"archivos": ["a.zip"]})
    assert r.status_code == 400 and "venció" in r.get_json()["error"]
    assert cliente.get("/api/tareas/1").get_json()["entrega"]["estado"] == "Pendiente"


def test_c4_confirma_con_fecha_y_hora_exacta_y_cambia_a_entregado(entorno):
    cliente, reloj = entorno
    reloj["ahora"] = datetime(2026, 3, 3, 21, 5, 9)
    mensaje = cliente.post("/api/tareas/1/entrega", json={"archivos": ["a.zip"]}).get_json()["mensaje"]
    assert mensaje == "Entrega confirmada el 03/03/2026 a las 21:05:09"
    entrega = cliente.get("/api/tareas/1").get_json()["entrega"]
    assert entrega["estado"] == "Entregada" and entrega["fecha_hora_entrega"] == "2026-03-03T21:05:09"


def test_c5_registrar_nota_escala_y_comentarios_visibles_en_el_historial(entorno):
    cliente, _ = entorno
    cliente.post("/api/tareas/1/entrega", json={"archivos": ["a.zip"]})
    cliente.post("/api/tareas/1/calificacion", json={"nota": "85.5", "escala": "0-100", "comentarios": "Buen trabajo"})
    entrega = cliente.get("/api/tareas/1").get_json()["entrega"]
    assert (entrega["nota"], entrega["escala"], entrega["comentarios"]) == ("85.5", "0-100", "Buen trabajo")
    fila = [t for t in cliente.get("/api/tareas").get_json()["tareas"] if t["numero"] == 1][0]
    assert fila["nota"] == "85.5" and fila["estado"] == "Calificada"


def test_c5_rechaza_nota_fuera_de_rango_y_tarea_no_entregada(entorno):
    cliente, _ = entorno
    assert cliente.post("/api/tareas/1/calificacion", json={"nota": "50", "escala": "0-100"}).status_code == 400
    cliente.post("/api/tareas/1/entrega", json={"archivos": ["a.zip"]})
    assert cliente.post("/api/tareas/1/calificacion", json={"nota": "101", "escala": "0-100"}).status_code == 400


def test_c6_advertencia_si_falta_menos_de_24_horas(entorno):
    cliente, reloj = entorno
    assert cliente.get("/api/tareas").get_json()["por_vencer"] == []
    reloj["ahora"] = datetime(2026, 3, 3, 8, 0)               # faltan 22 h 45 min para la tarea 3
    assert cliente.get("/api/tareas").get_json()["por_vencer"] == [3]
    cliente.post("/api/tareas/3/entrega", json={"archivos": ["a.zip"]})
    assert cliente.get("/api/tareas").get_json()["por_vencer"] == []   # ya entregada: sin advertencia


def test_c7_el_panel_distingue_individuales_y_grupales(entorno):
    cliente, _ = entorno
    tipos = {t["numero"]: t["tipo"] for t in cliente.get("/api/tareas").get_json()["tareas"]}
    assert tipos == {1: "Individual", 2: "Grupal", 3: "Individual"}


def test_c8_un_integrante_entrega_por_el_equipo_y_queda_entregada(entorno):
    cliente, _ = entorno
    r = cliente.post("/api/tareas/2/entrega-equipo", json={
        "integrantes": ["Ana", "Luis", "Eva"], "estudiante": "Luis", "archivos": ["eq.zip"]})
    assert r.status_code == 200
    detalle = cliente.get("/api/tareas/2").get_json()
    assert detalle["entrega"]["estado"] == "Entregada"
    assert detalle["equipo"]["integrantes"] == ["Ana", "Luis", "Eva"]
    assert cliente.post("/api/tareas/2/entrega-equipo", json={
        "integrantes": ["Ana", "Luis", "Eva"], "estudiante": "Ana", "archivos": ["otro.zip"]}).status_code == 400
    assert cliente.post("/api/tareas/2/entrega-equipo", json={
        "integrantes": ["Ana", "Luis"], "estudiante": "Ana", "archivos": ["x.zip"]}).status_code == 400


def test_c9_penaliza_al_integrante_que_incumple_y_muestra_el_motivo(entorno):
    cliente, _ = entorno
    r = cliente.post("/api/tareas/2/entrega-equipo", json={
        "integrantes": ["Ana", "Luis", "Eva"], "estudiante": "Ana", "incumplen": ["Ana", "Eva"], "archivos": ["eq.zip"]}).get_json()
    assert r["descuento"] == "20"
    assert "Ana, Eva" in r["motivo"]
    cliente.post("/api/tareas/2/calificacion", json={"nota": "90", "escala": "0-100"})
    detalle = cliente.get("/api/tareas/2").get_json()
    assert "Ana, Eva" in detalle["penalizacion"]["motivo"]
    fila = [t for t in cliente.get("/api/tareas").get_json()["tareas"] if t["numero"] == 2][0]
    assert (fila["nota"], fila["descuento"], fila["nota_final"]) == ("90", "20", "72.00")


def test_c9_la_penalizacion_respeta_el_tope(entorno):
    cliente, _ = entorno
    r = cliente.post("/api/tareas/2/entrega-equipo", json={
        "integrantes": ["Ana", "Luis", "Eva"], "estudiante": "Ana", "incumplen": ["Ana", "Luis", "Eva"], "archivos": ["e.zip"]})
    assert r.get_json()["descuento"] == "30"


def test_c10_historial_de_individuales_y_grupales_con_nota_final(entorno):
    cliente, _ = entorno
    cliente.post("/api/tareas/1/entrega", json={"archivos": ["a.zip"]})
    cliente.post("/api/tareas/1/calificacion", json={"nota": "80", "escala": "0-100"})
    historial = cliente.get("/api/tareas").get_json()["tareas"]
    assert [t["numero"] for t in historial] == [3, 1, 2]       # ordenado por fecha límite
    assert {t["tipo"] for t in historial} == {"Individual", "Grupal"}
    assert [t["nota_final"] for t in historial] == [None, "80.00", None]


def test_c11_apuntes_vinculados_a_cada_tarea(entorno):
    cliente, _ = entorno
    cliente.post("/api/apuntes", json={"vinculo": "tarea-1", "texto": "repasar listas"})
    cliente.post("/api/apuntes", json={"vinculo": "tarea-2", "texto": "dividir el trabajo"})
    assert [a["texto"] for a in cliente.get("/api/apuntes?vinculo=tarea-1").get_json()] == ["repasar listas"]
    assert cliente.post("/api/apuntes", json={"vinculo": "tarea-1", "texto": "  "}).status_code == 400


def test_persistencia_en_las_tablas_de_hu2(entorno, tmp_path):
    cliente, _ = entorno
    cliente.post("/api/tareas/2/entrega-equipo", json={
        "integrantes": ["Ana", "Luis", "Eva"], "estudiante": "Ana", "incumplen": ["Eva"], "archivos": ["e.zip"]})
    cliente.post("/api/apuntes", json={"vinculo": "tarea-2", "texto": "x"})
    ruta = str(tmp_path / "hu2.db")
    conexion = sqlite3.connect(ruta)
    for tabla in ("entregas", "equipos", "penalizaciones", "apuntes"):
        assert conexion.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0] == 1