"""Control de lectura: el docente no siempre envía el texto, así que cada estudiante registra las fuentes que busca."""
from datetime import datetime

import pytest

from src.api.app import crear_app
from src.constantes import MSG_FUENTE_NO_EXISTE, MSG_FUENTE_SIN_TITULO
from src.modelo.apuntes_control_lectura import ApuntesControlLectura
from src.modelo.clase_lectura import ClaseLectura

AHORA = datetime(2026, 3, 3, 7, 0)
INICIO = "2026-03-03T06:45"
PLAZO = "2026-03-04T06:45"
ANA = "Ana Pérez"
EVA = "Eva Díaz"


@pytest.fixture
def cliente(tmp_path):
    app = crear_app(str(tmp_path / "fuentes.db"), ahora=lambda: AHORA, carpeta_pdf=str(tmp_path / "pdf"))
    cliente = app.test_client()
    cliente.post("/api/clases-lectura", json={"tema": "Clase libre", "inicio": INICIO, "cierre_respuesta": PLAZO,
                                              "ids_lecturas": [], "investigacion_libre": True})
    return cliente


def _fuente(cliente, titulo="Qué es un sistema", enlace="https://ejemplo.org/sistemas", estudiante=ANA):
    return cliente.post("/api/clases-lectura/1/fuentes", json={"estudiante": estudiante, "titulo": titulo, "enlace": enlace})


def test_una_clase_sin_textos_del_docente_solo_existe_si_es_investigacion_libre():
    with pytest.raises(ValueError):
        ClaseLectura(1, "T", AHORA, AHORA.replace(day=4), [])
    assert ClaseLectura(1, "T", AHORA, AHORA.replace(day=4), [], investigacion_libre=True).investigacion_libre


def test_la_regla_de_bibliografia_sigue_igual_si_no_se_marca_investigacion_libre(cliente):
    sin_biblio = cliente.post("/api/clases-lectura", json={"tema": "X", "inicio": INICIO, "cierre_respuesta": PLAZO, "ids_lecturas": []})
    assert sin_biblio.status_code == 400


def test_el_estudiante_registra_fuentes_propias_y_las_ve_en_la_clase(cliente):
    assert _fuente(cliente).status_code == 201
    assert _fuente(cliente, titulo="Video de clase", enlace="").get_json()["enlace"] is None
    detalle = cliente.get(f"/api/clases-lectura/1?estudiante={ANA}").get_json()
    assert detalle["investigacion_libre"] is True and detalle["bibliografia"] == []
    assert [f["titulo"] for f in detalle["fuentes"]] == ["Qué es un sistema", "Video de clase"]


def test_las_fuentes_son_privadas_de_cada_estudiante(cliente):
    _fuente(cliente)
    assert cliente.get(f"/api/clases-lectura/1?estudiante={EVA}").get_json()["fuentes"] == []


def test_la_fuente_exige_titulo_y_se_puede_editar(cliente):
    assert _fuente(cliente, titulo=" ").get_json() == {"error": MSG_FUENTE_SIN_TITULO}
    cliente.post("/api/clases-lectura/1/fuentes", json={"estudiante": ANA, "titulo": "Borrador"})
    editada = cliente.put("/api/clases-lectura/1/fuentes/1", json={"estudiante": ANA, "titulo": "Final", "enlace": "https://x.org"})
    assert editada.get_json()["titulo"] == "Final"
    assert cliente.put("/api/clases-lectura/1/fuentes/9", json={"estudiante": ANA, "titulo": "x"}).get_json() == {"error": MSG_FUENTE_NO_EXISTE}


def test_un_apunte_se_asocia_a_una_fuente_propia(cliente):
    _fuente(cliente)
    creado = cliente.post("/api/clases-lectura/1/apuntes", json={"estudiante": ANA, "id_fuente": 1, "texto": "Idea clave"})
    assert creado.status_code == 201 and creado.get_json()["id_fuente"] == 1
    apunte = cliente.get(f"/api/clases-lectura/1?estudiante={ANA}").get_json()["apuntes"][0]
    assert apunte["titulo_lectura"] == "Qué es un sistema"
    ajena = cliente.post("/api/clases-lectura/1/apuntes", json={"estudiante": ANA, "id_fuente": 7, "texto": "x"})
    assert ajena.get_json() == {"error": MSG_FUENTE_NO_EXISTE}
    sin_origen = cliente.post("/api/clases-lectura/1/apuntes", json={"estudiante": ANA, "texto": "x"})
    assert sin_origen.status_code == 400


def test_el_cuaderno_guardado_antes_de_las_fuentes_sigue_cargando():
    viejo = {"id_clase": 1, "estudiante": ANA, "apuntes": [{"id": 1, "id_lectura": 2, "texto": "a", "creado": "x", "actualizado": "x"}], "dudas": []}
    cuaderno = ApuntesControlLectura.desdeDiccionario(viejo)
    assert cuaderno.fuentes == [] and cuaderno.apuntes[0]["id_fuente"] is None
