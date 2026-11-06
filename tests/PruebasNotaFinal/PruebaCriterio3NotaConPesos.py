import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from .ayudas import (CLASE_1, CLASE_2, MATERIA, crearCalculadora, crearClienteApi,
                                              crearServicios, entregarYCalificarIndividual)


class PruebaCriterio3NotaConPesos(unittest.TestCase):

    def setUp(self):
        self.tareas, self.asistencia = crearServicios()
        self.asistencia.registrarAsistencia(MATERIA, CLASE_1, "Presente")
        entregarYCalificarIndividual(self.tareas, 80)

    def testCalculaLaNotaFinalAplicandoLosPesos(self):
      
        self.assertEqual(crearCalculadora(self.tareas, self.asistencia).calcular(), Decimal("34.00"))

    def testIncluyeExamenYProyectoConSusPesos(self):
        calculadora = crearCalculadora(self.tareas, self.asistencia,
                                       otras={"examenes": Decimal("70"), "proyecto": Decimal("60")})
      
        self.assertEqual(calculadora.calcular(), Decimal("74.00"))

    def testCambiarLosPesosCambiaLaNotaFinal(self):
        calculadora = crearCalculadora(self.tareas, self.asistencia,
                                       pesos={"asistencia": 50, "tareas": 50, "examenes": 0, "proyecto": 0})
        self.assertEqual(calculadora.calcular(), Decimal("90.00"))

    def testElPanelDeLaApiMuestraLaNotaFinalCalculada(self):
        with tempfile.TemporaryDirectory() as carpeta:
            cliente = crearClienteApi(str(Path(carpeta) / "prueba.db"))
            cliente.post("/api/asistencia", json={"materia": MATERIA, "fecha": CLASE_1.isoformat(), "estado": "Presente"})
            cliente.post("/api/tareas/1/entrega", json={"archivos": ["t.zip"]})
            cliente.post("/api/tareas/1/calificacion", json={"nota": "80", "escala": "0-100"})
            self.assertEqual(cliente.get("/api/nota-final").get_json()["nota_final"], "34.00")


if __name__ == "__main__":
    unittest.main()
