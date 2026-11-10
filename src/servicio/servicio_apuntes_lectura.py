import re
import unicodedata
from datetime import datetime

from src.constantes import (
    MSG_CLASE_NO_EXISTE,
    MSG_ERROR_GUARDADO,
    MSG_FECHAS_INVALIDAS,
    MSG_LECTURA_FUERA_DE_CLASE,
    MSG_LECTURA_NO_EXISTE,
    MSG_PDF_NO_EXISTE,
    PUNTAJE_RESPUESTA_POR_DEFECTO,
    TABLA_APUNTES_LECTURA,
    TABLA_CLASES_LECTURA,
    TABLA_ESTUDIANTES_LECTURA,
    TABLA_LECTURAS,
    TABLA_RESPUESTAS_CLASE,
)
from src.modelo.apuntes_control_lectura import ApuntesControlLectura
from src.modelo.clase_lectura import ClaseLectura
from src.modelo.estudiante import Estudiante
from src.modelo.lectura import Lectura
from src.modelo.respuesta_clase import RespuestaClase
from src.servicio.generador_pdf_respuesta import GeneradorPdfRespuesta


class ErrorGuardado(Exception):
    """El PDF o el registro no se pudieron guardar: la respuesta no quedó enviada."""


class ServicioApuntesLectura:
    def __init__(self, repo_lecturas, repo_clases, repo_apuntes, repo_respuestas, repo_estudiantes,
                 almacen_pdf, generador_pdf=None):
        self._repo_lecturas = repo_lecturas
        self._repo_clases = repo_clases
        self._repo_apuntes = repo_apuntes
        self._repo_respuestas = repo_respuestas
        self._repo_estudiantes = repo_estudiantes
        self._almacen_pdf = almacen_pdf
        self._generador_pdf = generador_pdf or GeneradorPdfRespuesta()

    @classmethod
    def desdeContexto(cls, contexto):
        return cls(
            contexto.repositorio(TABLA_LECTURAS),
            contexto.repositorio(TABLA_CLASES_LECTURA),
            contexto.repositorio(TABLA_APUNTES_LECTURA),
            contexto.repositorio(TABLA_RESPUESTAS_CLASE),
            contexto.repositorio(TABLA_ESTUDIANTES_LECTURA),
            contexto.almacenPdf(),
        )

    # ---------- docente: bibliografía y clases ----------
    @staticmethod
    def _siguienteId(repositorio):
        return max([int(clave) for clave in repositorio.listar()] + [0]) + 1

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

    def publicarClase(self, datos):
        ids = datos.get("ids_lecturas") or []
        libre = bool(datos.get("investigacion_libre"))
        for id_lectura in ids:
            self._lectura(id_lectura)
        clase = ClaseLectura(self._siguienteId(self._repo_clases), datos.get("tema"),
                             self._fecha(datos.get("inicio")), self._fecha(datos.get("cierre_respuesta")), ids, libre)
        clase.guardar(self._repo_clases)
        return clase.aDiccionario()

    def _clase(self, id_clase):
        datos = self._repo_clases.obtener(id_clase)
        if datos is None:
            raise ValueError(MSG_CLASE_NO_EXISTE)
        return ClaseLectura.desdeDiccionario(datos)

    # ---------- estudiante ----------
    @staticmethod
    def _clave(id_clase, nombre):
        return f"{id_clase}|{nombre.casefold()}"

    def registrarEstudiante(self, nombre):
        nombre = Estudiante(nombre).nombre
        self._repo_estudiantes.guardar(nombre.casefold(), {"nombre": nombre})
        return nombre

    def _cuaderno(self, id_clase, nombre):
        datos = self._repo_apuntes.obtener(self._clave(id_clase, nombre))
        return ApuntesControlLectura.desdeDiccionario(datos) if datos else ApuntesControlLectura(id_clase, nombre)

    def _guardarCuaderno(self, cuaderno):
        self._repo_apuntes.guardar(self._clave(cuaderno.id_clase, cuaderno.estudiante), cuaderno.aDiccionario())

    def _respuesta(self, id_clase, nombre):
        datos = self._repo_respuestas.obtener(self._clave(id_clase, nombre))
        return RespuestaClase.desdeDiccionario(datos) if datos else RespuestaClase(id_clase, nombre)

    def _guardarRespuesta(self, respuesta):
        self._repo_respuestas.guardar(self._clave(respuesta.id_clase, respuesta.estudiante), respuesta.aDiccionario())

    def _bibliografia(self, clase):
        return [self._lectura(id_lectura).aDiccionario() for id_lectura in clase.ids_lecturas]

    def _vistaClase(self, clase, nombre, ahora, detalle):
        respuesta = self._respuesta(clase.id, nombre) if nombre else RespuestaClase(clase.id, "")
        vista = {
            "id": clase.id,
            "tema": clase.tema,
            "inicio": clase.inicio.isoformat(),
            "cierre_respuesta": clase.cierre_respuesta.isoformat(),
            "ventana": clase.ventana(ahora).value,
            "bibliografia": self._bibliografia(clase),
            "investigacion_libre": clase.investigacion_libre,
            "puede_responder": bool(nombre) and respuesta.puedeResponder(clase, ahora),
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
            titulos = {lectura["id"]: lectura["titulo"] for lectura in vista["bibliografia"]}
            cuaderno = self._cuaderno(clase.id, nombre) if nombre else ApuntesControlLectura(clase.id, "")
            titulos_fuentes = {f["id"]: f["titulo"] for f in cuaderno.fuentes}
            vista["apuntes"] = [{**a, "titulo_lectura": titulos.get(a["id_lectura"]) or titulos_fuentes.get(a.get("id_fuente"), "")}
                                for a in cuaderno.apuntes]
            vista["fuentes"] = cuaderno.fuentes
            vista["dudas"] = cuaderno.dudas
            vista["titulo_respuesta"] = respuesta.titulo
            vista["texto_respuesta"] = respuesta.respuesta
            vista["tiene_pdf"] = bool(respuesta.archivo_pdf and self._almacen_pdf.ruta(respuesta.archivo_pdf))
            vista["puntaje_maximo"] = str(PUNTAJE_RESPUESTA_POR_DEFECTO)
        return vista

    def listarClases(self, nombre, ahora):
        nombre = Estudiante(nombre).nombre if nombre else None
        clases = sorted((ClaseLectura.desdeDiccionario(d) for d in self._repo_clases.listar().values()),
                        key=lambda clase: clase.inicio)
        return [self._vistaClase(clase, nombre, ahora, detalle=False) for clase in clases]

    def obtenerClase(self, id_clase, nombre, ahora):
        nombre = Estudiante(nombre).nombre if nombre else None
        return self._vistaClase(self._clase(id_clase), nombre, ahora, detalle=True)

    # ----- apuntes y dudas -----
    def agregarFuente(self, id_clase, nombre, titulo, enlace, ahora):
        nombre = Estudiante(nombre).nombre
        self._clase(id_clase)
        cuaderno = self._cuaderno(id_clase, nombre)
        fuente = cuaderno.agregarFuente(titulo, enlace, ahora)
        self._guardarCuaderno(cuaderno)
        return fuente

    def editarFuente(self, id_clase, nombre, id_fuente, titulo, enlace):
        nombre = Estudiante(nombre).nombre
        self._clase(id_clase)
        cuaderno = self._cuaderno(id_clase, nombre)
        fuente = cuaderno.editarFuente(id_fuente, titulo, enlace)
        self._guardarCuaderno(cuaderno)
        return fuente

    def agregarApunte(self, id_clase, nombre, id_lectura, texto, ahora, id_fuente=None):
        nombre = Estudiante(nombre).nombre
        clase = self._clase(id_clase)
        if id_lectura is not None and not clase.incluyeLectura(id_lectura):
            raise ValueError(MSG_LECTURA_FUERA_DE_CLASE)
        cuaderno = self._cuaderno(id_clase, nombre)
        apunte = cuaderno.agregarApunte(id_lectura, texto, ahora, id_fuente)
        self._guardarCuaderno(cuaderno)
        return apunte

    def editarApunte(self, id_clase, nombre, id_apunte, texto, ahora, id_lectura=None, id_fuente=None):
        nombre = Estudiante(nombre).nombre
        clase = self._clase(id_clase)
        if id_lectura is not None and not clase.incluyeLectura(id_lectura):
            raise ValueError(MSG_LECTURA_FUERA_DE_CLASE)
        cuaderno = self._cuaderno(id_clase, nombre)
        apunte = cuaderno.editarApunte(id_apunte, texto, ahora, id_lectura, id_fuente)
        self._guardarCuaderno(cuaderno)
        return apunte

    def agregarDuda(self, id_clase, nombre, texto, ahora):
        nombre = Estudiante(nombre).nombre
        self._clase(id_clase)
        cuaderno = self._cuaderno(id_clase, nombre)
        duda = cuaderno.agregarDuda(texto, ahora)
        self._guardarCuaderno(cuaderno)
        return duda

    def editarDuda(self, id_clase, nombre, id_duda, texto, ahora):
        nombre = Estudiante(nombre).nombre
        self._clase(id_clase)
        cuaderno = self._cuaderno(id_clase, nombre)
        duda = cuaderno.editarDuda(id_duda, texto, ahora)
        self._guardarCuaderno(cuaderno)
        return duda

    # ----- respuesta a la pregunta de clase -----
    @staticmethod
    def _nombrePdf(id_clase, nombre, intento):
        base = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
        base = re.sub(r"[^a-z0-9]+", "-", base.casefold()).strip("-") or "estudiante"
        return f"clase{id_clase}_{base}_intento{intento}.pdf"

    def enviarRespuesta(self, id_clase, nombre, titulo, texto, ahora):
        nombre = Estudiante(nombre).nombre
        clase = self._clase(id_clase)
        anterior = self._respuesta(id_clase, nombre)
        nueva = anterior.conEnvio(clase, titulo, texto, ahora)       # valida: sin campos vacíos, un solo intento
        archivo = self._nombrePdf(id_clase, nombre, nueva.intentos)
        try:
            contenido = self._generador_pdf.generar(nueva, clase)
            nueva.archivo_pdf = self._almacen_pdf.guardar(archivo, contenido)
            self._guardarRespuesta(nueva)
            self.registrarEstudiante(nombre)
        except Exception as error:
            self._almacen_pdf.eliminar(archivo)                       # no queda un PDF huérfano ni un envío a medias
            raise ErrorGuardado(MSG_ERROR_GUARDADO) from error
        if anterior.archivo_pdf and anterior.archivo_pdf != archivo:
            self._almacen_pdf.eliminar(anterior.archivo_pdf)          # el nuevo intento reemplaza al anterior
        return {"mensaje": nueva.mensajeConfirmacion(), "estado": nueva.estado.value,
                "puntualidad": nueva.puntualidad.value, "fecha_hora_envio": nueva.fecha_hora_envio.isoformat()}

    def rutaPdf(self, id_clase, nombre):
        self._clase(id_clase)
        respuesta = self._respuesta(id_clase, Estudiante(nombre).nombre)
        ruta = self._almacen_pdf.ruta(respuesta.archivo_pdf) if respuesta.archivo_pdf else None
        if ruta is None:
            raise FileNotFoundError(MSG_PDF_NO_EXISTE)
        return ruta

    # ---------- docente: respuestas, nuevo intento y calificación ----------
    def _nombresConocidos(self, id_clase):
        nombres = {datos["nombre"] for datos in self._repo_estudiantes.listar().values()}
        for datos in self._repo_respuestas.listar().values():
            if datos["id_clase"] == id_clase:
                nombres.add(datos["estudiante"])
        return sorted(nombres, key=str.casefold)

    def listarRespuestas(self, id_clase):
        clase = self._clase(id_clase)
        filas = []
        for nombre in self._nombresConocidos(id_clase):
            respuesta = self._respuesta(id_clase, nombre)
            filas.append({**respuesta.aDiccionario(), "estado_revision": respuesta.estadoVisible()})
        return {"clase": clase.aDiccionario(), "bibliografia": self._bibliografia(clase), "estudiantes": filas}

    def habilitarNuevoIntento(self, id_clase, nombre):
        self._clase(id_clase)
        respuesta = self._respuesta(id_clase, self.registrarEstudiante(nombre))
        respuesta.habilitarNuevoIntento()
        self._guardarRespuesta(respuesta)

    def calificar(self, id_clase, nombre, nota, retroalimentacion, publicar):
        self._clase(id_clase)
        respuesta = self._respuesta(id_clase, Estudiante(nombre).nombre)
        respuesta.calificar(nota, retroalimentacion, publicar, PUNTAJE_RESPUESTA_POR_DEFECTO)
        self._guardarRespuesta(respuesta)