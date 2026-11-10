"""HU3 - Apuntes, lectura y respuesta a pregunta de clase: un test por criterio de aceptación (API + servicio + SQLite)."""
from datetime import datetime

import pytest

from src.api.app import crear_app
from src.repositorio.almacen_pdf import AlmacenPdf
from src.repositorio.repositorio_memoria import RepositorioMemoria
from src.servicio.servicio_apuntes_lectura import ErrorGuardado, ServicioApuntesLectura

ANTES_DE_CLASE = datetime(2026, 3, 3, 6, 0)
EN_CLASE = datetime(2026, 3, 3, 7, 0)
DESPUES_DEL_PLAZO = datetime(2026, 3, 5, 9, 0)
INICIO = "2026-03-03T06:45"
PLAZO = "2026-03-04T06:45"
ANA = "Ana Pérez"
LIBRO_1 = {"titulo": "Sistemas y complejidad", "autor": "Bertalanffy", "enlace": "https://ejemplo.org/lectura"}
LIBRO_2 = {"titulo": "Teoría general de sistemas", "archivo": "/lecturas/tgs.pdf"}


@pytest.fixture
def entorno(tmp_path):
    reloj = {"ahora": EN_CLASE}
    app = crear_app(str(tmp_path / "hu3.db"), ahora=lambda: reloj["ahora"], carpeta_pdf=str(tmp_path / "pdf"))
    cliente = app.test_client()
    cliente.post("/api/lecturas", json=LIBRO_1)
    cliente.post("/api/lecturas", json=LIBRO_2)
    cliente.post("/api/clases-lectura", json={"tema": "Clase 5: sistemas", "inicio": INICIO,
                                              "cierre_respuesta": PLAZO, "ids_lecturas": [1, 2]})
    return cliente, reloj, tmp_path / "pdf"


def _detalle(cliente, estudiante=ANA):
    return cliente.get(f"/api/clases-lectura/1?estudiante={estudiante}").get_json()


def _responder(cliente, titulo="Qué es un sistema", respuesta="Un conjunto de partes", estudiante=ANA):
    return cliente.post("/api/clases-lectura/1/respuesta",
                        json={"estudiante": estudiante, "titulo": titulo, "respuesta": respuesta})


# ---------- Criterio 1: bibliografía visible antes de la clase ----------
def test_c1_veo_la_bibliografia_del_docente_con_titulo_y_archivo_o_enlace_antes_de_la_clase(entorno):
    cliente, reloj, _ = entorno
    reloj["ahora"] = ANTES_DE_CLASE
    clase = cliente.get(f"/api/clases-lectura?estudiante={ANA}").get_json()[0]
    assert clase["ventana"] == "Antes de la clase"
    assert [(t["titulo"], t["enlace"], t["archivo"]) for t in clase["bibliografia"]] == [
        ("Sistemas y complejidad", "https://ejemplo.org/lectura", None),
        ("Teoría general de sistemas", None, "/lecturas/tgs.pdf")]
    assert _detalle(cliente)["bibliografia"] == clase["bibliografia"]
    assert cliente.post("/api/lecturas", json={"titulo": "Sin recurso"}).status_code == 400      # exige archivo o enlace
    sin_biblio = cliente.post("/api/clases-lectura", json={"tema": "X", "inicio": INICIO, "cierre_respuesta": PLAZO,
                                                           "ids_lecturas": []})
    assert sin_biblio.get_json() == {"error": "La clase debe tener al menos un texto de bibliografía"}


