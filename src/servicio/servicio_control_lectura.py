from datetime import datetime

from src.constantes import (
    MSG_CONTROL_NO_EXISTE,
    MSG_ERROR_GUARDADO,
    MSG_FECHAS_INVALIDAS,
    MSG_LECTURA_NO_EXISTE,
    TABLA_CONTROLES,
    TABLA_ESTUDIANTES_LECTURA,
    TABLA_LECTURAS,
    TABLA_RESPUESTAS_CONTROL,
)
from src.modelo.control_lectura import ControlLectura
from src.modelo.estudiante import Estudiante
from src.modelo.lectura import Lectura
from src.modelo.pregunta import Pregunta
from src.modelo.respuesta_control import RespuestaControl

VENTANA_SIN_ABRIR = "Aún no abre"
VENTANA_ABIERTO = "Abierto"
VENTANA_CERRADO = "Cerrado"


class ErrorGuardado(Exception):
    """El almacenamiento falló: el control no quedó registrado como enviado."""


class ServicioControlLectura:
    def __init__(self, repo_lecturas, repo_controles, repo_respuestas, repo_estudiantes):
        self._repo_lecturas = repo_lecturas
        self._repo_controles = repo_controles
        self._repo_respuestas = repo_respuestas
        self._repo_estudiantes = repo_estudiantes

    @classmethod
    def desdeContexto(cls, contexto):
        return cls(
            contexto.repositorio(TABLA_LECTURAS),
            contexto.repositorio(TABLA_CONTROLES),
            contexto.repositorio(TABLA_RESPUESTAS_CONTROL),
            contexto.repositorio(TABLA_ESTUDIANTES_LECTURA),
        )

    # ---------- docente: lecturas y controles ----------
    def _siguienteId(self, repositorio):
        return len(repositorio.listar()) + 1

    def registrarLectura(self, datos):
        lectura = Lectura(self._siguienteId(self._repo_lecturas), datos.get("titulo"), datos.get("autor"),
                          datos.get("archivo"), datos.get("enlace"))
        lectura.guardar(self._repo_lecturas)
        return lectura.aDiccionario()

    def listarLecturas(self):
        return sorted(self._repo_lecturas.listar().values(), key=lambda lectura: lectura["id"])

    def _lectura(self, id_lectura):
        datos = self._repo_lecturas.obtener(id_lectura)
        if datos is None:
            raise ValueError(MSG_LECTURA_NO_EXISTE)
        return Lectura.desdeDiccionario(datos)

    @staticmethod
    def _fecha(texto):
        try:
            return datetime.fromisoformat(texto)
        except (TypeError, ValueError):
            raise ValueError(MSG_FECHAS_INVALIDAS) from None

    def publicarControl(self, datos):
        id_lectura = datos.get("id_lectura")
        if id_lectura is not None:
            self._lectura(id_lectura)
        extras = {}
        if datos.get("puntaje_maximo") not in (None, ""):
            extras["puntaje_maximo"] = datos["puntaje_maximo"]
        control = ControlLectura(
            self._siguienteId(self._repo_controles),
            datos.get("titulo"),
            id_lectura,
            [Pregunta(p.get("enunciado"), p.get("obligatoria", True)) for p in datos.get("preguntas") or []],
            self._fecha(datos.get("apertura")),
            self._fecha(datos.get("cierre")),
            **extras,
        )
        control.guardar(self._repo_controles)
        return control.aDiccionario()

    def _control(self, id_control):
        datos = self._repo_controles.obtener(id_control)
        if datos is None:
            raise ValueError(MSG_CONTROL_NO_EXISTE)
        return ControlLectura.desdeDiccionario(datos)

    # ---------- estudiantes ----------
    @staticmethod
    def _clave(id_control, nombre):
        return f"{id_control}|{nombre.casefold()}"

    def registrarEstudiante(self, nombre):
        nombre = Estudiante(nombre).nombre
        self._repo_estudiantes.guardar(nombre.casefold(), {"nombre": nombre})
        return nombre

    def _respuesta(self, id_control, nombre):
        datos = self._repo_respuestas.obtener(self._clave(id_control, nombre))
        if datos is None:
            return RespuestaControl(id_control, nombre)
        return RespuestaControl.desdeDiccionario(datos)

    def _guardarRespuesta(self, respuesta):
        self._repo_respuestas.guardar(self._clave(respuesta.id_control, respuesta.estudiante), respuesta.aDiccionario())

    @staticmethod
    def _ventana(control, ahora):
        if ahora < control.apertura:
            return VENTANA_SIN_ABRIR
        return VENTANA_ABIERTO if ahora <= control.cierre else VENTANA_CERRADO

    def _vistaEstudiante(self, control, nombre, ahora, detalle):
        respuesta = self._respuesta(control.id, nombre) if nombre else RespuestaControl(control.id, "")
        lectura = self._lectura(control.id_lectura).aDiccionario()
        vista = {
            "id": control.id,
            "titulo": control.titulo,
            "lectura": lectura,
            "apertura": control.apertura.isoformat(),
            "cierre": control.cierre.isoformat(),
            "puntaje_maximo": str(control.puntaje_maximo),
            "ventana": self._ventana(control, ahora),
            "puede_responder": bool(nombre) and respuesta.puedeResponder(control, ahora),
            "estado": respuesta.estado.value,
            "puntualidad": respuesta.puntualidad.value if respuesta.puntualidad else None,
            "fecha_hora_envio": respuesta.fecha_hora_envio.isoformat() if respuesta.fecha_hora_envio else None,
            "intento_habilitado": respuesta.intento_habilitado,
            "calificacion_publicada": respuesta.calificacion_publicada,
            "nota": None,
            "retroalimentacion": None,
        }
        if respuesta.calificacion_publicada:
            vista["nota"] = str(respuesta.nota)
            vista["retroalimentacion"] = respuesta.retroalimentacion
        if detalle:
            vista["preguntas"] = [pregunta.aDiccionario() for pregunta in control.preguntas]
            vista["respuestas"] = respuesta.respuestas
        return vista

    def listarControles(self, nombre, ahora):
        nombre = Estudiante(nombre).nombre if nombre else None
        controles = sorted((ControlLectura.desdeDiccionario(d) for d in self._repo_controles.listar().values()),
                           key=lambda control: control.apertura)
        return [self._vistaEstudiante(control, nombre, ahora, detalle=False) for control in controles]

    def obtenerControl(self, id_control, nombre, ahora):
        nombre = Estudiante(nombre).nombre if nombre else None
        return self._vistaEstudiante(self._control(id_control), nombre, ahora, detalle=True)

    def enviarRespuestas(self, id_control, nombre, respuestas, ahora):
        nombre = Estudiante(nombre).nombre
        control = self._control(id_control)
        lectura = self._lectura(control.id_lectura)
        respuesta = self._respuesta(id_control, nombre)
        mensaje = respuesta.enviar(control, lectura, respuestas, ahora)
        try:
            self._guardarRespuesta(respuesta)
            self.registrarEstudiante(nombre)
        except Exception as error:
            raise ErrorGuardado(MSG_ERROR_GUARDADO) from error
        return {"mensaje": mensaje, "estado": respuesta.estado.value, "puntualidad": respuesta.puntualidad.value,
                "fecha_hora_envio": respuesta.fecha_hora_envio.isoformat()}

    # ---------- docente: revisión ----------
    def _nombresConocidos(self, id_control):
        nombres = {datos["nombre"] for datos in self._repo_estudiantes.listar().values()}
        for datos in self._repo_respuestas.listar().values():
            if datos["id_control"] == id_control:
                nombres.add(datos["estudiante"])
        return sorted(nombres, key=str.casefold)

    def listarRevision(self, id_control):
        control = self._control(id_control)
        filas = []
        for nombre in self._nombresConocidos(id_control):
            respuesta = self._respuesta(id_control, nombre)
            filas.append({**respuesta.aDiccionario(), "estado_revision": respuesta.estadoRevision()})
        return {"control": control.aDiccionario(), "lectura": self._lectura(control.id_lectura).aDiccionario(),
                "preguntas": [pregunta.aDiccionario() for pregunta in control.preguntas], "estudiantes": filas}

    def habilitarNuevoIntento(self, id_control, nombre):
        self._control(id_control)
        nombre = self.registrarEstudiante(nombre)
        respuesta = self._respuesta(id_control, nombre)
        respuesta.habilitarNuevoIntento()
        self._guardarRespuesta(respuesta)

    def calificar(self, id_control, nombre, nota, retroalimentacion, publicar):
        control = self._control(id_control)
        respuesta = self._respuesta(id_control, Estudiante(nombre).nombre)
        respuesta.calificar(nota, retroalimentacion, publicar, control.puntaje_maximo)
        self._guardarRespuesta(respuesta)