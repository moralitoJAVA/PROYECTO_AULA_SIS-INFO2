import sqlite3
from datetime import date, datetime

import pytest

from src.constantes import (
    MSG_NO_SE_PUEDE_REVISAR,
    MSG_REENTREGA_FUERA_DE_PLAZO,
    MSG_REENTREGA_NO_HABILITADA,
    MSG_REENTREGA_SIN_PRESENCIA,
    MSG_SOLO_PDF,
    MSG_TAREA_NO_EXISTE,
)
from src.modelo.rubrica import Rubrica
from src.modelo.tarea_individual import TareaIndividual
from src.repositorio.repositorio_memoria import RepositorioMemoria
from src.repositorio.repositorio_sqlite import RepositorioSqlite
from src.servicio.servicio_asistencia import ServicioAsistencia
from src.servicio.servicio_revision_tareas import ServicioRevisionTareas
from src.servicio.servicio_tareas import ServicioTareas

MATERIA = "Sistemas de Información 2"
REGISTRO = datetime(2026, 3, 1, 10, 0)
LIMITE = datetime(2026, 3, 4, 6, 45)
ANTES = datetime(2026, 3, 3, 20, 0)
CLASE = datetime(2026, 3, 4, 7, 30)
REENTREGA = datetime(2026, 3, 4, 8, 0)
DIA_CLASE = date(2026, 3, 4)


class Entorno:
    def __init__(self, repos=None):
        r = repos or {n: RepositorioMemoria() for n in ("tareas", "entregas", "equipos", "penalizaciones", "revisiones", "asistencias")}
        self.repos = r
        self.tareas = ServicioTareas(r["tareas"], r["entregas"], r["equipos"], r["penalizaciones"])
        self.asistencia = ServicioAsistencia(r["asistencias"])
        self.revision = ServicioRevisionTareas(r["tareas"], r["entregas"], r["revisiones"], self.asistencia)

    def registrarTarea(self, numero=1, limite=LIMITE):
        rubrica = Rubrica()
        rubrica.agregarCriterio("c", 100)
        tarea = TareaIndividual(numero, f"Tarea {numero}", "x", limite, ruta_adjunto="g.pdf", rubrica=rubrica)
        tarea.registrar(REGISTRO)
        tarea.guardar(self.repos["tareas"])

    def entregar(self, numero=1, ahora=ANTES):
        self.tareas.entregar(numero, ["a.pdf"], [], ahora)

    def asistir(self, estado, dia=DIA_CLASE):
        if self.asistencia.abrirSesion(MATERIA, dia).asistencia.existePara(dia):
            self.asistencia.editarAsistencia(MATERIA, dia, estado)
        else:
            self.asistencia.registrarAsistencia(MATERIA, dia, estado)

    def estado(self, numero=1):
        return self.revision.obtenerEstado(numero)


@pytest.fixture
def e():
    entorno = Entorno()
    entorno.registrarTarea()
    return entorno


def test_tarea_inexistente_falla(e):
    with pytest.raises(ValueError, match=MSG_TAREA_NO_EXISTE):
        e.revision.obtenerEstado(99)


def test_sin_entrega_la_tarea_esta_pendiente_y_no_se_crea_una_entrega_ficticia(e):
    e.asistir("Atraso")
    estado = e.estado()
    assert estado["estado"] == "Pendiente" and estado["motivo"] is None and estado["a_tiempo"] is None
    assert e.repos["entregas"].obtener(1) is None and e.repos["revisiones"].obtener(1) is None


def test_entrega_a_tiempo_y_llegada_puntual_queda_pendiente_de_revision(e):
    e.entregar()
    e.asistir("Presente")
    estado = e.estado()
    assert (estado["estado"], estado["a_tiempo"], estado["puntualidad"]) == ("Pendiente de revisión", True, "Puntual")
    assert estado["puede_revisarse"] is True


def test_entrega_exactamente_a_las_0645_se_considera_tarde(e):
    e.entregar(ahora=LIMITE)
    e.asistir("Presente")
    estado = e.estado()
    assert estado["estado"] == "No revisada" and estado["motivo"] == "No revisada: entrega tardía"


