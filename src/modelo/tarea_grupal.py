from src.constantes import MSG_SIN_TAMANO, MSG_TAMANO_EQUIPO, TAMANO_MINIMO_EQUIPO, TIPOS_TAREA
from src.modelo.tarea import Tarea


class TareaGrupal(Tarea):
    def __init__(self, numero, titulo, instrucciones, fecha_limite,
                 tamano_equipo=None, penalizacion=None, **otros):
        super().__init__(numero, titulo, instrucciones, fecha_limite, TIPOS_TAREA.GRUPAL, **otros)
        self.tamano_equipo = None
        self.penalizacion = penalizacion
        if tamano_equipo is not None:
            self.definirTamano(tamano_equipo)

    def definirTamano(self, tamano):
        if not isinstance(tamano, int) or isinstance(tamano, bool) or tamano < TAMANO_MINIMO_EQUIPO:
            raise ValueError(MSG_TAMANO_EQUIPO)
        self.tamano_equipo = tamano

    def definirPenalizacion(self, penalizacion):
        self.penalizacion = penalizacion

    def registrar(self, ahora):
        # Validación del tamaño
        if self.tamano_equipo is None:
            raise ValueError(MSG_SIN_TAMANO)
            
        super().registrar(ahora)

    def aDiccionario(self):
        datos = super().aDiccionario()
        datos["tamano_equipo"] = self.tamano_equipo
        # NUEVO: Guardar la penalización en el diccionario
        datos["penalizacion"] = self.penalizacion 
        return datos

    @classmethod
    def desdeDiccionario(cls, datos):
        tarea = super().desdeDiccionario(datos)
        if datos.get("tamano_equipo") is not None:
            tarea.definirTamano(datos["tamano_equipo"])
        # NUEVO: Recuperar la penalización desde el diccionario
        if datos.get("penalizacion") is not None:
            tarea.definirPenalizacion(datos["penalizacion"])
        return tarea
