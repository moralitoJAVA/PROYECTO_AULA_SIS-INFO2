from src.constantes import (
    MATERIA_POR_DEFECTO,
    MSG_TAREA_NO_EXISTE,
    TABLA_ASISTENCIAS,
    TABLA_ENTREGAS,
    TABLA_REVISIONES,
    TABLA_TAREAS,
)
from src.modelo.entrega import Entrega
from src.modelo.reentrega import Reentrega
from src.modelo.revision_tareas import RevisionTareas
from src.modelo.tarea import Tarea
from src.servicio.servicio_asistencia import ServicioAsistencia


class ServicioRevisionTareas:
    """Casos de uso de la HU4. Reutiliza las entregas (HU2) y la asistencia (HU1)."""

    def __init__(self, repo_tareas, repo_entregas, repo_revisiones, servicio_asistencia, materia=MATERIA_POR_DEFECTO):
        self._repo_tareas = repo_tareas
        self._repo_entregas = repo_entregas
        self._repo_revisiones = repo_revisiones
        self._asistencia = servicio_asistencia
        self._materia = materia

    @classmethod
    def desdeContexto(cls, contexto):
        return cls(
            contexto.repositorio(TABLA_TAREAS),
            contexto.repositorio(TABLA_ENTREGAS),
            contexto.repositorio(TABLA_REVISIONES),
            ServicioAsistencia(contexto.repositorio(TABLA_ASISTENCIAS)),
        )

    # ---- lectura de las fuentes de HU1 y HU2 (nunca se duplican) ----
    def _tarea(self, numero):
        datos = self._repo_tareas.obtener(numero)
        if datos is None:
            raise ValueError(MSG_TAREA_NO_EXISTE)
        return Tarea.desdeDiccionario(datos)

    def _entrega(self, tarea):
        datos = self._repo_entregas.obtener(tarea.numero)
        return None if datos is None else Entrega.desdeDiccionario(datos, tarea)

    def _estadoAsistencia(self, tarea, materia):
        """Asistencia de la clase en la que vence la tarea (HU1), o None si aún no se registró."""
        historial = dict(self._asistencia.obtenerHistorial(materia))
        return historial.get(tarea.fecha_limite.date())

    def _evaluar(self, tarea, materia, ahora=None):
        """Construye la revisión y la recalcula con la entrega y la asistencia vigentes."""
        revision = RevisionTareas.desdeDiccionario(self._repo_revisiones.obtener(tarea.numero), tarea.numero, tarea.fecha_limite)
        entrega = self._entrega(tarea)
        fecha_entrega = entrega.fecha_hora_entrega if entrega else None
        revision.evaluarRevision(fecha_entrega, self._estadoAsistencia(tarea, materia), ahora)
        return revision, entrega

    # ---- consultas ----
    def _describir(self, revision, tarea, entrega):
        revisada = revision.estado.value in ("Revisada", "Reentrega")
        return {
            "numero": tarea.numero,
            "titulo": tarea.titulo,
            "fecha_limite": tarea.fecha_limite.isoformat(),
            "fecha_entrega": revision.fecha_entrega.isoformat() if revision.fecha_entrega else None,
            "archivos": list(entrega.archivos) if entrega else [],
            "version": len(revision.versiones) + 1 if entrega else None,
            "a_tiempo": revision.a_tiempo,
            "puntualidad": revision.puntualidad,
            "estado": revision.estado.value,
            "motivo": revision.obtenerMotivo(),
            "con_errores": revision.con_errores if revisada else None,
            "observaciones": revision.observaciones if revisada else None,
            "puede_revisarse": revision.puedeRevisarse(),
            "reentrega_habilitada": revision.reentrega_habilitada,
            "plazo_reentrega": revision.fechaLimiteReentrega().isoformat() if revision.fechaLimiteReentrega() else None,
            "mensaje_reentrega": revision.mensaje_reentrega,
        }

    def _sincronizar(self, revision, entrega):
        """Guarda el resultado recalculado cuando cambió, para que persista entre reinicios."""
        if entrega is None:
            return
        nuevo = revision.aDiccionario()
        if self._repo_revisiones.obtener(revision.numero) != nuevo:
            revision.guardar(self._repo_revisiones)

    def obtenerEstado(self, numero, materia=None, ahora=None):
        tarea = self._tarea(numero)
        revision, entrega = self._evaluar(tarea, materia or self._materia, ahora)
        self._sincronizar(revision, entrega)
        return self._describir(revision, tarea, entrega)

    def listarRevisiones(self, materia=None, ahora=None):
        numeros = sorted(int(clave) for clave in self._repo_tareas.listar())
        return [self.obtenerEstado(numero, materia, ahora) for numero in numeros]

    def recalcular(self, numero, materia=None, ahora=None):
        return self.obtenerEstado(numero, materia, ahora)

    def obtenerHistorial(self, numero, materia=None):
        tarea = self._tarea(numero)
        revision, entrega = self._evaluar(tarea, materia or self._materia)
        versiones = [{**version, "vigente": False} for version in revision.versiones]
        if entrega:
            vigente = revision.estado.value in ("Revisada", "Reentrega")
            versiones.append({
                "version": len(revision.versiones) + 1,
                "archivos": list(entrega.archivos),
                "enlaces": list(entrega.enlaces),
                "fecha_hora_entrega": entrega.fecha_hora_entrega.isoformat(),
                "con_errores": revision.con_errores if vigente else None,
                "observaciones": revision.observaciones if vigente else None,
                "fecha_revision": revision.fecha_revision.isoformat() if vigente and revision.fecha_revision else None,
                "vigente": True,
            })
        return {"numero": numero, "titulo": tarea.titulo, "versiones": versiones}

    # ---- revisión del docente ----
    def registrarRevision(self, numero, con_errores, observaciones, ahora, materia=None):
        tarea = self._tarea(numero)
        revision, entrega = self._evaluar(tarea, materia or self._materia)
        revision.registrarResultado(con_errores, observaciones, ahora)
        revision.evaluarRevision(revision.fecha_entrega, self._estadoAsistencia(tarea, materia or self._materia), ahora)
        revision.guardar(self._repo_revisiones)
        return self._describir(revision, tarea, entrega)

    # ---- reentrega ----
    def solicitarReentrega(self, numero, archivos, enlaces, ahora, materia=None):
        materia = materia or self._materia
        tarea = self._tarea(numero)
        revision, entrega = self._evaluar(tarea, materia, ahora)
        estado_asistencia = self._estadoAsistencia(tarea, materia)
        reentrega = Reentrega()
        reentrega.habilitarReentrega(revision, estado_asistencia, ahora)
        reentrega.validarPDF(archivos, enlaces)
        reentrega.reemplazarEntrega(entrega, revision, archivos, ahora)
        revision.evaluarRevision(entrega.fecha_hora_entrega, estado_asistencia, ahora)
        reentrega.guardar(entrega, revision, self._repo_entregas, self._repo_revisiones)
        return {"mensaje": reentrega.notificarRevision(), "revision": self._describir(revision, tarea, entrega)}
