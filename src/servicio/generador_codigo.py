from src.constantes import CODIGO_MATERIA, CODIGO_PARCIAL, FORMATO_CODIGO

class GeneradorCodigo:
    def generar(self, numero_tarea):
        """
        Genera el código de asunto basado en el número de tarea.
        Ejemplo: [IS-2026][P1] Tarea 01
        """
        return FORMATO_CODIGO.format(
            materia=CODIGO_MATERIA,
            parcial=CODIGO_PARCIAL,
            numero=numero_tarea
        )