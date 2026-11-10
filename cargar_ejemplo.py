"""Simula el docente y otros estudiantes: bibliografía enviada, dudas, respuestas, calificaciones y un nuevo intento.

El docente no usa este sistema, así que sus acciones se cargan directo en la base de datos.
Uso (desde la carpeta del proyecto, con el servidor apagado o encendido):
    python cargar_ejemplo.py
Para empezar de cero, borra el archivo aula_virtual.db y la carpeta entregas_pdf, y vuelve a ejecutarlo.
"""
from datetime import datetime, timedelta

from src.api.contexto import Contexto
from src.constantes import RUTA_BD
from src.servicio.servicio_apuntes_lectura import ServicioApuntesLectura

FORMATO = "%Y-%m-%dT%H:%M"


def main():
    ahora = datetime.now()
    servicio = ServicioApuntesLectura.desdeContexto(Contexto(RUTA_BD))

    if any(c["tema"].startswith("Clase 1: Proceso Unificado") for c in servicio.listarClases("Edwin Morales Alvis", ahora)):
        print("Los datos de ejemplo ya estaban cargados. No se repitió nada.")
        return

    # ---------- El docente "envía" la bibliografía (archivos en web/lecturas/) ----------
    def lectura(titulo, autor, archivo):
        return servicio.registrarLectura({"titulo": titulo, "autor": autor, "archivo": archivo})["id"]

    libro = lectura("El Proceso Unificado de Desarrollo de Software",
                    "Ivar Jacobson, Grady Booch y James Rumbaugh", "/lecturas/proceso_unificado_jacobson.pdf")
    aup = lectura("Agile Unified Process (AUP)", "Scott W. Ambler", "/lecturas/AgileUP.pdf")
    openup = lectura("OpenUP", None, "/lecturas/OpenUP.pdf")
    refs = lectura("Referencias de AUP", None, "/lecturas/referencias_AUP.docx")
    essup = lectura("EssUP: folleto", None, "/lecturas/EssUP_Brochure.pdf")
    paper = lectura("EssUP: una primera mirada (paper)", None, "/lecturas/paper_essup_first_look.pdf")

    # ---------- El docente "publica" tres clases ----------
    def clase(tema, inicio, cierre, lecturas):
        return servicio.publicarClase({"tema": tema, "inicio": inicio.strftime(FORMATO),
                                       "cierre_respuesta": cierre.strftime(FORMATO), "ids_lecturas": lecturas})["id"]

    c1_inicio = ahora - timedelta(days=7)
    c2_inicio = ahora - timedelta(days=3)
    c1 = clase("Clase 1: Proceso Unificado (UP)", c1_inicio, c1_inicio + timedelta(days=3), [libro])
    c2 = clase("Clase 2: Variantes del UP (AUP y OpenUP)", c2_inicio, c2_inicio + timedelta(days=2), [aup, openup, refs])
    c3 = clase("Clase 3: Essential Unified Process (EssUP)", ahora - timedelta(hours=1), ahora + timedelta(days=3), [essup, paper])

    # ---------- Estudiantes ----------
    def apunte(id_clase, nombre, id_lectura, texto, cuando):
        servicio.agregarApunte(id_clase, nombre, id_lectura, texto, cuando)

    def duda(id_clase, nombre, texto, cuando):
        servicio.agregarDuda(id_clase, nombre, texto, cuando)

    def responder(id_clase, nombre, titulo, texto, cuando):
        servicio.registrarEstudiante(nombre)
        servicio.enviarRespuesta(id_clase, nombre, titulo, texto, cuando)

    def calificar(id_clase, nombre, nota, comentario):
        servicio.calificar(id_clase, nombre, nota, comentario, True)

    # Edwin (tú): clase 1 respondida A TIEMPO y calificada; clase 2 respondida TARDE y calificada;
    # clase 3 en curso: ya tiene apuntes y dudas, y todavía puede responder.
    edwin = "Edwin Morales Alvis"
    servicio.registrarEstudiante(edwin)
    apunte(c1, edwin, libro, "El UP es iterativo e incremental, dirigido por casos de uso y centrado en la arquitectura.", c1_inicio - timedelta(hours=20))
    apunte(c1, edwin, libro, "Las 4 fases: inicio, elaboración, construcción y transición. Cada una termina en un hito.", c1_inicio - timedelta(hours=18))
    duda(c1, edwin, "¿Cuál es la diferencia entre una iteración y una fase?", c1_inicio - timedelta(hours=17))
    duda(c1, edwin, "¿Cuándo queda lista la línea base de la arquitectura?", c1_inicio - timedelta(hours=16))
    responder(c1, edwin, "Las fases del Proceso Unificado",
              "El UP se organiza en cuatro fases: inicio, elaboración, construcción y transición. Cada fase se divide en "
              "iteraciones y termina en un hito. Como dice el libro, la arquitectura se establece durante la elaboración.",
              c1_inicio + timedelta(hours=3))
    calificar(c1, edwin, 85, "Buena respuesta y basada en la lectura. Te faltó mencionar los hitos de cada fase.")

    apunte(c2, edwin, aup, "AUP simplifica el RUP a 7 disciplinas y adopta prácticas ágiles.", c2_inicio - timedelta(hours=10))
    apunte(c2, edwin, openup, "OpenUP es un proceso mínimo, completo y extensible, de código abierto.", c2_inicio - timedelta(hours=9))
    duda(c2, edwin, "¿Cuándo conviene usar AUP en lugar de OpenUP?", c2_inicio - timedelta(hours=8))
    responder(c2, edwin, "Diferencia entre AUP y OpenUP",
              "AUP es una versión simplificada y ágil del RUP, mientras que OpenUP es un proceso mínimo y extensible. "
              "Los dos mantienen un ciclo iterativo e incremental.",
              c2_inicio + timedelta(days=2, hours=2))             # pasó el plazo: queda "Tarde"
    calificar(c2, edwin, 70, "Correcto, pero llegó fuera de plazo. Cita mejor el documento de OpenUP.")

    apunte(c3, edwin, essup, "EssUP combina prácticas del UP, ágiles y de otros procesos en un solo marco.", ahora - timedelta(hours=5))
    apunte(c3, edwin, paper, "El paper presenta EssUP como una primera mirada a un proceso esencial y reutilizable.", ahora - timedelta(hours=4))
    duda(c3, edwin, "¿Qué significa que EssUP sea un proceso 'esencial'?", ahora - timedelta(hours=3))

    # Otros estudiantes, en distintos estados.
    ana = "Ana Pérez"       # respondió la clase 1, todavía sin calificación publicada
    servicio.registrarEstudiante(ana)
    apunte(c1, ana, libro, "El UP está dirigido por casos de uso.", c1_inicio - timedelta(hours=12))
    responder(c1, ana, "Las 4 fases del UP", "Inicio, elaboración, construcción y transición.", c1_inicio + timedelta(hours=5))

    luis = "Luis Mamani"    # solo anotó dudas, no ha respondido
    servicio.registrarEstudiante(luis)
    duda(c1, luis, "¿El UP sirve para proyectos pequeños?", c1_inicio - timedelta(hours=11))

    carla = "Carla Quispe"  # el docente le habilitó un nuevo intento
    servicio.registrarEstudiante(carla)
    responder(c1, carla, "Casos de uso", "Describen cómo usa el sistema un actor.", c1_inicio + timedelta(hours=6))
    calificar(c1, carla, 40, "Muy corta: desarrolla más y cita el libro.")
    servicio.habilitarNuevoIntento(c1, carla)

    print("Listo: 6 lecturas, 3 clases y 4 estudiantes (Edwin, Ana, Luis y Carla) cargados.")


main()