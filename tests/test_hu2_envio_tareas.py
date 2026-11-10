"""HU2 - Envío de tareas al correo del docente: un test por criterio de aceptación (servicio + repositorio en memoria)."""
from datetime import datetime

import pytest

from src.repositorio.repositorio_memoria import RepositorioMemoria
from src.servicio.servicio_envio_tareas import ErrorEnvioCorreo, ServicioEnvioTareas

MATERIA = "Sistemas 2"
DOCENTE = "docente.si2@umss.edu.bo"
TAREA = "Tarea 1: diagrama de clases"
ANA = "Ana Pérez"
CORREO_ANA = "ana.perez@est.umss.edu.bo"
ADJUNTOS = [{"nombre": "diagrama.pdf", "contenido": "ZGF0b3M="}]
A_TIEMPO = datetime(2026, 3, 10, 9, 0, 0)
TARDE = datetime(2026, 3, 12, 9, 0, 0)
LIMITE = datetime(2026, 3, 11, 23, 59, 0)


class EnviadorEspia:
    def __init__(self):
        self.enviados = []

    def enviar(self, destino, asunto, cuerpo, adjuntos):
        self.enviados.append({"destino": destino, "asunto": asunto, "cuerpo": cuerpo, "adjuntos": adjuntos})


class EnviadorRoto:
    def enviar(self, *args):
        raise RuntimeError("smtp caído")


def _servicio(enviador=None):
    servicio = ServicioEnvioTareas(RepositorioMemoria(), RepositorioMemoria(), enviador or EnviadorEspia())
    servicio.asignarDocente(MATERIA, DOCENTE)
    return servicio


# ---------- Criterio 1: el sistema muestra el correo del docente de la materia ----------
def test_c1_muestra_el_correo_del_docente_asignado_a_la_materia():
    servicio = _servicio()
    assert servicio.correoDocente(MATERIA) == DOCENTE


def test_c1_materia_sin_docente_avisa_en_lugar_de_enviar():
    servicio = ServicioEnvioTareas(RepositorioMemoria(), RepositorioMemoria(), EnviadorEspia())
    with pytest.raises(ValueError):
        servicio.correoDocente("Materia inexistente")


# ---------- Criterio 2: debe adjuntar al menos un archivo ----------
def test_c2_sin_adjuntos_no_envia_y_avisa():
    espia = EnviadorEspia()
    servicio = _servicio(espia)
    with pytest.raises(ValueError):
        servicio.enviar(MATERIA, TAREA, ANA, CORREO_ANA, [], LIMITE, A_TIEMPO)
    assert espia.enviados == []


# ---------- Criterio 3: envía el correo al docente con los adjuntos ----------
def test_c3_envia_el_correo_al_docente_con_los_adjuntos():
    espia = EnviadorEspia()
    servicio = _servicio(espia)
    servicio.enviar(MATERIA, TAREA, ANA, CORREO_ANA, ADJUNTOS, LIMITE, A_TIEMPO)
    assert len(espia.enviados) == 1
    correo = espia.enviados[0]
    assert correo["destino"] == DOCENTE
    assert [a["nombre"] for a in correo["adjuntos"]] == ["diagrama.pdf"]


# ---------- Criterio 4: el cuerpo incluye los datos del estudiante y la entrega ----------
def test_c4_el_cuerpo_incluye_estudiante_correo_materia_tarea_y_fecha():
    espia = EnviadorEspia()
    servicio = _servicio(espia)
    servicio.enviar(MATERIA, TAREA, ANA, CORREO_ANA, ADJUNTOS, LIMITE, A_TIEMPO)
    cuerpo = espia.enviados[0]["cuerpo"]
    assert ANA in cuerpo and CORREO_ANA in cuerpo and MATERIA in cuerpo and TAREA in cuerpo
    assert "10/03/2026 09:00:00" in cuerpo


# ---------- Criterio 5: registra la fecha y hora exactas del envío ----------
def test_c5_registra_la_fecha_y_hora_exactas_del_envio():
    servicio = _servicio()
    resultado = servicio.enviar(MATERIA, TAREA, ANA, CORREO_ANA, ADJUNTOS, LIMITE, A_TIEMPO)
    assert resultado["fecha_hora_envio"] == A_TIEMPO.isoformat()


