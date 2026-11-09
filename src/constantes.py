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
# HU4: Revisión de tareas en clase
# ---------------------------------------------------------------
class ESTADOS_REVISION(Enum):
    PENDIENTE = "Pendiente"
    NO_REVISADA = "No revisada"
    PENDIENTE_DE_REVISION = "Pendiente de revisión"
    REVISADA = "Revisada"
    REENTREGA = "Reentrega"


PUNTUAL = "Puntual"
PUNTUALIDAD_TARDIA = "Tardío"
PUNTUALIDAD_AUSENTE = "Ausente"
PUNTUALIDAD_LICENCIA = "Licencia"
PUNTUALIDAD_SIN_REGISTRO = "Sin registrar"
MOTIVO_ENTREGA_TARDIA = "entrega tardía"
MOTIVO_LLEGADA_TARDIA = "llegada tardía"
MOTIVO_INASISTENCIA = "inasistencia a clase"
SEPARADOR_MOTIVOS = " y "
FORMATO_NO_REVISADA = "No revisada: {motivos}"
EXTENSION_PDF = ".pdf"
TABLA_REVISIONES = "revisiones"
MAX_OBSERVACIONES = 1000
MSG_REENTREGA_SIN_PRESENCIA = "Reentrega no habilitada: no tienes asistencia registrada como presente en esa clase"
MSG_REENTREGA_SIN_ERRORES = "Reentrega no habilitada: la tarea no fue revisada con errores"
MSG_REENTREGA_NO_HABILITADA = "La reentrega no está habilitada para esta tarea"
MSG_SOLO_PDF = "La reentrega debe ser un archivo PDF"
MSG_REENTREGA_SIN_ARCHIVO = "Debes adjuntar un archivo PDF para la reentrega"
MSG_NO_SE_PUEDE_REVISAR = "La tarea no se puede revisar: debe estar entregada a tiempo y con llegada puntual registrada"
MSG_CON_ERRORES_INVALIDO = "El campo con_errores debe ser verdadero o falso"
MSG_OBSERVACIONES_INVALIDAS = "Las observaciones deben ser texto de hasta 1000 caracteres"
MSG_OBSERVACIONES_OBLIGATORIAS = "Debes escribir observaciones cuando la tarea tiene errores"
MSG_REENTREGA_REGISTRADA = "Reentrega registrada: tu tarea quedó pendiente de revisión"
MSG_REENTREGA_FUERA_DE_PLAZO = "Reentrega no habilitada: el plazo terminó en la siguiente clase, donde se revisa de nuevo"

