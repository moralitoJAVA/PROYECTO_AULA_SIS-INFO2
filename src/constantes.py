from calendar import FRIDAY, TUESDAY, WEDNESDAY
from datetime import time
from decimal import Decimal
from enum import Enum


DIAS_DE_CLASE = frozenset({TUESDAY, WEDNESDAY, FRIDAY})


class ESTADOS(Enum):
    PRESENTE = "Presente"
    ATRASO = "Atraso"
    AUSENTE = "Ausente"
    LICENCIA = "Licencia"


MSG_NOMBRE_VACIO = "El nombre del estudiante no puede estar vacío"
MSG_ESTADO_INVALIDO = "El estado de asistencia no es válido"
MSG_YA_REGISTRADA = "La asistencia de esa clase ya fue registrada"
MSG_NO_REGISTRADA = "No existe asistencia registrada para esa clase"
MSG_NO_ES_DIA_DE_CLASE = "La fecha no es un día de clase"
FORMATO_RESUMEN = "{presentes} presentes, {atrasos} atrasos, {ausentes} ausentes"
FORMATO_LICENCIAS = ", {licencias} licencias"
CIEN = Decimal("100")
CENTESIMOS = Decimal("0.01")
MINIMO_ASISTENCIA = Decimal("80")
ESTADOS_QUE_ASISTEN = frozenset({ESTADOS.PRESENTE, ESTADOS.ATRASO})
TABLA_ASISTENCIAS = "asistencias"
MSG_TABLA_INVALIDA = "El nombre de la tabla no es válido"
RUTA_BD = "aula_virtual.db"
MATERIA_POR_DEFECTO = "Sistemas de Información 2"

# ---------------------------------------------------------------
# HU2: Entrega de tareas y consulta de calificaciones
# ---------------------------------------------------------------
HORA_LIMITE = time(6, 45)


class ESTADOS_TAREA(Enum):
    REGISTRADA = "Registrada"
    PENDIENTE = "Pendiente"
    ENTREGADA = "Entregada"
    CALIFICADA = "Calificada"


class TIPOS_TAREA(Enum):
    INDIVIDUAL = "Individual"
    GRUPAL = "Grupal"


MSG_FECHA_PASADA = "La fecha límite debe ser posterior a la fecha y hora actual."
MSG_TITULO_VACIO = "El título de la tarea no puede estar vacío"
MSG_NUMERO_INVALIDO = "El número de la tarea debe ser un entero mayor que cero"
MSG_DIA_NO_HABIL = "La fecha límite debe ser martes, miércoles o viernes a las 06:45"
MSG_SIN_GUIA = "La tarea debe tener un documento de guía adjunto"
CODIGO_MATERIA = "IS-2026"
CODIGO_PARCIAL = "P1"
FORMATO_CODIGO = "[{materia}][{parcial}] Tarea {numero:02d}"
MSG_CRITERIO_VACIO = "El criterio de la rúbrica debe tener nombre"
MSG_PUNTAJE_INVALIDO = "El puntaje del criterio debe ser mayor que cero"
MSG_RUBRICA_VACIA = "La rúbrica debe tener al menos un criterio"
CERO = Decimal("0")
TAMANO_MINIMO_EQUIPO = 2
MSG_TAMANO_EQUIPO = "El tamaño del equipo debe ser un entero mayor o igual a 2"
MSG_SIN_TAMANO = "Las tareas grupales deben definir el tamaño de equipo"
HORAS_AVISO = 24
MSG_FUERA_DE_PLAZO = "La fecha límite de la tarea ya venció"
MSG_SIN_ENTREGA = "Debes adjuntar al menos un archivo o enlace"
FORMATO_CONFIRMACION = "Entrega confirmada el {fecha:%d/%m/%Y} a las {fecha:%H:%M:%S}"
MSG_NOTA_FUERA_DE_RANGO = "La nota debe estar entre 0 y el puntaje máximo de la tarea"
MSG_SOLO_ENTREGADAS = "Solo se puede calificar una tarea entregada"
PORCENTAJE_POR_INCUMPLIMIENTO = Decimal("10")
TOPE = Decimal("30")
FORMATO_MOTIVO = "Incumplieron: {nombres}. Descuento aplicado: {descuento}%"
MSG_INTEGRANTE_VACIO = "El nombre del integrante no puede estar vacío"
MSG_INTEGRANTE_REPETIDO = "El integrante ya está en el equipo"
MSG_NO_ES_INTEGRANTE = "El estudiante no pertenece al equipo"
MSG_SIN_ENTREGA_EQUIPO = "El equipo todavía no entregó"
TABLA_TAREAS = "tareas"
TABLA_ENTREGAS = "entregas"
TABLA_EQUIPOS = "equipos"
TABLA_PENALIZACIONES = "penalizaciones"
TABLA_APUNTES = "apuntes"
MSG_TAREA_NO_EXISTE = "La tarea no existe"
MSG_YA_ENTREGADA = "La tarea ya fue entregada"
MSG_ES_GRUPAL = "Esta tarea es grupal: entrégala por el equipo"
MSG_ES_INDIVIDUAL = "Esta tarea es individual: no se entrega por equipo"
MSG_TAMANO_DEL_EQUIPO = "El equipo debe tener exactamente {tamano} integrantes"
MSG_APUNTE_VACIO = "El apunte no puede estar vacío"
MSG_APUNTE_NO_EXISTE = "El apunte no existe"
ASISTENCIA = "asistencia"
TAREAS = "tareas"
EXAMENES = "examenes"
PROYECTO = "proyecto"
COMPONENTES = (ASISTENCIA, TAREAS, EXAMENES, PROYECTO)
TABLA_PORCENTAJES = "porcentajes"
CLAVE_PORCENTAJES = "pesos"
MSG_COMPONENTE_DESCONOCIDO = "El componente no existe"
TOTAL_PESOS = Decimal("100")
MSG_PESOS_NO_SUMAN_100 = "Los pesos deben sumar 100%"
MSG_PESO_NEGATIVO = "Los pesos no pueden ser negativos"
PESOS_POR_DEFECTO = {ASISTENCIA: Decimal("10"), TAREAS: Decimal("30"), EXAMENES: Decimal("40"), PROYECTO: Decimal("20")}