def test_llegada_despues_de_las_0700_no_se_revisa(e):
    e.entregar()
    e.asistir("Atraso")
    assert e.estado()["motivo"] == "No revisada: llegada tardía"


def test_entrega_tardia_y_llegada_tardia_muestran_los_dos_motivos(e):
    datos = e.repos["entregas"]
    e.entregar()
    registro = datos.obtener(1)
    registro["fecha_hora_entrega"] = datetime(2026, 3, 4, 6, 50).isoformat()
    datos.guardar(1, registro)
    e.asistir("Atraso")
    assert e.estado()["motivo"] == "No revisada: entrega tardía y llegada tardía"


def test_la_presencia_no_convierte_en_puntual_una_entrega_tardia(e):
    e.entregar(ahora=LIMITE)
    e.asistir("Presente")
    assert e.estado()["estado"] == "No revisada"


def test_la_puntualidad_se_toma_de_la_asistencia_de_la_hu1_sin_duplicarla(e):
    e.entregar()
    assert e.estado()["puntualidad"] == "Sin registrar"
    e.asistir("Presente")
    assert e.estado()["puntualidad"] == "Puntual"
    assert set(e.repos["asistencias"].listar()) == {MATERIA}


def test_no_se_puede_revisar_sin_puntualidad_confirmada(e):
    e.entregar()
    with pytest.raises(ValueError, match=MSG_NO_SE_PUEDE_REVISAR):
        e.revision.registrarRevision(1, False, "", CLASE)


def test_revision_sin_errores_deja_la_tarea_revisada(e):
    e.entregar()
    e.asistir("Presente")
    estado = e.revision.registrarRevision(1, False, "Muy bien", CLASE)
    assert estado["estado"] == "Revisada" and estado["observaciones"] == "Muy bien"
    assert estado["reentrega_habilitada"] is False


def test_revision_con_errores_y_presente_habilita_la_reentrega(e):
    e.entregar()
    e.asistir("Presente")
    estado = e.revision.registrarRevision(1, True, "Falta el punto 2", CLASE)
    assert estado["estado"] == "Reentrega" and estado["reentrega_habilitada"] is True
    assert estado["observaciones"] == "Falta el punto 2"


def preparar_reentrega(e):
    e.entregar()
    e.asistir("Presente")
    e.revision.registrarRevision(1, True, "Falta el punto 2", CLASE)


def test_reentrega_bloqueada_si_el_estudiante_ya_no_figura_presente(e):
    preparar_reentrega(e)
    e.asistir("Ausente")
    with pytest.raises(ValueError, match=MSG_REENTREGA_SIN_PRESENCIA):
        e.revision.solicitarReentrega(1, ["b.pdf"], [], REENTREGA)
    estado = e.estado()
    assert estado["estado"] == "No revisada" and estado["reentrega_habilitada"] is False
    assert e.repos["entregas"].obtener(1)["archivos"] == ["a.pdf"]


def test_reentrega_con_pdf_valido_reemplaza_la_version_anterior(e):
    preparar_reentrega(e)
    resultado = e.revision.solicitarReentrega(1, ["b.pdf"], [], REENTREGA)
    assert resultado["mensaje"].startswith("Reentrega registrada")
    guardada = e.repos["entregas"].obtener(1)
    assert guardada["archivos"] == ["b.pdf"] and guardada["fecha_hora_entrega"] == REENTREGA.isoformat()


def test_despues_de_reentregar_el_estado_vuelve_a_pendiente_de_revision(e):
    preparar_reentrega(e)
    estado = e.revision.solicitarReentrega(1, ["b.pdf"], [], REENTREGA)["revision"]
    assert estado["estado"] == "Pendiente de revisión" and estado["observaciones"] is None
    assert estado["reentrega_habilitada"] is True and estado["version"] == 2 and estado["a_tiempo"] is True


@pytest.mark.parametrize("archivos, enlaces", [(["b.docx"], []), (["b.pdf"], ["https://x.com"]), ([None], [])])
def test_la_reentrega_rechaza_lo_que_no_sea_pdf_sin_cambiar_nada(e, archivos, enlaces):
    preparar_reentrega(e)
    with pytest.raises(ValueError, match=MSG_SOLO_PDF):
        e.revision.solicitarReentrega(1, archivos, enlaces, REENTREGA)
    assert e.repos["entregas"].obtener(1)["archivos"] == ["a.pdf"] and e.estado()["estado"] == "Reentrega"


