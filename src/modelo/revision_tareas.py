from datetime import datetime, timedelta

from src.constantes import (
    DIAS_DE_CLASE,
    ESTADOS,
    ESTADOS_QUE_ASISTEN,
    ESTADOS_REVISION,
    FORMATO_NO_REVISADA,
    HORA_LIMITE,
    MAX_OBSERVACIONES,
    MOTIVO_ENTREGA_TARDIA,
    MOTIVO_INASISTENCIA,
    MOTIVO_LLEGADA_TARDIA,
    MSG_CON_ERRORES_INVALIDO,
    MSG_NO_SE_PUEDE_REVISAR,
    MSG_OBSERVACIONES_INVALIDAS,
    MSG_OBSERVACIONES_OBLIGATORIAS,
    MSG_REENTREGA_FUERA_DE_PLAZO,
    MSG_REENTREGA_SIN_PRESENCIA,
    PUNTUAL,
    PUNTUALIDAD_AUSENTE,
    PUNTUALIDAD_LICENCIA,
    PUNTUALIDAD_SIN_REGISTRO,
    PUNTUALIDAD_TARDIA,
    SEPARADOR_MOTIVOS,
)

ETIQUETAS_PUNTUALIDAD = {
    ESTADOS.PRESENTE: PUNTUAL,
    ESTADOS.ATRASO: PUNTUALIDAD_TARDIA,
    ESTADOS.AUSENTE: PUNTUALIDAD_AUSENTE,
    ESTADOS.LICENCIA: PUNTUALIDAD_LICENCIA,
}


