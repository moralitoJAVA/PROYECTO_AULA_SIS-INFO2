import unittest
from decimal import Decimal

from .ayudas import crearCalculadora, crearServicios, entregarYCalificarGrupal


class PruebaCriterio7PenalizacionGrupal(unittest.TestCase):

    def setUp(self):
        self.tareas, self.asistencia = crearServicios()
      
        entregarYCalificarGrupal(self.tareas, 90, ["Ana", "Eva"])
        self.desglose = crearCalculadora(self.tareas, self.asistencia).obtenerDesglose()
        self.tareasComponente = self.desglose["componentes"]["tareas"]

    def testElHistorialRegistraElDescuentoDeLaTareaGrupal(self):
        self.assertEqual(self.tareas.crearHistorial().obtenerNotas()[0]["descuento"], Decimal("20"))

    def testLaNotaDeTareasIncluyeLaPenalizacion(self):
        self.assertEqual(self.tareasComponente["nota"], Decimal("72.00"))

    def testElDesgloseMuestraLaPenalizacionPorSeparado(self):
        self.assertEqual(self.tareasComponente["penalizacion"], Decimal("18.00"))

    def testLaPenalizacionNoSeMezclaConOtrosComponentes(self):
        self.assertIsNone(self.desglose["componentes"]["examenes"]["penalizacion"])

    def testLaNotaFinalUsaLaNotaPenalizada(self):
        self.assertEqual(self.desglose["nota_final"], Decimal("21.60"))

    def testElDescuentoRespetaElTopeDel30Porciento(self):
        tareas, asistencia = crearServicios()
        entregarYCalificarGrupal(tareas, 100, ["Ana", "Luis", "Eva"])
        nota = crearCalculadora(tareas, asistencia).obtenerDesglose()["componentes"]["tareas"]["nota"]
        self.assertEqual(nota, Decimal("70.00"))


if __name__ == "__main__":
    unittest.main()
