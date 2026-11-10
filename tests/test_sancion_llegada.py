import unittest
from datetime import time
from src.modelo.sancion_llegada import SancionLlegada

class PruebaCriterio1DiasYHorarios(unittest.TestCase):
    """Criterio 1. Las clases son martes, miércoles y viernes, de 06:45 a 08:14."""
    
    def test_dia_valido_es_reconocido(self):
        sancion = SancionLlegada()
        resultado = sancion.evaluar_ingreso(dia_semana=1, hora_ingreso=time(7, 0))
        self.assertNotEqual(resultado, "Día sin clases")

    def test_dia_no_valido_devuelve_sin_clases(self):
        sancion = SancionLlegada()
        resultado = sancion.evaluar_ingreso(dia_semana=0, hora_ingreso=time(6, 50))
        self.assertEqual(resultado, "Día sin clases")


class PruebaCriterio2IngresoPuntual(unittest.TestCase):
    """Criterio 2. Ingresar hasta las 07:00 = puntual, sin sanción."""
    
    def test_ingresar_antes_de_las_7_es_puntual(self):
        sancion = SancionLlegada()
        resultado = sancion.evaluar_ingreso(dia_semana=2, hora_ingreso=time(6, 45))
        self.assertEqual(resultado, "Puntual")

    def test_ingresar_exactamente_a_las_7_es_puntual(self):
        sancion = SancionLlegada()
        resultado = sancion.evaluar_ingreso(dia_semana=4, hora_ingreso=time(7, 0))
        self.assertEqual(resultado, "Puntual")


class PruebaCriterio3SancionFruta(unittest.TestCase):
    """Criterio 3. Ingresar después de las 07:00 genera 'Debe fruta' para la próxima clase."""
    
    def test_ingresar_tardio_genera_debe_fruta(self):
        sancion = SancionLlegada()
        resultado = sancion.evaluar_ingreso(dia_semana=1, hora_ingreso=time(7, 15))
        self.assertEqual(resultado, "Debe fruta")


class PruebaCriterio4EstadoParaHu4(unittest.TestCase):
    """Criterio 4. Este estado de puntualidad lo usa la HU 4."""
    
    def test_estado_generado_es_valido_para_tareas(self):
        sancion = SancionLlegada()
        resultado = sancion.evaluar_ingreso(dia_semana=1, hora_ingreso=time(7, 5))
        self.assertIn(resultado, ["Puntual", "Debe fruta", "Día sin clases"])


if __name__ == "__main__":
    unittest.main()