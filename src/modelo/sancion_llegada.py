from datetime import datetime, time

class SancionLlegada:
    def __init__(self):
        # Días de clase permitidos: 0: Lunes, 1: Martes, 2: Miércoles, 3: Jueves, 4: Viernes, 5: Sábado, 6: Domingo
        # Martes (1), Miércoles (2), Viernes (4)
        self.dias_clase = [1, 2, 4] 
        self.hora_inicio = time(6, 45)
        self.hora_fin = time(8, 14)
        self.hora_limite_sin_sancion = time(7, 0)

    def evaluar_ingreso(self, dia_semana: int, hora_ingreso: time) -> str:
        """
        Evalúa la llegada del estudiante según los criterios de aceptación:
        - Si el día no es martes, miércoles o viernes -> "Día sin clases"
        - Si la hora está fuera del rango de 06:45 a 08:14 -> "Fuera de horario"
        - Si llega hasta las 07:00 -> "Puntual"
        - Si llega después de las 07:00 (dentro de la hora de clase) -> "Debe fruta"
        """
        if dia_semana not in self.dias_clase:
            return "Día sin clases"
        
        # Validar que esté dentro del horario de clases (06:45 a 08:14)
        if not (self.hora_inicio <= hora_ingreso <= self.hora_fin):
            return "Fuera de horario"
        
        if hora_ingreso > self.hora_limite_sin_sancion:
            return "Debe fruta"
        
        return "Puntual"