# ---------------------------------------------------------------
# HU3: Apuntes, lectura y respuesta a pregunta de clase (vista del estudiante)
# ---------------------------------------------------------------
class ESTADOS_RESPUESTA(Enum):
    PENDIENTE = "Pendiente"
    RESPONDIDO = "Respondido"


class PUNTUALIDAD(Enum):
    A_TIEMPO = "A tiempo"
    TARDE = "Tarde"


class VENTANA_CLASE(Enum):
    ANTES_DE_CLASE = "Antes de la clase"
    DENTRO_DEL_PLAZO = "Dentro del plazo"
    PLAZO_VENCIDO = "Plazo vencido"


TABLA_LECTURAS = "lecturas"
TABLA_CLASES_LECTURA = "clases_lectura"
TABLA_APUNTES_LECTURA = "apuntes_lectura"
TABLA_RESPUESTAS_CLASE = "respuestas_clase"
TABLA_ESTUDIANTES_LECTURA = "estudiantes_lectura"
CARPETA_PDF_POR_DEFECTO = "entregas_pdf"
FORMATO_CONFIRMACION_RESPUESTA = "Respuesta enviada el {fecha:%d/%m/%Y} a las {fecha:%H:%M:%S}"
FORMATO_FECHA_HORA_PDF = "{fecha:%d/%m/%Y} {fecha:%H:%M:%S}"
MSG_LECTURA_SIN_TITULO = "El título del texto de la bibliografía no puede estar vacío"
MSG_LECTURA_SIN_RECURSO = "El texto debe tener un archivo o un enlace"
MSG_LECTURA_NO_EXISTE = "El texto de la bibliografía no existe"
MSG_CLASE_SIN_TEMA = "El tema de la clase no puede estar vacío"
MSG_CLASE_SIN_BIBLIOGRAFIA = "La clase debe tener al menos un texto de bibliografía"
MSG_CLASE_CIERRE_INVALIDO = "El plazo de respuesta debe ser posterior al inicio de la clase"
MSG_CLASE_NO_EXISTE = "La clase no existe"
MSG_FECHAS_INVALIDAS = "Debes indicar fecha y hora válidas para la clase y para el plazo de respuesta"
MSG_APUNTE_SIN_LECTURA = "Elige el texto de la bibliografía al que pertenece el apunte"
MSG_LECTURA_FUERA_DE_CLASE = "Ese texto no pertenece a la bibliografía de la clase"
MSG_DUDA_VACIA = "La duda no puede estar vacía"
MSG_DUDA_NO_EXISTE = "La duda no existe"
MSG_FUENTE_SIN_TITULO = "El título de la fuente no puede estar vacío"
MSG_FUENTE_NO_EXISTE = "La fuente no existe"
MSG_APUNTE_DOS_ORIGENES = "El apunte pertenece a un texto de la bibliografía o a una fuente propia, no a ambos"
MSG_CAMPOS_OBLIGATORIOS = "Completa los campos obligatorios: {campos}"
MSG_CLASE_NO_INICIADA = "La pregunta se plantea en clase: aún no puedes responder"
MSG_RESPUESTA_YA_ENVIADA = "Ya enviaste tu respuesta; solo el docente puede habilitar otro intento"
MSG_ERROR_GUARDADO = "No se pudo guardar tu respuesta. No fue enviada; inténtalo de nuevo"
MSG_SOLO_RESPONDIDOS = "Solo se puede calificar una respuesta que ya fue enviada"
MSG_NOTA_RESPUESTA_FUERA_DE_RANGO = "La nota debe estar entre 0 y el puntaje máximo"
MSG_PDF_NO_EXISTE = "Todavía no hay un PDF de respuesta para este estudiante"
PUNTAJE_RESPUESTA_POR_DEFECTO = Decimal("100")