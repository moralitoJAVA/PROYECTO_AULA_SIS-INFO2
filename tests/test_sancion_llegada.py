from datetime import time
from src.modelo.sancion_llegada import SancionLlegada

def test_ingreso_puntual():
    sancionador = SancionLlegada()
    # Martes (1), ingresa a las 06:50 (antes de las 07:00)
    resultado = sancionador.evaluar_ingreso(1, time(6, 50))
    assert resultado == "Puntual"

def test_ingreso_tarde_debe_fruta():
    sancionador = SancionLlegada()
    # Martes (1), ingresa a las 07:05 (después de las 07:00)
    resultado = sancionador.evaluar_ingreso(1, time(7, 5))
    assert resultado == "Debe fruta"

def test_dia_sin_clases():
    sancionador = SancionLlegada()
    # Lunes (0) que no es día de clase
    resultado = sancionador.evaluar_ingreso(0, time(7, 0))
    assert resultado == "Día sin clases"