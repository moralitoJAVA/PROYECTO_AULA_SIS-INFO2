from src.constantes import TIPOS_TAREA
from src.modelo.tarea import Tarea


class TareaIndividual(Tarea):
    def __init__(self, numero, titulo, instrucciones, fecha_limite, **otros):
        super().__init__(numero, titulo, instrucciones, fecha_limite, TIPOS_TAREA.INDIVIDUAL, **otros)

    def asignarATodos(self, estudiantes):
        return list(estudiantes)