class RevisionTareas:
    """Revisión en clase de la entrega de una tarea.

    El estado se deriva siempre de la entrega vigente (HU2) y de la asistencia de
    la clase (HU1); solo el resultado del docente y el historial se conservan.
    """

    def __init__(self, numero, fecha_limite):
        self.numero = numero
        self.fecha_limite = fecha_limite
        self.fecha_entrega = None
        self.versiones = []
        self.con_errores = None
        self.observaciones = None
        self.fecha_revision = None
        self.estado = ESTADOS_REVISION.PENDIENTE
        self.motivos = []
        self.puntualidad = PUNTUALIDAD_SIN_REGISTRO
        self.a_tiempo = None
        self.reentrega_habilitada = False
        self.mensaje_reentrega = None

    # ---- reglas de entrega y puntualidad ----
    def validarEntrega(self, fecha_entrega):
        """True si se entregó antes del límite; el instante exacto del límite ya es tarde."""
        if fecha_entrega is None:
            return None
        return fecha_entrega < self.fecha_limite

    def validarPuntualidad(self, estado_asistencia):
        if estado_asistencia is None:
            return PUNTUALIDAD_SIN_REGISTRO
        return ETIQUETAS_PUNTUALIDAD[estado_asistencia]

    @staticmethod
    def resolverEstado(a_tiempo, puntual, presente, revisada=False, con_errores=False):
        """Tabla de decisión de la HU4. Devuelve (estado, reentrega_habilitada)."""
        if a_tiempo is None:
            return ESTADOS_REVISION.PENDIENTE, False
        if not a_tiempo or not puntual:
            return ESTADOS_REVISION.NO_REVISADA, False
        if not revisada:
            return ESTADOS_REVISION.PENDIENTE_DE_REVISION, False
        if not con_errores:
            return ESTADOS_REVISION.REVISADA, False
        if presente:
            return ESTADOS_REVISION.REENTREGA, True
        return ESTADOS_REVISION.REVISADA, False

    def obtenerMotivo(self):
        if not self.motivos:
            return None
        return FORMATO_NO_REVISADA.format(motivos=SEPARADOR_MOTIVOS.join(self.motivos))

    # ---- transiciones de estado ----
    def marcarPendiente(self):
        self.estado = ESTADOS_REVISION.PENDIENTE
        self.motivos = []
        self.reentrega_habilitada = False

    def marcarNoRevisada(self, motivos):
        self.estado = ESTADOS_REVISION.NO_REVISADA
        self.motivos = list(motivos)
        self.reentrega_habilitada = False

    def marcarPendienteRevision(self):
        self.estado = ESTADOS_REVISION.PENDIENTE_DE_REVISION
        self.motivos = []
        self.reentrega_habilitada = False

    def _motivos(self, a_tiempo, estado_asistencia):
        motivos = []
        if not a_tiempo:
            motivos.append(MOTIVO_ENTREGA_TARDIA)
        if estado_asistencia == ESTADOS.ATRASO:
            motivos.append(MOTIVO_LLEGADA_TARDIA)
        elif estado_asistencia in (ESTADOS.AUSENTE, ESTADOS.LICENCIA):
            motivos.append(MOTIVO_INASISTENCIA)
        return motivos

    def evaluarRevision(self, fecha_entrega, estado_asistencia, ahora=None):
        """Recalcula estado, motivo y reentrega desde los datos vigentes."""
        self.fecha_entrega = fecha_entrega
        fecha_plazo = fecha_entrega
        if self.versiones:
            fecha_plazo = datetime.fromisoformat(self.versiones[0]["fecha_hora_entrega"])
        self.a_tiempo = self.validarEntrega(fecha_plazo)
        self.puntualidad = self.validarPuntualidad(estado_asistencia)
        puntual = estado_asistencia == ESTADOS.PRESENTE
        presente = estado_asistencia in ESTADOS_QUE_ASISTEN
        if estado_asistencia is None and self.a_tiempo:
            estado, habilitada = ESTADOS_REVISION.PENDIENTE_DE_REVISION, False
        else:
            estado, habilitada = self.resolverEstado(
                self.a_tiempo, puntual, presente, self.con_errores is not None, bool(self.con_errores))
        # Mientras espera la nueva revisión, el estudiante puede reenviar las veces que necesite.
        puede_reenviar = estado == ESTADOS_REVISION.PENDIENTE_DE_REVISION and bool(self.versiones) and presente
        self.estado, self.reentrega_habilitada = estado, habilitada or puede_reenviar
        self.mensaje_reentrega = None
        if self.reentrega_habilitada and self.reentregaVencida(ahora):
            self.reentrega_habilitada = False
            self.mensaje_reentrega = MSG_REENTREGA_FUERA_DE_PLAZO
        self.motivos = self._motivos(self.a_tiempo, estado_asistencia) if estado == ESTADOS_REVISION.NO_REVISADA else []
        self.mensaje_reentrega = self.mensaje_reentrega or self._mensajeReentrega(estado, presente)

    def _mensajeReentrega(self, estado, presente):
        if self.con_errores and estado == ESTADOS_REVISION.REVISADA and not presente:
            return MSG_REENTREGA_SIN_PRESENCIA
        return None

    recalcular = evaluarRevision

    # ---- plazo de la reentrega ----
    def _fechaUltimaRevision(self):
        if self.fecha_revision:
            return self.fecha_revision
        for version in reversed(self.versiones):
            if version.get("fecha_revision"):
                return datetime.fromisoformat(version["fecha_revision"])
        return None

    def fechaLimiteReentrega(self):
        """Hora de cierre de la siguiente clase a la última revisión (06:45), o None si aún no hubo revisión."""
        revision = self._fechaUltimaRevision()
        if revision is None:
            return None
        dia = revision.date() + timedelta(days=1)
        while dia.weekday() not in DIAS_DE_CLASE:
            dia += timedelta(days=1)
        return datetime.combine(dia, HORA_LIMITE)

    def reentregaVencida(self, ahora):
        limite = self.fechaLimiteReentrega()
        return ahora is not None and limite is not None and ahora >= limite

    # ---- resultado del docente ----
    def puedeRevisarse(self):
        return self.estado == ESTADOS_REVISION.PENDIENTE_DE_REVISION and self.puntualidad == PUNTUAL

    def registrarResultado(self, con_errores, observaciones, ahora):
        if not self.puedeRevisarse():
            raise ValueError(MSG_NO_SE_PUEDE_REVISAR)
        if not isinstance(con_errores, bool):
            raise ValueError(MSG_CON_ERRORES_INVALIDO)
        if observaciones is None:
            observaciones = ""
        if not isinstance(observaciones, str) or len(observaciones) > MAX_OBSERVACIONES:
            raise ValueError(MSG_OBSERVACIONES_INVALIDAS)
        observaciones = observaciones.strip()
        if con_errores and not observaciones:
            raise ValueError(MSG_OBSERVACIONES_OBLIGATORIAS)
        self.con_errores = con_errores
        self.observaciones = observaciones
        self.fecha_revision = ahora

    def descartarResultado(self):
        self.con_errores = None
        self.observaciones = None
        self.fecha_revision = None

    # ---- persistencia ----
    def guardar(self, repositorio):
        repositorio.guardar(self.numero, self.aDiccionario())

    def aDiccionario(self):
        return {
            "numero": self.numero,
            "con_errores": self.con_errores,
            "observaciones": self.observaciones,
            "fecha_revision": self.fecha_revision.isoformat() if self.fecha_revision else None,
            "versiones": self.versiones,
            "estado": self.estado.value,
            "motivo": self.obtenerMotivo(),
        }

    @classmethod
    def desdeDiccionario(cls, datos, numero, fecha_limite):
        revision = cls(numero, fecha_limite)
        if datos:
            revision.con_errores = datos["con_errores"]
            revision.observaciones = datos["observaciones"]
            if datos["fecha_revision"]:
                revision.fecha_revision = datetime.fromisoformat(datos["fecha_revision"])
            revision.versiones = list(datos["versiones"])
        return revision
