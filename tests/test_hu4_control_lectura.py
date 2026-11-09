"""HU4 - Control de lectura: un test por criterio de aceptación (flujo real API + servicio + SQLite)."""
from datetime import datetime
from pathlib import Path

import pytest

from src.api.app import crear_app
from src.repositorio.repositorio_memoria import RepositorioMemoria
from src.servicio.servicio_control_lectura import ErrorGuardado, ServicioControlLectura

ANTES_DE_ABRIR = datetime(2026, 3, 2, 8, 0)
ABIERTO = datetime(2026, 3, 3, 10, 0)
DESPUES_DE_CERRAR = datetime(2026, 3, 5, 9, 0)
APERTURA = "2026-03-03T08:00"
CIERRE = "2026-03-04T06:45"
ANA = "Ana Pérez"

LECTURA = {"titulo": "Sistemas y complejidad", "autor": "Bertalanffy", "enlace": "https://ejemplo.org/lectura"}
PREGUNTAS = [{"enunciado": "¿Qué es un sistema?", "obligatoria": True},
             {"enunciado": "Comentario libre", "obligatoria": False}]


@pytest.fixture
def entorno(tmp_path):
    reloj = {"ahora": ABIERTO}
    cliente = crear_app(str(tmp_path / "hu4.db"), ahora=lambda: reloj["ahora"]).test_client()
    cliente.post("/api/lecturas", json=LECTURA)
    cliente.post("/api/controles-lectura", json={
        "titulo": "Control 1", "id_lectura": 1, "preguntas": PREGUNTAS,
        "apertura": APERTURA, "cierre": CIERRE, "puntaje_maximo": 10})
    return cliente, reloj


def _enviar(cliente, respuestas=("Un conjunto de partes", ""), estudiante=ANA):
    return cliente.post("/api/controles-lectura/1/respuestas",
                        json={"estudiante": estudiante, "respuestas": list(respuestas)})


def test_c1_el_docente_registra_la_lectura_y_el_estudiante_la_ve_asociada_al_control(entorno):
    cliente, _ = entorno
    lecturas = cliente.get("/api/lecturas").get_json()
    assert lecturas[0]["titulo"] == "Sistemas y complejidad"
    assert lecturas[0]["autor"] == "Bertalanffy"
    assert lecturas[0]["enlace"] == "https://ejemplo.org/lectura"
    detalle = cliente.get(f"/api/controles-lectura/1?estudiante={ANA}").get_json()
    assert detalle["lectura"]["titulo"] == "Sistemas y complejidad"
    assert cliente.post("/api/lecturas", json={"titulo": "X", "autor": "Y"}).status_code == 400   # sin archivo ni enlace
    sin_lectura = cliente.post("/api/controles-lectura", json={
        "titulo": "Sin lectura", "preguntas": PREGUNTAS, "apertura": APERTURA, "cierre": CIERRE})
    assert sin_lectura.get_json() == {"error": "El control debe estar asociado a una lectura"}


def test_c2_el_docente_publica_el_control_con_preguntas_apertura_y_cierre(entorno):
    cliente, _ = entorno
    control = cliente.get(f"/api/controles-lectura/1?estudiante={ANA}").get_json()
    assert [p["enunciado"] for p in control["preguntas"]] == ["¿Qué es un sistema?", "Comentario libre"]
    assert control["apertura"] == "2026-03-03T08:00:00" and control["cierre"] == "2026-03-04T06:45:00"
    invalido = cliente.post("/api/controles-lectura", json={
        "titulo": "Malo", "id_lectura": 1, "preguntas": PREGUNTAS, "apertura": CIERRE, "cierre": APERTURA})
    assert invalido.status_code == 400
    sin_preguntas = cliente.post("/api/controles-lectura", json={
        "titulo": "Vacío", "id_lectura": 1, "preguntas": [], "apertura": APERTURA, "cierre": CIERRE})
    assert sin_preguntas.get_json() == {"error": "El control debe tener al menos una pregunta"}


