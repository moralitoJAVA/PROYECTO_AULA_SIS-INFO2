import unittest
from decimal import Decimal

from src.constantes import COMPONENTES
from .ayudas import (CLASE_1, MATERIA, crearCalculadora, crearServicios,
                                              entregarYCalificarIndividual)

OTRAS = {"examenes": Decimal("70"), "proyecto": Decimal("60")}


class PruebaCriterio5DesglosePorComponente(unittest.TestCase):

    def setUp(self):
        tareas, asistencia = crearServicios()
        asistencia.registrarAsistencia(MATERIA, CLASE_1, "Presente")
        entregarYCalificarIndividual(tareas, 80)
        self.desglose = crearCalculadora(tareas, asistencia, otras=OTRAS).obtenerDesglose()

    def testMuestraLosCuatroComponentes(self):
        self.assertEqual(set(self.desglose["componentes"]), set(COMPONENTES))

    def testCadaComponenteMuestraPesoNotaYAporte(self):
        for dato in self.desglose["componentes"].values():
            self.assertTrue({"peso", "nota", "aporte"} <= set(dato))

    def testMuestraLosAportesPorComponente(self):
        aportes = {nombre: dato["aporte"] for nombre, dato in self.desglose["componentes"].items()}
        self.assertEqual(aportes, {"asistencia": Decimal("10.00"), "tareas": Decimal("24.00"),
                                   "examenes": Decimal("28.00"), "proyecto": Decimal("12.00")})

    def testMuestraLaNotaFinal(self):
        self.assertEqual(self.desglose["nota_final"], Decimal("74.00"))

    def testLaNotaFinalEsLaSumaDeLosAportes(self):
        suma = sum(dato["aporte"] for dato in self.desglose["componentes"].values())
        self.assertEqual(self.desglose["nota_final"], suma)


if __name__ == "__main__":
    unittest.main()