# ---------- Criterio 2: apuntes por clase y por texto (crear, editar, ver) ----------
def test_c2_cada_apunte_se_asocia_a_una_clase_y_a_un_texto_y_se_puede_crear_editar_y_ver(entorno):
    cliente, _, _ = entorno
    creado = cliente.post("/api/clases-lectura/1/apuntes",
                          json={"estudiante": ANA, "id_lectura": 2, "texto": "Sistema = partes + relaciones"})
    assert creado.status_code == 201
    id_apunte = creado.get_json()["id"]
    visto = _detalle(cliente)["apuntes"]
    assert [(a["id_lectura"], a["titulo_lectura"], a["texto"]) for a in visto] == [
        (2, "Teoría general de sistemas", "Sistema = partes + relaciones")]
    editado = cliente.put(f"/api/clases-lectura/1/apuntes/{id_apunte}",
                          json={"estudiante": ANA, "texto": "Sistema = partes + relaciones + límite"})
    assert editado.status_code == 200
    assert _detalle(cliente)["apuntes"][0]["texto"] == "Sistema = partes + relaciones + límite"
    assert _detalle(cliente, "Luis Rojas")["apuntes"] == []                      # el cuaderno es de cada estudiante
    sin_texto = cliente.post("/api/clases-lectura/1/apuntes", json={"estudiante": ANA, "id_lectura": 1, "texto": " "})
    assert sin_texto.get_json() == {"error": "El apunte no puede estar vacío"}
    sin_lectura = cliente.post("/api/clases-lectura/1/apuntes", json={"estudiante": ANA, "texto": "x"})
    assert sin_lectura.status_code == 400
    otra = cliente.post("/api/lecturas", json={"titulo": "Ajeno", "enlace": "https://x.org"}).get_json()["id"]
    ajena = cliente.post("/api/clases-lectura/1/apuntes", json={"estudiante": ANA, "id_lectura": otra, "texto": "x"})
    assert ajena.get_json() == {"error": "Ese texto no pertenece a la bibliografía de la clase"}
    assert cliente.put("/api/clases-lectura/1/apuntes/99", json={"estudiante": ANA, "texto": "x"}).status_code == 400


# ---------- Criterio 3: dudas para plantear después de la explicación ----------
def test_c3_puedo_anotar_y_editar_dudas_para_plantearlas_despues_de_la_explicacion(entorno):
    cliente, _, _ = entorno
    creada = cliente.post("/api/clases-lectura/1/dudas", json={"estudiante": ANA, "texto": "¿Qué es entropía?"})
    assert creada.status_code == 201
    cliente.put(f"/api/clases-lectura/1/dudas/{creada.get_json()['id']}",
                json={"estudiante": ANA, "texto": "¿Qué es entropía en sistemas abiertos?"})
    assert [d["texto"] for d in _detalle(cliente)["dudas"]] == ["¿Qué es entropía en sistemas abiertos?"]
    assert cliente.post("/api/clases-lectura/1/dudas", json={"estudiante": ANA, "texto": ""}).get_json() == {
        "error": "La duda no puede estar vacía"}


# ---------- Criterio 4: la pregunta la plantea el docente en clase; el sistema solo recibe la respuesta ----------
def test_c4_el_sistema_no_genera_ni_guarda_la_pregunta_solo_recibe_la_respuesta(entorno):
    cliente, _, _ = entorno
    detalle = _detalle(cliente)
    assert not any("pregunta" in clave for clave in detalle)                     # la clase no trae preguntas
    clase = cliente.post("/api/clases-lectura", json={"tema": "Otra", "inicio": INICIO, "cierre_respuesta": PLAZO,
                                                      "ids_lecturas": [1], "preguntas": ["¿Algo?"]}).get_json()
    assert "preguntas" not in clase                                              # aunque se la manden, no existe el concepto
    assert _responder(cliente).status_code == 200


# ---------- Criterio 5: título + respuesta obligatorios ----------
def test_c5_escribo_titulo_y_respuesta_y_no_puedo_enviar_con_campos_obligatorios_vacios(entorno):
    cliente, _, _ = entorno
    sin_titulo = _responder(cliente, titulo="  ")
    assert sin_titulo.status_code == 400
    assert sin_titulo.get_json() == {"error": "Completa los campos obligatorios: título"}
    sin_respuesta = _responder(cliente, respuesta="")
    assert sin_respuesta.get_json() == {"error": "Completa los campos obligatorios: respuesta"}
    ninguno = _responder(cliente, titulo="", respuesta="")
    assert ninguno.get_json() == {"error": "Completa los campos obligatorios: título y respuesta"}
    assert _detalle(cliente)["estado"] == "Pendiente"
    assert _responder(cliente).status_code == 200
    assert _responder(cliente, estudiante=" ").status_code == 400                # sin nombre tampoco


