from datetime import datetime

import pytest

from src.constantes import (
    ESTADOS,
    ESTADOS_REVISION,
    MSG_CON_ERRORES_INVALIDO,
    MSG_NO_SE_PUEDE_REVISAR,
    MSG_OBSERVACIONES_INVALIDAS,
    MSG_OBSERVACIONES_OBLIGATORIAS,
    MSG_REENTREGA_SIN_PRESENCIA,
)
from src.modelo.revision_tareas import RevisionTareas
from src.repositorio.repositorio_memoria import RepositorioMemoria

LIMITE = datetime(2026, 3, 4, 6, 45)
ANTES = datetime(2026, 3, 3, 20, 0)
JUSTO = datetime(2026, 3, 4, 6, 45)
DESPUES = datetime(2026, 3, 4, 6, 46)
CLASE = datetime(2026, 3, 4, 7, 30)


def revision():
    return RevisionTareas(1, LIMITE)


def test_entrega_antes_del_limite_es_a_tiempo():
    assert revision().validarEntrega(ANTES) is True


def test_entrega_exactamente_en_el_limite_es_tarde():
    assert revision().validarEntrega(JUSTO) is False


def test_entrega_posterior_al_limite_es_tarde():
    assert revision().validarEntrega(DESPUES) is False


def test_sin_entrega_no_se_clasifica():
    assert revision().validarEntrega(None) is None


@pytest.mark.parametrize("estado, etiqueta", [
    (ESTADOS.PRESENTE, "Puntual"), (ESTADOS.ATRASO, "Tardío"), (ESTADOS.AUSENTE, "Ausente"),
    (ESTADOS.LICENCIA, "Licencia"), (None, "Sin registrar"),
])
def test_puntualidad_segun_la_asistencia_de_la_hu1(estado, etiqueta):
    assert revision().validarPuntualidad(estado) == etiqueta


@pytest.mark.parametrize("a_tiempo, puntual, presente, esperado", [
    (None, False, False, ESTADOS_REVISION.PENDIENTE),
    (None, True, True, ESTADOS_REVISION.PENDIENTE),
    (True, True, True, ESTADOS_REVISION.PENDIENTE_DE_REVISION),
    (True, False, True, ESTADOS_REVISION.NO_REVISADA),
    (False, True, True, ESTADOS_REVISION.NO_REVISADA),
    (False, False, True, ESTADOS_REVISION.NO_REVISADA),
    (True, True, False, ESTADOS_REVISION.PENDIENTE_DE_REVISION),
])
def test_tabla_de_decision_de_la_hu4(a_tiempo, puntual, presente, esperado):
    estado, habilitada = RevisionTareas.resolverEstado(a_tiempo, puntual, presente)
    assert estado == esperado and habilitada is False


def test_revisada_sin_errores():
    assert RevisionTareas.resolverEstado(True, True, True, True, False) == (ESTADOS_REVISION.REVISADA, False)


def test_revisada_con_errores_y_presente_habilita_la_reentrega():
    assert RevisionTareas.resolverEstado(True, True, True, True, True) == (ESTADOS_REVISION.REENTREGA, True)


def test_revisada_con_errores_y_ausente_no_habilita_la_reentrega():
    assert RevisionTareas.resolverEstado(True, True, False, True, True) == (ESTADOS_REVISION.REVISADA, False)


def test_la_presencia_no_vuelve_puntual_a_una_entrega_tardia():
    assert RevisionTareas.resolverEstado(False, True, True, True, True)[0] == ESTADOS_REVISION.NO_REVISADA


@pytest.mark.parametrize("entrega, asistencia, mensaje", [
    (DESPUES, ESTADOS.PRESENTE, "No revisada: entrega tardía"),
    (ANTES, ESTADOS.ATRASO, "No revisada: llegada tardía"),
    (DESPUES, ESTADOS.ATRASO, "No revisada: entrega tardía y llegada tardía"),
    (ANTES, ESTADOS.AUSENTE, "No revisada: inasistencia a clase"),
])
def test_no_revisada_explica_el_motivo(entrega, asistencia, mensaje):
    r = revision()
    r.evaluarRevision(entrega, asistencia)
    assert r.estado == ESTADOS_REVISION.NO_REVISADA and r.obtenerMotivo() == mensaje


def test_entregada_a_tiempo_y_puntual_queda_pendiente_de_revision():
    r = revision()
    r.evaluarRevision(ANTES, ESTADOS.PRESENTE)
    assert r.estado == ESTADOS_REVISION.PENDIENTE_DE_REVISION and r.obtenerMotivo() is None


def test_sin_entrega_queda_pendiente_sin_motivo_ni_revision():
    r = revision()
    r.evaluarRevision(None, ESTADOS.ATRASO)
    assert r.estado == ESTADOS_REVISION.PENDIENTE and r.obtenerMotivo() is None and not r.puedeRevisarse()


def test_entrega_a_tiempo_con_asistencia_sin_registrar_espera_la_clase():
    r = revision()
    r.evaluarRevision(ANTES, None)
    assert r.estado == ESTADOS_REVISION.PENDIENTE_DE_REVISION and r.puntualidad == "Sin registrar"
    assert not r.puedeRevisarse()