def test_no_hay_reentrega_si_la_tarea_no_fue_revisada_con_errores(e):
    e.entregar()
    e.asistir("Presente")
    with pytest.raises(ValueError, match=MSG_REENTREGA_NO_HABILITADA):
        e.revision.solicitarReentrega(1, ["b.pdf"], [], REENTREGA)


def test_el_historial_conserva_las_versiones_y_sus_revisiones(e):
    preparar_reentrega(e)
    e.revision.solicitarReentrega(1, ["b.pdf"], [], REENTREGA)
    versiones = e.revision.obtenerHistorial(1)["versiones"]
    assert [(v["version"], v["archivos"], v["vigente"]) for v in versiones] == [(1, ["a.pdf"], False), (2, ["b.pdf"], True)]
    assert versiones[0]["con_errores"] is True and versiones[0]["observaciones"] == "Falta el punto 2"
    assert versiones[1]["con_errores"] is None


def test_varias_reentregas_acumulan_versiones(e):
    preparar_reentrega(e)
    e.revision.solicitarReentrega(1, ["b.pdf"], [], REENTREGA)
    e.revision.registrarRevision(1, True, "Aún falta", datetime(2026, 3, 4, 8, 15))
    e.revision.solicitarReentrega(1, ["c.pdf"], [], datetime(2026, 3, 4, 8, 30))
    assert [v["archivos"] for v in e.revision.obtenerHistorial(1)["versiones"]] == [["a.pdf"], ["b.pdf"], ["c.pdf"]]
    assert e.estado()["a_tiempo"] is True


def test_cambiar_la_entrega_actualiza_el_resultado_solo(e):
    e.entregar()
    e.asistir("Presente")
    assert e.estado()["estado"] == "Pendiente de revisión"
    registro = e.repos["entregas"].obtener(1)
    registro["fecha_hora_entrega"] = datetime(2026, 3, 4, 6, 50).isoformat()
    e.repos["entregas"].guardar(1, registro)
    assert e.estado()["motivo"] == "No revisada: entrega tardía"


def test_cambiar_la_asistencia_actualiza_el_resultado_y_descarta_la_revision_invalida(e):
    e.entregar()
    e.asistir("Presente")
    e.revision.registrarRevision(1, True, "Falta", CLASE)
    e.asistir("Atraso")
    estado = e.estado()
    assert estado["estado"] == "No revisada" and estado["observaciones"] is None and estado["con_errores"] is None
    e.asistir("Presente")
    assert e.estado()["estado"] == "Reentrega"


def test_listar_revisiones_incluye_todas_las_tareas_en_orden(e):
    e.registrarTarea(2, datetime(2026, 3, 6, 6, 45))
    e.entregar(1)
    e.asistir("Presente")
    lista = e.revision.listarRevisiones()
    assert [(r["numero"], r["estado"]) for r in lista] == [(1, "Pendiente de revisión"), (2, "Pendiente")]


def test_la_clase_de_cada_tarea_es_la_de_su_fecha_limite(e):
    e.registrarTarea(2, datetime(2026, 3, 6, 6, 45))
    e.entregar(2)
    e.asistir("Presente", DIA_CLASE)
    assert e.estado(2)["puntualidad"] == "Sin registrar"
    e.asistir("Atraso", date(2026, 3, 6))
    assert e.estado(2)["motivo"] == "No revisada: llegada tardía"


def test_los_datos_persisten_en_sqlite_despues_de_reiniciar(tmp_path):
    ruta = str(tmp_path / "aula.db")

    def abrir():
        conexion = sqlite3.connect(ruta)
        return Entorno({n: RepositorioSqlite(conexion, n) for n in
                        ("tareas", "entregas", "equipos", "penalizaciones", "revisiones", "asistencias")})

    primero = abrir()
    primero.registrarTarea()
    primero.entregar()
    primero.asistir("Presente")
    primero.revision.registrarRevision(1, True, "Falta el punto 2", CLASE)
    primero.revision.solicitarReentrega(1, ["b.pdf"], [], REENTREGA)
    primero.revision.registrarRevision(1, True, "Otro error", datetime(2026, 3, 4, 8, 15))

    segundo = abrir()
    estado = segundo.estado()
    assert estado["estado"] == "Reentrega" and estado["observaciones"] == "Otro error" and estado["archivos"] == ["b.pdf"]
    assert [v["archivos"] for v in segundo.revision.obtenerHistorial(1)["versiones"]] == [["a.pdf"], ["b.pdf"]]