def test_c3_solo_se_responde_mientras_el_control_esta_habilitado(entorno):
    cliente, reloj = entorno
    for momento in (ANTES_DE_ABRIR, DESPUES_DE_CERRAR):
        reloj["ahora"] = momento
        assert cliente.get(f"/api/controles-lectura/1?estudiante={ANA}").get_json()["puede_responder"] is False
        respuesta = _enviar(cliente)
        assert respuesta.status_code == 400
        assert respuesta.get_json() == {"error": "El control de lectura no está habilitado para responder"}
    reloj["ahora"] = ABIERTO
    assert cliente.get(f"/api/controles-lectura/1?estudiante={ANA}").get_json()["puede_responder"] is True
    assert _enviar(cliente).status_code == 200


def test_c4_el_sistema_muestra_las_preguntas_con_un_campo_de_respuesta_por_pregunta(entorno):
    cliente, _ = entorno
    control = cliente.get(f"/api/controles-lectura/1?estudiante={ANA}").get_json()
    assert len(control["preguntas"]) == 2
    assert _enviar(cliente, respuestas=["solo una"]).status_code == 400    # debe haber una respuesta por pregunta
    # El formulario web genera un campo por pregunta
    pagina = (Path(__file__).resolve().parents[1] / "web" / "js" / "vista_control_lectura.js").open(encoding="utf-8").read()
    assert "textarea" in pagina and "preguntas.map" in pagina


def test_c5_no_se_envia_si_una_pregunta_obligatoria_esta_sin_responder(entorno):
    cliente, _ = entorno
    respuesta = _enviar(cliente, respuestas=["   ", "algo"])
    assert respuesta.status_code == 400
    assert respuesta.get_json() == {"error": "Falta responder la pregunta obligatoria 1"}
    assert cliente.get(f"/api/controles-lectura/1?estudiante={ANA}").get_json()["estado"] == "Pendiente"
    assert _enviar(cliente, respuestas=["ok", ""]).status_code == 200     # la opcional puede ir vacía


def test_c6_guarda_respuestas_con_estudiante_lectura_y_fecha_hora_exacta(entorno):
    cliente, reloj = entorno
    reloj["ahora"] = datetime(2026, 3, 3, 10, 15, 42)
    assert _enviar(cliente).status_code == 200
    fila = cliente.get("/api/controles-lectura/1/revision").get_json()["estudiantes"][0]
    assert fila["estudiante"] == ANA
    assert fila["titulo_lectura"] == "Sistemas y complejidad" and fila["id_lectura"] == 1
    assert fila["respuestas"] == ["Un conjunto de partes", ""]
    assert fila["fecha_hora_envio"] == "2026-03-03T10:15:42"


def test_c7_clasifica_el_envio_como_a_tiempo_o_tarde(entorno):
    cliente, reloj = entorno
    assert _enviar(cliente).get_json()["puntualidad"] == "Enviada a tiempo"
    # Con un nuevo intento autorizado después del cierre, el envío queda como tardío.
    cliente.post("/api/controles-lectura/1/nuevo-intento", json={"estudiante": ANA})
    reloj["ahora"] = DESPUES_DE_CERRAR
    assert _enviar(cliente).get_json()["puntualidad"] == "Enviada tarde"


def test_c8_si_el_guardado_falla_no_queda_enviado_y_se_muestra_error():
    class RepositorioQueFalla(RepositorioMemoria):
        def guardar(self, clave, dato):
            raise OSError("disco lleno")

    servicio = ServicioControlLectura(RepositorioMemoria(), RepositorioMemoria(), RepositorioMemoria(), RepositorioMemoria())
    servicio.registrarLectura(LECTURA)
    servicio.publicarControl({"titulo": "C", "id_lectura": 1, "preguntas": PREGUNTAS,
                              "apertura": APERTURA, "cierre": CIERRE})
    servicio._repo_respuestas = RepositorioQueFalla()
    with pytest.raises(ErrorGuardado) as error:
        servicio.enviarRespuestas(1, ANA, ["x", ""], ABIERTO)
    assert "No se pudieron guardar tus respuestas" in str(error.value)
    servicio._repo_respuestas = RepositorioMemoria()
    assert servicio.obtenerControl(1, ANA, ABIERTO)["estado"] == "Pendiente"


def test_c8_la_api_responde_con_error_de_guardado(entorno, monkeypatch):
    cliente, _ = entorno
    monkeypatch.setattr(ServicioControlLectura, "_guardarRespuesta",
                        lambda self, respuesta: (_ for _ in ()).throw(OSError("fallo")))
    respuesta = _enviar(cliente)
    assert respuesta.status_code == 500
    assert "No se pudieron guardar" in respuesta.get_json()["error"]


