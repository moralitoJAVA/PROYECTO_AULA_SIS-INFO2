import unittest
from decimal import Decimal

from .ayudas import (CLASE_1, MATERIA, crearCalculadora, crearServicios,
                     entregarYCalificarIndividual)


class PruebaCriterio6ComponentePendiente(unittest.TestCase):

    def setUp(self):
        self.tareas, self.asistencia = crearServicios()

    def testSinNingunaNotaTodosLosComponentesQuedanPendientes(self):
        desglose = crearCalculadora(self.tareas, self.asistencia).obtenerDesglose()
        self.assertTrue(all(dato["pendiente"] for dato in desglose["componentes"].values()))
        self.assertIsNone(desglose["nota_final"])

    def testUnComponenteSinNotasSeMarcaPendienteYSinNota(self):
        self.asistencia.registrarAsistencia(MATERIA, CLASE_1, "Presente")
        tareas = crearCalculadora(self.tareas, self.asistencia).obtenerDesglose()["componentes"]["tareas"]
        self.assertTrue(tareas["pendiente"])
        self.assertIsNone(tareas["nota"])
        self.assertIsNone(tareas["aporte"])

    def testElPendienteNoSeCuentaComoCero(self):
        self.asistencia.registrarAsistencia(MATERIA, CLASE_1, "Presente")
      
        self.assertEqual(crearCalculadora(self.tareas, self.asistencia).calcular(), Decimal("10.00"))

    def testElDesgloseAvisaQueLaNotaEsParcial(self):
        self.asistencia.registrarAsistencia(MATERIA, CLASE_1, "Presente")
        self.assertTrue(crearCalculadora(self.tareas, self.asistencia).obtenerDesglose()["parcial"])

    def testConTodosLosComponentesNoEsParcial(self):
        self.asistencia.registrarAsistencia(MATERIA, CLASE_1, "Presente")
        entregarYCalificarIndividual(self.tareas, 80)
        otras = {"examenes": Decimal("70"), "proyecto": Decimal("60")}
        self.assertFalse(crearCalculadora(self.tareas, self.asistencia, otras=otras).obtenerDesglose()["parcial"])


if __name__ == "__main__":
    unittest.main()
