from datetime import date, datetime

from src.constantes import (
    ESTADOS,
    FORMATO_MENSAJE_FRUTA,
    FORMATO_MENSAJE_PUNTUAL,
    MATERIA_POR_DEFECTO,
    MSG_FECHA_INGRESO_INVALIDA,
    MSG_FUERA_DE_HORARIO,
    MSG_INGRESO_YA_REGISTRADO,
    MSG_NO_ES_DIA_DE_CLASE,
    SANCION_DEBE_FRUTA,
    SANCION_DIA_SIN_CLASES,
    SANCION_FUERA_DE_HORARIO,
    SANCION_PUNTUAL,
    TABLA_ASISTENCIAS,
    TABLA_INGRESOS,
)
from src.modelo.sancion_llegada import SancionLlegada
from src.servicio.servicio_asistencia import ServicioAsistencia

ASISTENCIA_POR_SANCION = {SANCION_PUNTUAL: ESTADOS.PRESENTE, SANCION_DEBE_FRUTA: ESTADOS.ATRASO}


class ServicioSancionLlegada:
    """Casos de uso de la HU1. El estado de puntualidad se comparte con la HU4 a través de la asistencia."""

    def __init__(self, repo_ingresos, servicio_asistencia):
        self._repo = repo_ingresos
        self._asistencia = servicio_asistencia
        self._sancion = SancionLlegada()

    @classmethod
    def desdeContexto(cls, contexto):
        return cls(contexto.repositorio(TABLA_INGRESOS), ServicioAsistencia(contexto.repositorio(TABLA_ASISTENCIAS)))

    @staticmethod
    def interpretarMomento(texto, ahora):
        if not texto:
            return ahora
        try:
            return datetime.fromisoformat(str(texto))
        except ValueError:
            raise ValueError(MSG_FECHA_INGRESO_INVALIDA) from None

    @staticmethod
    def _clave(materia, fecha):
        return f"{materia}|{fecha.isoformat()}"

    def _validar(self, estado):
        if estado == SANCION_DIA_SIN_CLASES:
            raise ValueError(MSG_NO_ES_DIA_DE_CLASE)
        if estado == SANCION_FUERA_DE_HORARIO:
            raise ValueError(MSG_FUERA_DE_HORARIO)

    def _describir(self, momento, estado):
        hora = momento.time().replace(microsecond=0).isoformat()
        proxima = self._sancion.proxima_clase(momento.date())
        debe = estado == SANCION_DEBE_FRUTA
        mensaje = (FORMATO_MENSAJE_FRUTA.format(hora=hora, proxima=proxima) if debe
                   else FORMATO_MENSAJE_PUNTUAL.format(hora=hora))
        return {
            "fecha": momento.date().isoformat(),
            "hora_ingreso": hora,
            "estado": estado,
            "debe_fruta": debe,
            "fruta_para": proxima.isoformat() if debe else None,
            "mensaje": mensaje,
        }

    def evaluar(self, momento):
        """Evalúa sin guardar nada. Devuelve también los estados 'Día sin clases' y 'Fuera de horario'."""
        estado = self._sancion.evaluar_momento(momento)
        datos = self._describir(momento, estado)
        if estado in (SANCION_DIA_SIN_CLASES, SANCION_FUERA_DE_HORARIO):
            datos["mensaje"] = MSG_NO_ES_DIA_DE_CLASE if estado == SANCION_DIA_SIN_CLASES else MSG_FUERA_DE_HORARIO
            datos["fruta_para"] = None
        return datos

    def registrarIngreso(self, materia, momento):
        estado = self._sancion.evaluar_momento(momento)
        self._validar(estado)
        clave = self._clave(materia, momento.date())
        if self._repo.obtener(clave) is not None:
            raise ValueError(MSG_INGRESO_YA_REGISTRADO)
        datos = self._describir(momento, estado)
        self._repo.guardar(clave, {**datos, "materia": materia})
        self._asistencia.guardarAsistencia(materia, momento.date(), ASISTENCIA_POR_SANCION[estado].value)
        return datos

    def listarIngresos(self, materia=MATERIA_POR_DEFECTO, hoy=None):
        ingresos = sorted((d for d in self._repo.listar().values() if d["materia"] == materia),
                          key=lambda d: d["fecha"], reverse=True)
        hoy = (hoy or datetime.now()).date()
        pendiente = next((d for d in ingresos if d["debe_fruta"] and date.fromisoformat(d["fruta_para"]) >= hoy), None)
        return {"ingresos": ingresos, "fruta_pendiente": pendiente}