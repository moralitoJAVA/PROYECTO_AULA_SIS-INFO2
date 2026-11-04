from calendar import FRIDAY, TUESDAY, WEDNESDAY
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
