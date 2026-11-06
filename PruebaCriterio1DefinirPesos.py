
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from src.modelo.porcentaje import Porcentaje
from src.repositorio.repositorio_memoria import RepositorioMemoria
from Pruebas.PruebasNotaFinal.ayudas import PESOS_VALIDOS, crearClienteApi


class PruebaCriterio1DefinirPesos(unittest.TestCase):

    def testAceptaPesos10_30_40_20(self):
        Porcentaje(PESOS_VALIDOS).validarSuma()  # no debe lanzar error

    def testObtienePesoDeCadaComponente(self):
        porcentaje = Porcentaje(PESOS_VALIDOS)
        self.assertEqual(porcentaje.obtenerPeso("asistencia"), Decimal("10"))
        self.assertEqual(porcentaje.obtenerPeso("tareas"), Decimal("30"))
        self.assertEqual(porcentaje.obtenerPeso("examenes"), Decimal("40"))
        self.assertEqual(porcentaje.obtenerPeso("proyecto"), Decimal("20"))

    def testAceptaOtraDistribucionQueSumeExactamente100(self):
        Porcentaje({"asistencia": 20, "tareas": 30, "examenes": 30, "proyecto": 20}).validarSuma()

    def testGuardaLosPesosEnElRepositorio(self):
        repositorio = RepositorioMemoria()
        Porcentaje(PESOS_VALIDOS).guardar(repositorio)
        self.assertEqual(Porcentaje.cargar(repositorio).aDiccionario(),
                         {"asistencia": "10", "tareas": "30", "examenes": "40", "proyecto": "20"})

    def testLaApiGuardaLosPesosValidosYLosConserva(self):
        with tempfile.TemporaryDirectory() as carpeta:
            cliente = crearClienteApi(str(Path(carpeta) / "prueba.db"))
            respuesta = cliente.put("/api/pesos", json={"asistencia": 20, "tareas": 30, "examenes": 30, "proyecto": 20})
            self.assertEqual(respuesta.status_code, 200)
            self.assertEqual(cliente.get("/api/pesos").get_json()["asistencia"], "20")


if __name__ == "__main__":
    unittest.main()
