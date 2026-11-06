from decimal import Decimal
 
from src.modelo.calculadora_nota_final import CalculadoraNotaFinal
from src.modelo.porcentaje import Porcentaje
 
PESOS = Porcentaje({"asistencia": 10, "tareas": 30, "examenes": 40, "proyecto": 20})
 
 
class RegistroFalso:
    def __init__(self, porcentaje):
        self.porcentaje = porcentaje
 
    def calcularPorcentaje(self):
        return self.porcentaje
 
 
class HistorialFalso:
    def __init__(self, notas):
        self.notas = notas
 
    def obtenerNotas(self):
        return [{"numero": i, "nota_sobre_100": Decimal(n), "descuento": Decimal("0")} for i, n in enumerate(self.notas, 1)]
 
 
def calculadora(asistencia="90", tareas=("80", "100"), otras=None):
    otras = otras or {"examenes": Decimal("70"), "proyecto": Decimal("60")}
    return CalculadoraNotaFinal(PESOS, HistorialFalso(tareas), RegistroFalso(Decimal(asistencia)), otras)
 
 
def test_obtener_pesos_devuelve_los_configurados():
    assert calculadora().obtenerPesos()["examenes"] == Decimal("40")
 
 
def test_calcula_la_nota_final_con_los_pesos():
    # 90*10% + 90*30% + 70*40% + 60*20% = 9 + 27 + 28 + 12
    assert calculadora().calcular() == Decimal("76.00")
 
 
def test_configurar_pesos_cambia_el_resultado():
    nueva = calculadora()
    nueva.configurarPesos(Porcentaje({"asistencia": 100}))
    assert nueva.calcular() == Decimal("90.00")
class HistorialConDescuento(HistorialFalso):
    def __init__(self, notas, descuento):
        super().__init__(notas)
        self.descuento = Decimal(descuento)
 
    def obtenerNotas(self):
        return [{**n, "descuento": self.descuento} for n in super().obtenerNotas()]
 
 
def test_un_componente_sin_notas_queda_pendiente_y_no_cuenta_como_cero():
    solo_asistencia = CalculadoraNotaFinal(PESOS, HistorialFalso([]), RegistroFalso(Decimal("100")))
    assert solo_asistencia.calcular() == Decimal("10.00")
 
 
def test_si_todos_los_componentes_estan_pendientes_no_hay_nota():
    vacia = CalculadoraNotaFinal(PESOS, HistorialFalso([]), RegistroFalso(None))
    assert vacia.calcular() is None
 
 
def test_la_penalizacion_baja_la_nota_de_tareas():
    # tareas: 100 con 10% de descuento = 90 -> aporta 27 de 30
    con_descuento = CalculadoraNotaFinal(
        PESOS, HistorialConDescuento(["100"], "10"), RegistroFalso(None))
    assert con_descuento.calcular() == Decimal("27.00")
def test_el_desglose_muestra_pendientes_y_la_penalizacion_por_separado():
    calc = CalculadoraNotaFinal(PESOS, HistorialConDescuento(["100"], "10"), RegistroFalso(Decimal("100")))
    desglose = calc.obtenerDesglose()
    assert desglose["parcial"] is True
    assert desglose["componentes"]["examenes"]["pendiente"] is True
    assert desglose["componentes"]["tareas"]["nota"] == Decimal("90.00")
    assert desglose["componentes"]["tareas"]["penalizacion"] == Decimal("10.00")
    assert desglose["componentes"]["asistencia"]["penalizacion"] == Decimal("0.00")
    assert desglose["nota_final"] == Decimal("37.00")
 
 
def test_con_todos_los_componentes_el_desglose_no_es_parcial():
    assert calculadora().obtenerDesglose()["parcial"] is False
 
 
def test_recalcular_toma_la_nota_nueva_cuando_cambia_una_nota():
    registro = RegistroFalso(Decimal("100"))
    calc = CalculadoraNotaFinal(PESOS, HistorialFalso(["100"]), registro, {"examenes": Decimal("100"), "proyecto": Decimal("100")})
    assert calc.recalcular() == Decimal("100.00")
    registro.porcentaje = Decimal("50")
    assert calc.recalcular() == Decimal("95.00")
 
 
def test_recalcular_toma_la_asistencia_nueva():
    registro = RegistroFalso(Decimal("100"))
    calc = CalculadoraNotaFinal(PESOS, HistorialFalso([]), registro)
    registro.porcentaje = Decimal("80")
    assert calc.recalcular() == Decimal("8.00")


