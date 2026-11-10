"""Carga datos de ejemplo para las demás historias de usuario: asistencia, tareas, envío de tareas al correo y nota final.

Las clases y lecturas (HU-03 y HU-04) las carga cargar_ejemplo.py; este script las llama primero, así que con uno solo
se llena todo. Uso (desde la carpeta del proyecto, con el entorno virtual activo):
    python cargar_ejemplo_completo.py
Cada bloque se salta solo si ya tiene datos, así que se puede ejecutar varias veces sin duplicar nada.
Para empezar de cero, borra el archivo aula_virtual.db y la carpeta entregas_pdf, y vuelve a ejecutarlo.
"""
import base64
from datetime import datetime, timedelta

from src.api.contexto import Contexto
from src.constantes import (
    DIAS_DE_CLASE,
    ESTADOS,
    HORA_LIMITE,
    MATERIA_POR_DEFECTO,
    RUTA_BD,
    TABLA_APUNTES,
    TABLA_ASISTENCIAS,
    TABLA_ENVIOS_TAREA,
    TABLA_MATERIAS,
)
from src.modelo.gestor_apuntes import GestorApuntes
from src.servicio.servicio_asistencia import ServicioAsistencia
from src.servicio.servicio_envio_tareas import ServicioEnvioTareas
from src.servicio.servicio_tareas import ServicioTareas

import cargar_ejemplo  # noqa: F401  (al importarlo carga HU-03 y HU-04)

EDWIN = "Edwin Morales Alvis"
ANA = "Ana Pérez"
LUIS = "Luis Mamani"
CORREO_DOCENTE = "docente.ejemplo@umss.edu.bo"


# ---------- fechas: asistencia y tareas solo aceptan martes, miércoles y viernes (tareas, a las 06:45) ----------
def esDiaDeClase(dia):
    return dia.weekday() in DIAS_DE_CLASE


def diasDeClaseAtras(ahora, cantidad):
    dias, dia = [], ahora.date() - timedelta(days=1)
    while len(dias) < cantidad:
        if esDiaDeClase(dia):
            dias.append(dia)
        dia -= timedelta(days=1)
    return sorted(dias)


def limiteAnterior(ahora, minimo_dias):
    dia = (ahora - timedelta(days=minimo_dias)).date()
    while not esDiaDeClase(dia):
        dia -= timedelta(days=1)
    return datetime.combine(dia, HORA_LIMITE)


def limiteProximo(ahora, minimo_dias):
    dia = (ahora + timedelta(days=minimo_dias)).date()
    while not esDiaDeClase(dia):
        dia += timedelta(days=1)
    return datetime.combine(dia, HORA_LIMITE)


# ---------- HU-01: asistencia ----------
def cargarAsistencia(contexto, ahora):
    servicio = ServicioAsistencia(contexto.repositorio(TABLA_ASISTENCIAS))
    if servicio.obtenerHistorial(MATERIA_POR_DEFECTO):
        print("Asistencia: ya tenía registros. No se repitió nada.")
        return
    estados = [ESTADOS.PRESENTE, ESTADOS.PRESENTE, ESTADOS.PRESENTE, ESTADOS.ATRASO, ESTADOS.PRESENTE,
               ESTADOS.PRESENTE, ESTADOS.AUSENTE, ESTADOS.PRESENTE, ESTADOS.LICENCIA, ESTADOS.PRESENTE]
    for dia, estado in zip(diasDeClaseAtras(ahora, len(estados)), estados):
        servicio.registrarAsistencia(MATERIA_POR_DEFECTO, dia, estado.value)
    print(f"Asistencia: {len(estados)} clases registradas en '{MATERIA_POR_DEFECTO}'.")


