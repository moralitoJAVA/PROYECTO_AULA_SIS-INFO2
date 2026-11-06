import unittest
from decimal import Decimal

from .ayudas import (crearCalculadora, crearServicios, entregarYCalificarGrupal,
                                              entregarYCalificarIndividual)


class PruebaCriterio8DesgloseDesdeHistorial(unittest.TestCase):

    def setUp(self):
        self.tareas, self.asistencia = crearServicios()

    def tareasDelDesglose(self):
        return crearCalculadora(self.tareas, self.asistencia).obtenerDesglose()["componentes"]["tareas"]

    def testSinTareasCalificadasElComponenteEstaPendiente(self):
        self.assertTrue(self.tareasDelDesglose()["pendiente"])

    def testUsaUnaTareaIndividualDelHistorial(self):
        entregarYCalificarIndividual(self.tareas, 80)
        self.assertEqual(self.tareasDelDesglose()["nota"], Decimal("80.00"))

    def testUsaUnaTareaGrupalDelHistorial(self):
        entregarYCalificarGrupal(self.tareas, 90, [])
        self.assertEqual(self.tareasDelDesglose()["nota"], Decimal("90.00"))

    def testPromediaIndividualesYGrupalesConLaPenalizacion(self):
        entregarYCalificarIndividual(self.tareas, 80)
        entregarYCalificarGrupal(self.tareas, 90, ["Ana", "Eva"])
        self.assertEqual(self.tareasDelDesglose()["nota"], Decimal("76.00"))

    def testLasTareasSinCalificarNoEntranAlPromedio(self):
        entregarYCalificarIndividual(self.tareas, 80)
        self.assertEqual(self.tareasDelDesglose()["nota"], Decimal("80.00"))

    def testUnaNuevaTareaCalificadaActualizaElDesglose(self):
        entregarYCalificarIndividual(self.tareas, 80)
        self.assertEqual(self.tareasDelDesglose()["nota"], Decimal("80.00"))
        entregarYCalificarGrupal(self.tareas, 100, [])
        self.assertEqual(self.tareasDelDesglose()["nota"], Decimal("90.00"))


if __name__ == "__main__":
    unittest.main()
