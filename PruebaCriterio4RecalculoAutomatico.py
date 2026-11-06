"""Criterio 4: si cambia una nota o mi porcentaje de asistencia, la nota final debe recalcularse sola."""
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from Pruebas.PruebasNotaFinal.ayudas import (CLASE_1, CLASE_2, MATERIA, crearCalculadora, crearClienteApi,
                                              crearServicios, entregarYCalificarGrupal,
                                              entregarYCalificarIndividual)


class PruebaCriterio4RecalculoAutomatico(unittest.TestCase):

    def setUp(self):
        self.tareas, self.asistencia = crearServicios()
        self.asistencia.registrarAsistencia(MATERIA, CLASE_1, "Presente")
        entregarYCalificarIndividual(self.tareas, 80)

    def testSeRecalculaAlCambiarUnaNota(self):
        self.assertEqual(crearCalculadora(self.tareas, self.asistencia).calcular(), Decimal("34.00"))
        entregarYCalificarGrupal(self.tareas, 100, [])  # entra una nueva nota: promedio (80 + 100) / 2 = 90
        # asistencia 100*10% + tareas 90*30%
        self.assertEqual(crearCalculadora(self.tareas, self.asistencia).calcular(), Decimal("37.00"))

    def testSeRecalculaAlCambiarElPorcentajeDeAsistencia(self):
        self.asistencia.registrarAsistencia(MATERIA, CLASE_2, "Ausente")  # asistencia pasa de 100% a 50%
        # 50*10% + 80*30%
        self.assertEqual(crearCalculadora(self.tareas, self.asistencia).calcular(), Decimal("29.00"))

    def testElMismoObjetoRecalculaConRecalcular(self):
        calculadora = crearCalculadora(self.tareas, self.asistencia)
        self.assertEqual(calculadora.recalcular(), Decimal("34.00"))
        self.asistencia.registrarAsistencia(MATERIA, CLASE_2, "Ausente")
        calculadora = crearCalculadora(self.tareas, self.asistencia)
        self.assertEqual(calculadora.recalcular(), Decimal("29.00"))
        self.assertEqual(calculadora.ultima_nota, Decimal("29.00"))

    def testLaApiRecalculaSolaSinPasosExtra(self):
        with tempfile.TemporaryDirectory() as carpeta:
            cliente = crearClienteApi(str(Path(carpeta) / "prueba.db"))
            cliente.post("/api/asistencia", json={"materia": MATERIA, "fecha": CLASE_1.isoformat(), "estado": "Presente"})
            cliente.post("/api/tareas/1/entrega", json={"archivos": ["t.zip"]})
            cliente.post("/api/tareas/1/calificacion", json={"nota": "80", "escala": "0-100"})
            self.assertEqual(cliente.get("/api/nota-final").get_json()["nota_final"], "34.00")
            cliente.post("/api/asistencia", json={"materia": MATERIA, "fecha": CLASE_2.isoformat(), "estado": "Ausente"})
            self.assertEqual(cliente.get("/api/nota-final").get_json()["nota_final"], "29.00")


if __name__ == "__main__":
    unittest.main()