def test_c9_si_el_guardado_es_correcto_hay_confirmacion_y_el_estado_pasa_a_respondido(entorno):
    cliente, reloj = entorno
    reloj["ahora"] = datetime(2026, 3, 3, 10, 15, 42)
    respuesta = _enviar(cliente).get_json()
    assert respuesta["mensaje"] == "Respuestas enviadas el 03/03/2026 a las 10:15:42"
    assert respuesta["estado"] == "Respondido"
    assert cliente.get(f"/api/controles-lectura?estudiante={ANA}").get_json()[0]["estado"] == "Respondido"


def test_c10_un_solo_intento_salvo_que_el_docente_habilite_otro_que_reemplaza_al_anterior(entorno):
    cliente, _ = entorno
    assert _enviar(cliente, respuestas=["primera", ""]).status_code == 200
    repetido = _enviar(cliente, respuestas=["segunda", ""])
    assert repetido.status_code == 400
    assert "Ya enviaste este control" in repetido.get_json()["error"]
    cliente.post("/api/controles-lectura/1/calificacion", json={"estudiante": ANA, "nota": 7, "publicar": True})
    cliente.post("/api/controles-lectura/1/nuevo-intento", json={"estudiante": ANA})
    assert _enviar(cliente, respuestas=["segunda", ""]).status_code == 200
    fila = cliente.get("/api/controles-lectura/1/revision").get_json()["estudiantes"][0]
    assert fila["respuestas"] == ["segunda", ""] and fila["intentos"] == 2
    assert fila["nota"] is None                                  # el nuevo intento reemplaza al anterior por completo
    assert _enviar(cliente).status_code == 400                   # y vuelve a quedar un solo intento


def test_c11_el_docente_ve_estudiantes_con_estado_y_registra_calificacion_y_retroalimentacion(entorno):
    cliente, reloj = entorno
    cliente.post("/api/controles-lectura/estudiantes", json={"nombre": "Luis Rojas"})     # entró y no respondió
    _enviar(cliente)
    cliente.post("/api/controles-lectura/1/nuevo-intento", json={"estudiante": "Eva Díaz"})
    reloj["ahora"] = DESPUES_DE_CERRAR
    _enviar(cliente, estudiante="Eva Díaz")                                                # tarde
    estados = {f["estudiante"]: f["estado_revision"]
               for f in cliente.get("/api/controles-lectura/1/revision").get_json()["estudiantes"]}
    assert estados == {ANA: "Respondido", "Eva Díaz": "Tarde", "Luis Rojas": "Pendiente"}
    ok = cliente.post("/api/controles-lectura/1/calificacion",
                      json={"estudiante": ANA, "nota": "8.5", "retroalimentacion": "Buen trabajo"})
    assert ok.status_code == 200
    fila = next(f for f in cliente.get("/api/controles-lectura/1/revision").get_json()["estudiantes"]
                if f["estudiante"] == ANA)
    assert fila["nota"] == "8.5" and fila["retroalimentacion"] == "Buen trabajo"
    assert cliente.post("/api/controles-lectura/1/calificacion", json={"estudiante": ANA, "nota": 11}).status_code == 400
    pendiente = cliente.post("/api/controles-lectura/1/calificacion", json={"estudiante": "Luis Rojas", "nota": 5})
    assert pendiente.get_json() == {"error": "Solo se puede calificar un control que ya fue respondido"}


def test_c12_el_estudiante_ve_calificacion_y_retroalimentacion_solo_cuando_el_docente_las_publica(entorno):
    cliente, _ = entorno
    _enviar(cliente)
    cliente.post("/api/controles-lectura/1/calificacion",
                 json={"estudiante": ANA, "nota": 9, "retroalimentacion": "Muy bien", "publicar": False})
    oculto = cliente.get(f"/api/controles-lectura/1?estudiante={ANA}").get_json()
    assert oculto["nota"] is None and oculto["retroalimentacion"] is None
    cliente.post("/api/controles-lectura/1/calificacion",
                 json={"estudiante": ANA, "nota": 9, "retroalimentacion": "Muy bien", "publicar": True})
    visible = cliente.get(f"/api/controles-lectura/1?estudiante={ANA}").get_json()
    assert visible["nota"] == "9" and visible["retroalimentacion"] == "Muy bien"