# ---------- HU-02: tareas (registro, entrega, calificación, equipos, apuntes) ----------
def cargarTareas(contexto, ahora):
    servicio = ServicioTareas.desdeContexto(contexto)
    if servicio.obtenerHistorial():
        print("Tareas: ya había tareas. No se repitió nada.")
        return
    apuntes = GestorApuntes(contexto.repositorio(TABLA_APUNTES))

    def registrar(datos, momento):
        tarea = servicio.crearTarea(datos)
        return servicio.registrarTarea(tarea, momento)["numero"]

    # Tarea 1: individual, ya venció, entregada a tiempo y calificada.
    limite1 = limiteAnterior(ahora, 14)
    t1 = registrar({"titulo": "Informe de requisitos", "tipo": "Individual", "fecha_limite": limite1.isoformat(),
                    "instrucciones": "Redacta el informe de requisitos del sistema del aula virtual.",
                    "ruta_adjunto": "/guias/guia_tarea_01.pdf",
                    "criterios": [{"nombre": "Contenido", "puntaje": 60}, {"nombre": "Presentación", "puntaje": 25},
                                  {"nombre": "Ortografía", "puntaje": 15}]}, limite1 - timedelta(days=7))
    servicio.entregar(t1, ["informe_requisitos.pdf"], [], limite1 - timedelta(hours=10))
    servicio.registrarCalificacion(t1, 85, "sobre 100", "Buen informe. Faltó detallar los requisitos no funcionales.")
    apuntes.crear(f"tarea-{t1}", "Revisar la plantilla de requisitos antes de entregar.")

    # Tarea 2: grupal de 3, ya venció y fue calificada. El descuento (10% por incumplimiento) solo se aplica a quien aparece
    # en la lista de incumplen; Edwin está ahí para que la penalización se vea en su nota final. Quítalo de la lista para no verla.
    limite2 = limiteAnterior(ahora, 8)
    t2 = registrar({"titulo": "Diagrama de clases del equipo", "tipo": "Grupal", "tamano_equipo": 3,
                    "fecha_limite": limite2.isoformat(), "instrucciones": "Entreguen el diagrama de clases del módulo de tareas.",
                    "ruta_adjunto": "/guias/guia_tarea_02.pdf",
                    "criterios": [{"nombre": "Diagrama", "puntaje": 70}, {"nombre": "Documentación", "puntaje": 30}]},
                   limite2 - timedelta(days=7))
    servicio.entregarPorEquipo(t2, [EDWIN, ANA, LUIS], EDWIN, [EDWIN], ["diagrama_clases.pdf"], [],
                               limite2 - timedelta(hours=5))
    servicio.registrarCalificacion(t2, 90, "sobre 100", "Diagrama completo. Se descontó 10% porque un integrante no cumplió su parte.")

    # Tarea 3: individual, entregada pero todavía sin calificar.
    limite3 = limiteProximo(ahora, 2)
    t3 = registrar({"titulo": "Casos de uso", "tipo": "Individual", "fecha_limite": limite3.isoformat(),
                    "instrucciones": "Describe los casos de uso principales.", "ruta_adjunto": "/guias/guia_tarea_03.pdf",
                    "criterios": [{"nombre": "Casos de uso", "puntaje": 70}, {"nombre": "Diagrama", "puntaje": 30}]}, ahora)
    servicio.entregar(t3, ["casos_de_uso.pdf"], ["https://github.com/ejemplo/casos-de-uso"], ahora)
    apuntes.crear(f"tarea-{t3}", "Confirmar con el docente si el diagrama va en el mismo PDF.")

    # Tareas 4 y 5: pendientes (una individual y una grupal).
    registrar({"titulo": "Prototipo de interfaz", "tipo": "Individual", "fecha_limite": limiteProximo(ahora, 6).isoformat(),
               "instrucciones": "Diseña el prototipo de la pantalla principal.", "ruta_adjunto": "/guias/guia_tarea_04.pdf",
               "criterios": [{"nombre": "Prototipo", "puntaje": 100}]}, ahora)
    registrar({"titulo": "Proyecto parcial", "tipo": "Grupal", "tamano_equipo": 4,
               "fecha_limite": limiteProximo(ahora, 13).isoformat(), "instrucciones": "Primera entrega del proyecto en equipo.",
               "ruta_adjunto": "/guias/guia_tarea_05.pdf",
               "criterios": [{"nombre": "Funcionamiento", "puntaje": 60}, {"nombre": "Informe", "puntaje": 40}]}, ahora)
    print("Tareas: 5 tareas (2 calificadas, 1 entregada, 2 pendientes) y 2 apuntes cargados.")


# ---------- HU-02: envío de tareas al correo del docente ----------
class EnviadorSimulado:
    """No manda correos de verdad: así el ejemplo funciona sin servidor de correo."""

    def enviar(self, destino, asunto, cuerpo, adjuntos):
        return None


def adjunto(nombre):
    return {"nombre": nombre, "contenido": base64.b64encode(b"Archivo de ejemplo").decode()}


def cargarEnvios(contexto, ahora):
    servicio = ServicioEnvioTareas(contexto.repositorio(TABLA_MATERIAS), contexto.repositorio(TABLA_ENVIOS_TAREA),
                                   EnviadorSimulado())
    try:
        servicio.correoDocente(MATERIA_POR_DEFECTO)
    except ValueError:
        servicio.asignarDocente(MATERIA_POR_DEFECTO, CORREO_DOCENTE)
    try:
        servicio.estadoEnvio(MATERIA_POR_DEFECTO, "Tarea 01", EDWIN)
        print("Envío de tareas: ya había envíos. No se repitió nada.")
        return
    except ValueError:
        pass
    servicio.enviar(MATERIA_POR_DEFECTO, "Tarea 01", EDWIN, "edwin@ejemplo.com", [adjunto("tarea01.pdf")],
                    ahora + timedelta(days=2), ahora)                        # a tiempo
    servicio.enviar(MATERIA_POR_DEFECTO, "Tarea 02", ANA, "ana@ejemplo.com", [adjunto("tarea02.pdf")],
                    ahora - timedelta(days=2), ahora)                        # tarde
    servicio.habilitarReentrega(MATERIA_POR_DEFECTO, "Tarea 02", ANA)        # el docente le permite reenviar
    print(f"Envío de tareas: docente {CORREO_DOCENTE}, 1 envío a tiempo, 1 tarde y 1 reentrega habilitada.")


def main():
    ahora = datetime.now()
    contexto = Contexto(RUTA_BD)
    cargarAsistencia(contexto, ahora)
    cargarTareas(contexto, ahora)
    cargarEnvios(contexto, ahora)
    print("Nota final: se calcula sola con la asistencia y las tareas calificadas (exámenes y proyecto quedan pendientes).")


main()