def test_registrar_resultado_sin_errores_deja_la_tarea_revisada():
    r = revision()
    r.evaluarRevision(ANTES, ESTADOS.PRESENTE)
    r.registrarResultado(False, "", CLASE)
    r.evaluarRevision(ANTES, ESTADOS.PRESENTE)
    assert r.estado == ESTADOS_REVISION.REVISADA and not r.reentrega_habilitada


def test_registrar_resultado_con_errores_habilita_la_reentrega():
    r = revision()
    r.evaluarRevision(ANTES, ESTADOS.PRESENTE)
    r.registrarResultado(True, "Falta el punto 2", CLASE)
    r.evaluarRevision(ANTES, ESTADOS.PRESENTE)
    assert r.estado == ESTADOS_REVISION.REENTREGA and r.reentrega_habilitada


def test_no_se_puede_revisar_una_tarea_no_revisable():
    r = revision()
    r.evaluarRevision(DESPUES, ESTADOS.PRESENTE)
    with pytest.raises(ValueError, match=MSG_NO_SE_PUEDE_REVISAR):
        r.registrarResultado(False, "", CLASE)


def test_con_errores_exige_observaciones():
    r = revision()
    r.evaluarRevision(ANTES, ESTADOS.PRESENTE)
    with pytest.raises(ValueError, match=MSG_OBSERVACIONES_OBLIGATORIAS):
        r.registrarResultado(True, "   ", CLASE)


@pytest.mark.parametrize("con_errores", ["si", 1, None])
def test_con_errores_debe_ser_booleano(con_errores):
    r = revision()
    r.evaluarRevision(ANTES, ESTADOS.PRESENTE)
    with pytest.raises(ValueError, match=MSG_CON_ERRORES_INVALIDO):
        r.registrarResultado(con_errores, "x", CLASE)


def test_observaciones_invalidas():
    r = revision()
    r.evaluarRevision(ANTES, ESTADOS.PRESENTE)
    with pytest.raises(ValueError, match=MSG_OBSERVACIONES_INVALIDAS):
        r.registrarResultado(True, "x" * 1001, CLASE)


def test_el_resultado_deja_de_valer_si_la_tarea_deja_de_ser_revisable():
    r = revision()
    r.evaluarRevision(ANTES, ESTADOS.PRESENTE)
    r.registrarResultado(True, "Falta", CLASE)
    r.recalcular(ANTES, ESTADOS.ATRASO)
    assert r.estado == ESTADOS_REVISION.NO_REVISADA and not r.reentrega_habilitada


def test_con_errores_y_asistencia_cambiada_a_ausente_explica_por_que_no_hay_reentrega():
    r = revision()
    r.con_errores, r.observaciones = True, "Falta"
    assert r.estado == ESTADOS_REVISION.PENDIENTE
    estado, habilitada = r.resolverEstado(True, True, False, True, True)
    assert (estado, habilitada) == (ESTADOS_REVISION.REVISADA, False)
    assert r._mensajeReentrega(estado, False) == MSG_REENTREGA_SIN_PRESENCIA


def test_se_guarda_y_se_recupera_con_su_historial():
    r = revision()
    r.evaluarRevision(ANTES, ESTADOS.PRESENTE)
    r.registrarResultado(True, "Falta", CLASE)
    r.versiones.append({"version": 1, "fecha_hora_entrega": ANTES.isoformat()})
    repo = RepositorioMemoria()
    r.guardar(repo)
    otra = RevisionTareas.desdeDiccionario(repo.obtener(1), 1, LIMITE)
    assert (otra.con_errores, otra.observaciones, otra.fecha_revision, otra.versiones) == (
        True, "Falta", CLASE, r.versiones)


@pytest.mark.parametrize("dia_revision, siguiente_clase", [
    (datetime(2026, 3, 3, 7, 30), datetime(2026, 3, 4, 6, 45)),    # martes -> miércoles
    (datetime(2026, 3, 4, 7, 30), datetime(2026, 3, 6, 6, 45)),    # miércoles -> viernes
    (datetime(2026, 3, 6, 7, 30), datetime(2026, 3, 10, 6, 45)),   # viernes -> martes
])
def test_el_plazo_de_reentrega_cierra_en_la_siguiente_clase(dia_revision, siguiente_clase):
    r = revision()
    r.fecha_revision = dia_revision
    assert r.fechaLimiteReentrega() == siguiente_clase


def test_sin_revision_no_hay_plazo_ni_esta_vencido():
    r = revision()
    assert r.fechaLimiteReentrega() is None and r.reentregaVencida(datetime(2030, 1, 1)) is False


def test_el_plazo_usa_la_ultima_revision_del_historial_si_la_vigente_fue_descartada():
    r = revision()
    r.versiones = [{"fecha_hora_entrega": ANTES.isoformat(), "fecha_revision": CLASE.isoformat()}]
    assert r.fechaLimiteReentrega() == datetime(2026, 3, 6, 6, 45)


def test_vence_exactamente_al_cierre_de_la_siguiente_clase():
    r = revision()
    r.fecha_revision = CLASE
    assert r.reentregaVencida(datetime(2026, 3, 6, 6, 44)) is False
    assert r.reentregaVencida(datetime(2026, 3, 6, 6, 45)) is True
