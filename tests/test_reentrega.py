from datetime import datetime

import pytest

from src.constantes import (
    ESTADOS,
    MSG_REENTREGA_FUERA_DE_PLAZO,
    MSG_REENTREGA_NO_HABILITADA,
    MSG_REENTREGA_REGISTRADA,
    MSG_REENTREGA_SIN_ARCHIVO,
    MSG_REENTREGA_SIN_ERRORES,
    MSG_REENTREGA_SIN_PRESENCIA,
    MSG_SOLO_PDF,
)
from src.modelo.entrega import Entrega
from src.modelo.reentrega import Reentrega
from src.modelo.revision_tareas import RevisionTareas
from src.modelo.rubrica import Rubrica
from src.modelo.tarea_individual import TareaIndividual

LIMITE = datetime(2026, 3, 4, 6, 45)
ANTES = datetime(2026, 3, 3, 20, 0)
CLASE = datetime(2026, 3, 4, 7, 30)
REENTREGA = datetime(2026, 3, 4, 8, 0)


def entrega_revisada(con_errores=True):
    rubrica = Rubrica()
    rubrica.agregarCriterio("c", 100)
    tarea = TareaIndividual(1, "T1", "x", LIMITE, ruta_adjunto="g.pdf", rubrica=rubrica)
    entrega = Entrega(tarea, rubrica, ["a.pdf"])
    entrega.confirmar(ANTES)
    revision = RevisionTareas(1, LIMITE)
    revision.evaluarRevision(ANTES, ESTADOS.PRESENTE)
    revision.registrarResultado(con_errores, "Falta el punto 2" if con_errores else "", CLASE)
    revision.evaluarRevision(ANTES, ESTADOS.PRESENTE)
    return entrega, revision


def test_habilita_cuando_hay_errores_y_el_estudiante_esta_presente():
    _, revision = entrega_revisada()
    Reentrega().habilitarReentrega(revision, ESTADOS.PRESENTE)


def test_el_atraso_cuenta_como_presencia():
    Reentrega().validarPresencia(ESTADOS.ATRASO)


@pytest.mark.parametrize("estado", [ESTADOS.AUSENTE, ESTADOS.LICENCIA, None])
def test_sin_presencia_no_hay_reentrega(estado):
    with pytest.raises(ValueError, match=MSG_REENTREGA_SIN_PRESENCIA):
        Reentrega().validarPresencia(estado)


def test_una_tarea_revisada_sin_errores_no_se_reentrega():
    _, revision = entrega_revisada(con_errores=False)
    with pytest.raises(ValueError, match=MSG_REENTREGA_SIN_ERRORES):
        Reentrega().habilitarReentrega(revision, ESTADOS.PRESENTE)


def test_una_tarea_aun_no_revisada_no_se_reentrega():
    revision = RevisionTareas(1, LIMITE)
    revision.evaluarRevision(ANTES, ESTADOS.PRESENTE)
    with pytest.raises(ValueError, match=MSG_REENTREGA_NO_HABILITADA):
        Reentrega().habilitarReentrega(revision, ESTADOS.PRESENTE)


def test_acepta_pdf_en_mayusculas_o_minusculas():
    Reentrega().validarPDF(["corregida.pdf", "Anexo.PDF"], [])


@pytest.mark.parametrize("archivos, enlaces, mensaje", [
    ([], [], MSG_REENTREGA_SIN_ARCHIVO),
    (["tarea.docx"], [], MSG_SOLO_PDF),
    (["tarea.pdf.exe"], [], MSG_SOLO_PDF),
    ([".pdf"], [], MSG_SOLO_PDF),
    ([None], [], MSG_SOLO_PDF),
    (["tarea.pdf"], ["https://x.com"], MSG_SOLO_PDF),
])
def test_rechaza_lo_que_no_sea_pdf(archivos, enlaces, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        Reentrega().validarPDF(archivos, enlaces)


def test_reemplazar_deja_la_nueva_version_vigente_y_archiva_la_anterior():
    entrega, revision = entrega_revisada()
    Reentrega().reemplazarEntrega(entrega, revision, ["nueva.pdf"], REENTREGA)
    assert entrega.archivos == ["nueva.pdf"] and entrega.enlaces == []
    assert entrega.fecha_hora_entrega == REENTREGA
    anterior = revision.versiones[0]
    assert anterior["archivos"] == ["a.pdf"] and anterior["fecha_hora_entrega"] == ANTES.isoformat()
    assert anterior["con_errores"] is True and anterior["observaciones"] == "Falta el punto 2"


def test_reemplazar_descarta_el_resultado_anterior_de_la_revision():
    entrega, revision = entrega_revisada()
    Reentrega().reemplazarEntrega(entrega, revision, ["nueva.pdf"], REENTREGA)
    assert revision.con_errores is None and revision.observaciones is None and revision.fecha_revision is None


def test_la_fecha_de_plazo_sigue_siendo_la_de_la_primera_entrega():
    entrega, revision = entrega_revisada()
    Reentrega().reemplazarEntrega(entrega, revision, ["nueva.pdf"], REENTREGA)
    revision.evaluarRevision(entrega.fecha_hora_entrega, ESTADOS.PRESENTE)
    assert revision.a_tiempo is True and revision.estado.value == "Pendiente de revisión"


def test_notifica_que_quedo_pendiente_de_revision():
    assert Reentrega().notificarRevision() == MSG_REENTREGA_REGISTRADA


def test_habilita_dentro_del_plazo_y_rechaza_al_llegar_la_siguiente_clase():
    _, revision = entrega_revisada()
    Reentrega().habilitarReentrega(revision, ESTADOS.PRESENTE, datetime(2026, 3, 6, 6, 44))
    with pytest.raises(ValueError, match=MSG_REENTREGA_FUERA_DE_PLAZO):
        Reentrega().habilitarReentrega(revision, ESTADOS.PRESENTE, datetime(2026, 3, 6, 6, 45))


def test_tras_reentregar_se_puede_reenviar_mientras_espera_la_nueva_revision():
    entrega, revision = entrega_revisada()
    Reentrega().reemplazarEntrega(entrega, revision, ["nueva.pdf"], REENTREGA)
    revision.evaluarRevision(entrega.fecha_hora_entrega, ESTADOS.PRESENTE, REENTREGA)
    Reentrega().habilitarReentrega(revision, ESTADOS.PRESENTE, REENTREGA)