# ---- plazo de la reentrega: hasta la siguiente clase, donde se revisa de nuevo ----
SIGUIENTE_CLASE = datetime(2026, 3, 6, 6, 45)   # viernes, siguiente a la clase del miércoles


def test_se_puede_reenviar_las_veces_necesarias_antes_de_la_siguiente_clase(e):
    preparar_reentrega(e)
    for hora, nombre in ((8, "b.pdf"), (9, "c.pdf"), (10, "d.pdf")):
        estado = e.revision.solicitarReentrega(1, [nombre], [], datetime(2026, 3, 5, hora, 0))["revision"]
        assert estado["estado"] == "Pendiente de revisión" and estado["reentrega_habilitada"] is True
    assert e.repos["entregas"].obtener(1)["archivos"] == ["d.pdf"]
    assert [v["archivos"] for v in e.revision.obtenerHistorial(1)["versiones"]] == [["a.pdf"], ["b.pdf"], ["c.pdf"], ["d.pdf"]]


def test_el_plazo_de_la_reentrega_es_el_cierre_de_la_siguiente_clase(e):
    preparar_reentrega(e)
    assert e.estado()["plazo_reentrega"] == SIGUIENTE_CLASE.isoformat()


def test_un_minuto_antes_de_la_siguiente_clase_todavia_se_puede_reentregar(e):
    preparar_reentrega(e)
    e.revision.solicitarReentrega(1, ["b.pdf"], [], datetime(2026, 3, 6, 6, 44))


def test_en_la_siguiente_clase_la_reentrega_ya_no_se_acepta(e):
    preparar_reentrega(e)
    with pytest.raises(ValueError, match=MSG_REENTREGA_FUERA_DE_PLAZO):
        e.revision.solicitarReentrega(1, ["b.pdf"], [], SIGUIENTE_CLASE)
    assert e.repos["entregas"].obtener(1)["archivos"] == ["a.pdf"]


def test_con_el_plazo_vencido_el_estado_explica_por_que_no_hay_reentrega(e):
    preparar_reentrega(e)
    estado = e.revision.obtenerEstado(1, ahora=SIGUIENTE_CLASE)
    assert estado["estado"] == "Reentrega" and estado["reentrega_habilitada"] is False
    assert estado["mensaje_reentrega"] == MSG_REENTREGA_FUERA_DE_PLAZO


def test_el_plazo_vencido_tambien_corta_los_reenvios(e):
    preparar_reentrega(e)
    e.revision.solicitarReentrega(1, ["b.pdf"], [], datetime(2026, 3, 5, 9, 0))
    with pytest.raises(ValueError, match=MSG_REENTREGA_FUERA_DE_PLAZO):
        e.revision.solicitarReentrega(1, ["c.pdf"], [], SIGUIENTE_CLASE)


def test_si_el_docente_vuelve_a_marcar_errores_el_plazo_pasa_a_la_clase_siguiente(e):
    preparar_reentrega(e)
    e.revision.solicitarReentrega(1, ["b.pdf"], [], datetime(2026, 3, 5, 9, 0))
    segunda = datetime(2026, 3, 6, 7, 30)   # clase del viernes
    estado = e.revision.registrarRevision(1, True, "Aún falta", segunda)
    assert estado["estado"] == "Reentrega" and estado["plazo_reentrega"] == datetime(2026, 3, 10, 6, 45).isoformat()
    e.revision.solicitarReentrega(1, ["c.pdf"], [], datetime(2026, 3, 9, 20, 0))


def test_sin_revision_previa_no_hay_plazo_de_reentrega(e):
    e.entregar()
    e.asistir("Presente")
    assert e.estado()["plazo_reentrega"] is None