# ---------- Criterio 6: PDF con fecha y hora exactas, "A tiempo" o "Tarde" ----------
def test_c6_la_respuesta_se_entrega_en_pdf_con_fecha_hora_exactas_clasificada_a_tiempo_o_tarde(entorno):
    cliente, reloj, carpeta = entorno
    reloj["ahora"] = datetime(2026, 3, 3, 10, 15, 42)
    envio = _responder(cliente).get_json()
    assert envio["puntualidad"] == "A tiempo" and envio["fecha_hora_envio"] == "2026-03-03T10:15:42"
    pdf = cliente.get(f"/api/clases-lectura/1/respuesta/pdf?estudiante={ANA}")
    assert pdf.status_code == 200 and pdf.mimetype == "application/pdf" and pdf.data.startswith(b"%PDF")
    assert b"03/03/2026 10:15:42" in pdf.data and b"A tiempo" in pdf.data
    assert [p.name for p in carpeta.iterdir()] == ["clase1_ana-perez_intento1.pdf"]
    # Tarde: segundo estudiante responde pasado el plazo
    reloj["ahora"] = DESPUES_DEL_PLAZO
    assert _responder(cliente, estudiante="Eva Díaz").get_json()["puntualidad"] == "Tarde"
    pdf_tarde = cliente.get("/api/clases-lectura/1/respuesta/pdf?estudiante=Eva Díaz")
    assert b"05/03/2026 09:00:00" in pdf_tarde.data and b"Tarde" in pdf_tarde.data
    filas = {f["estudiante"]: f["estado_revision"]
             for f in cliente.get("/api/clases-lectura/1/respuestas").get_json()["estudiantes"]}
    assert filas == {ANA: "Respondido", "Eva Díaz": "Tarde"}
    assert cliente.get("/api/clases-lectura/1/respuesta/pdf?estudiante=Nadie").status_code == 404


def test_c6_no_se_puede_responder_antes_de_que_el_docente_plantee_la_pregunta_en_clase(entorno):
    cliente, reloj, _ = entorno
    reloj["ahora"] = ANTES_DE_CLASE
    assert _detalle(cliente)["puede_responder"] is False
    assert _responder(cliente).get_json() == {"error": "La pregunta se plantea en clase: aún no puedes responder"}


# ---------- Criterio 7: error => no se registra; éxito => "Respondido" ----------
def test_c7_si_falla_no_se_registra_y_se_muestra_error(tmp_path):
    class RepositorioQueFalla(RepositorioMemoria):
        def guardar(self, clave, dato):
            raise OSError("disco lleno")

    almacen = AlmacenPdf(tmp_path / "pdf")
    servicio = ServicioApuntesLectura(RepositorioMemoria(), RepositorioMemoria(), RepositorioMemoria(),
                                      RepositorioMemoria(), RepositorioMemoria(), almacen)
    servicio.registrarLectura(LIBRO_1)
    servicio.publicarClase({"tema": "C", "inicio": INICIO, "cierre_respuesta": PLAZO, "ids_lecturas": [1]})
    servicio._repo_respuestas = RepositorioQueFalla()
    with pytest.raises(ErrorGuardado) as error:
        servicio.enviarRespuesta(1, ANA, "Título", "Respuesta", EN_CLASE)
    assert "No se pudo guardar tu respuesta" in str(error.value)
    servicio._repo_respuestas = RepositorioMemoria()
    assert servicio.obtenerClase(1, ANA, EN_CLASE)["estado"] == "Pendiente"
    assert not (tmp_path / "pdf").exists() or list((tmp_path / "pdf").iterdir()) == []   # sin PDF huérfano


def test_c7_si_falla_la_generacion_del_pdf_tampoco_se_registra(tmp_path):
    class GeneradorRoto:
        def generar(self, respuesta, clase):
            raise RuntimeError("sin pdf")

    servicio = ServicioApuntesLectura(RepositorioMemoria(), RepositorioMemoria(), RepositorioMemoria(),
                                      RepositorioMemoria(), RepositorioMemoria(), AlmacenPdf(tmp_path), GeneradorRoto())
    servicio.registrarLectura(LIBRO_1)
    servicio.publicarClase({"tema": "C", "inicio": INICIO, "cierre_respuesta": PLAZO, "ids_lecturas": [1]})
    with pytest.raises(ErrorGuardado):
        servicio.enviarRespuesta(1, ANA, "Título", "Respuesta", EN_CLASE)
    assert servicio.obtenerClase(1, ANA, EN_CLASE)["estado"] == "Pendiente"