# ---------- Criterio 6: clasifica la entrega como a tiempo o tarde ----------
def test_c6_clasifica_entrega_a_tiempo_cuando_envia_antes_del_limite():
    servicio = _servicio()
    resultado = servicio.enviar(MATERIA, TAREA, ANA, CORREO_ANA, ADJUNTOS, LIMITE, A_TIEMPO)
    assert resultado["puntualidad"] == "Entregada a tiempo"


def test_c6_clasifica_entrega_tarde_cuando_envia_despues_del_limite():
    servicio = _servicio()
    resultado = servicio.enviar(MATERIA, TAREA, ANA, CORREO_ANA, ADJUNTOS, LIMITE, TARDE)
    assert resultado["puntualidad"] == "Entregada tarde"


# ---------- Criterio 7: si el correo falla, la tarea no se registra como entregada ----------
def test_c7_si_el_correo_falla_no_se_registra_la_entrega():
    servicio = _servicio(EnviadorRoto())
    with pytest.raises(ErrorEnvioCorreo):
        servicio.enviar(MATERIA, TAREA, ANA, CORREO_ANA, ADJUNTOS, LIMITE, A_TIEMPO)
    with pytest.raises(ValueError):
        servicio.estadoEnvio(MATERIA, TAREA, ANA)


# ---------- Criterio 8: si el correo se envía, estado pasa a Entregada y hay confirmación ----------
def test_c8_envio_correcto_deja_estado_entregada_y_confirmacion():
    servicio = _servicio()
    resultado = servicio.enviar(MATERIA, TAREA, ANA, CORREO_ANA, ADJUNTOS, LIMITE, A_TIEMPO)
    assert resultado["estado"] == "Entregada"
    assert DOCENTE in resultado["mensaje"]
    assert servicio.estadoEnvio(MATERIA, TAREA, ANA)["estado"] == "Entregada"


# ---------- Criterio 9: reentrega habilitada reemplaza la entrega anterior ----------
def test_c9_sin_reentrega_no_permite_reenviar():
    servicio = _servicio()
    servicio.enviar(MATERIA, TAREA, ANA, CORREO_ANA, ADJUNTOS, LIMITE, A_TIEMPO)
    with pytest.raises(ValueError):
        servicio.enviar(MATERIA, TAREA, ANA, CORREO_ANA, ADJUNTOS, LIMITE, A_TIEMPO)


def test_c9_reentrega_habilitada_reemplaza_la_entrega_anterior():
    espia = EnviadorEspia()
    servicio = _servicio(espia)
    servicio.enviar(MATERIA, TAREA, ANA, CORREO_ANA, ADJUNTOS, LIMITE, A_TIEMPO)
    servicio.habilitarReentrega(MATERIA, TAREA, ANA)
    nuevos_adjuntos = [{"nombre": "diagrama_v2.pdf", "contenido": "bnVldm8="}]
    resultado = servicio.enviar(MATERIA, TAREA, ANA, CORREO_ANA, nuevos_adjuntos, LIMITE, TARDE)
    guardado = servicio.estadoEnvio(MATERIA, TAREA, ANA)
    assert [a["nombre"] for a in guardado["adjuntos"]] == ["diagrama_v2.pdf"]   # reemplaza, no acumula
    assert resultado["puntualidad"] == "Entregada tarde"
    assert len(espia.enviados) == 2


# ---------- Criterio 10: el docente identifica al estudiante por el asunto ----------
def test_c10_el_asunto_identifica_estudiante_materia_y_tarea():
    espia = EnviadorEspia()
    servicio = _servicio(espia)
    servicio.enviar(MATERIA, TAREA, ANA, CORREO_ANA, ADJUNTOS, LIMITE, A_TIEMPO)
    asunto = espia.enviados[0]["asunto"]
    assert ANA in asunto and MATERIA in asunto and TAREA in asunto
