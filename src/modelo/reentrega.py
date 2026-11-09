from src.constantes import (
    ESTADOS_QUE_ASISTEN,
    ESTADOS_REVISION,
    EXTENSION_PDF,
    MSG_REENTREGA_FUERA_DE_PLAZO,
    MSG_REENTREGA_NO_HABILITADA,
    MSG_REENTREGA_REGISTRADA,
    MSG_REENTREGA_SIN_ARCHIVO,
    MSG_REENTREGA_SIN_ERRORES,
    MSG_REENTREGA_SIN_PRESENCIA,
    MSG_SOLO_PDF,
)


class Reentrega:
    """Reglas para corregir una tarea revisada con errores (HU4)."""

    def validarPresencia(self, estado_asistencia):
        if estado_asistencia not in ESTADOS_QUE_ASISTEN:
            raise ValueError(MSG_REENTREGA_SIN_PRESENCIA)

    def validarErrores(self, revision):
        if revision.estado == ESTADOS_REVISION.REENTREGA:
            return
        if revision.estado == ESTADOS_REVISION.PENDIENTE_DE_REVISION and revision.versiones:
            return  # ya reentregó y espera la nueva revisión: puede reenviar
        if revision.estado == ESTADOS_REVISION.REVISADA and revision.con_errores:
            raise ValueError(MSG_REENTREGA_SIN_PRESENCIA)
        if revision.estado == ESTADOS_REVISION.REVISADA:
            raise ValueError(MSG_REENTREGA_SIN_ERRORES)
        raise ValueError(MSG_REENTREGA_NO_HABILITADA)

    def validarPlazo(self, revision, ahora):
        if revision.reentregaVencida(ahora):
            raise ValueError(MSG_REENTREGA_FUERA_DE_PLAZO)

    def habilitarReentrega(self, revision, estado_asistencia, ahora=None):
        self.validarPresencia(estado_asistencia)
        self.validarErrores(revision)
        self.validarPlazo(revision, ahora)

    def validarPDF(self, archivos, enlaces):
        if not archivos:
            raise ValueError(MSG_REENTREGA_SIN_ARCHIVO)
        if enlaces or not all(isinstance(a, str) and a.strip().lower().endswith(EXTENSION_PDF)
                              and len(a.strip()) > len(EXTENSION_PDF) for a in archivos):
            raise ValueError(MSG_SOLO_PDF)

    def reemplazarEntrega(self, entrega, revision, archivos, ahora):
        """La nueva versión reemplaza a la vigente; la anterior solo queda en el historial."""
        revision.versiones.append({
            "version": len(revision.versiones) + 1,
            "archivos": list(entrega.archivos),
            "enlaces": list(entrega.enlaces),
            "fecha_hora_entrega": entrega.fecha_hora_entrega.isoformat(),
            "con_errores": revision.con_errores,
            "observaciones": revision.observaciones,
            "fecha_revision": revision.fecha_revision.isoformat() if revision.fecha_revision else None,
        })
        entrega.archivos = [a.strip() for a in archivos]
        entrega.enlaces = []
        entrega.fecha_hora_entrega = ahora
        revision.descartarResultado()

    def notificarRevision(self):
        return MSG_REENTREGA_REGISTRADA

    def guardar(self, entrega, revision, repo_entregas, repo_revisiones):
        entrega.guardar(repo_entregas)
        revision.guardar(repo_revisiones)