def test_c7_la_api_responde_con_error_de_guardado(entorno, monkeypatch):
    cliente, _, _ = entorno
    monkeypatch.setattr(ServicioApuntesLectura, "_guardarRespuesta",
                        lambda self, respuesta: (_ for _ in ()).throw(OSError("fallo")))
    respuesta = _responder(cliente)
    assert respuesta.status_code == 500 and "No se pudo guardar" in respuesta.get_json()["error"]
    assert _detalle(cliente)["estado"] == "Pendiente"


def test_c7_si_sale_bien_hay_confirmacion_y_el_estado_pasa_a_respondido(entorno):
    cliente, reloj, _ = entorno
    reloj["ahora"] = datetime(2026, 3, 3, 10, 15, 42)
    respuesta = _responder(cliente).get_json()
    assert respuesta["mensaje"] == "Respuesta enviada el 03/03/2026 a las 10:15:42"
    assert respuesta["estado"] == "Respondido"
    detalle = _detalle(cliente)
    assert detalle["estado"] == "Respondido" and detalle["tiene_pdf"] is True
    assert (detalle["titulo_respuesta"], detalle["texto_respuesta"]) == ("Qué es un sistema", "Un conjunto de partes")


# ---------- Criterio 8: un solo intento, salvo que el docente habilite otro que reemplaza al anterior ----------
def test_c8_un_solo_intento_salvo_que_el_docente_habilite_otro_que_reemplaza_al_anterior(entorno):
    cliente, reloj, carpeta = entorno
    assert _responder(cliente, respuesta="primera").status_code == 200
    repetido = _responder(cliente, respuesta="segunda")
    assert repetido.status_code == 400 and "Ya enviaste tu respuesta" in repetido.get_json()["error"]
    assert _detalle(cliente)["puede_responder"] is False
    cliente.post("/api/clases-lectura/1/calificacion", json={"estudiante": ANA, "nota": 7, "publicar": True})
    assert cliente.post("/api/clases-lectura/1/nuevo-intento", json={"estudiante": ANA}).status_code == 200
    assert _detalle(cliente)["puede_responder"] is True
    reloj["ahora"] = DESPUES_DEL_PLAZO
    assert _responder(cliente, respuesta="segunda").status_code == 200
    fila = cliente.get("/api/clases-lectura/1/respuestas").get_json()["estudiantes"][0]
    assert fila["respuesta"] == "segunda" and fila["intentos"] == 2 and fila["puntualidad"] == "Tarde"
    assert fila["nota"] is None                                           # el nuevo intento reemplaza al anterior por completo
    assert [p.name for p in carpeta.iterdir()] == ["clase1_ana-perez_intento2.pdf"]   # y su PDF reemplaza al anterior
    assert _responder(cliente).status_code == 400                         # vuelve a quedar un solo intento


# ---------- Criterio 9: calificación y retroalimentación cuando se publiquen ----------
def test_c9_veo_mi_calificacion_y_retroalimentacion_solo_cuando_el_docente_las_publica(entorno):
    cliente, _, _ = entorno
    _responder(cliente)
    cliente.post("/api/clases-lectura/1/calificacion",
                 json={"estudiante": ANA, "nota": 9, "retroalimentacion": "Muy bien", "publicar": False})
    oculto = _detalle(cliente)
    assert oculto["nota"] is None and oculto["retroalimentacion"] is None
    cliente.post("/api/clases-lectura/1/calificacion",
                 json={"estudiante": ANA, "nota": 9, "retroalimentacion": "Muy bien", "publicar": True})
    visible = _detalle(cliente)
    assert visible["nota"] == "9" and visible["retroalimentacion"] == "Muy bien"
    assert cliente.post("/api/clases-lectura/1/calificacion", json={"estudiante": ANA, "nota": 101}).status_code == 400
    pendiente = cliente.post("/api/clases-lectura/1/calificacion", json={"estudiante": "Luis Rojas", "nota": 5})
    assert pendiente.get_json() == {"error": "Solo se puede calificar una respuesta que ya fue enviada"}