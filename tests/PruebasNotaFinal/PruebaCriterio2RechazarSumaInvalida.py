import tempfile
import unittest
from pathlib import Path

from src.modelo.porcentaje import Porcentaje
from src.repositorio.repositorio_memoria import RepositorioMemoria
from .ayudas import crearClienteApi

MENSAJE = "Los pesos deben sumar 100%"


class PruebaCriterio2RechazarSumaInvalida(unittest.TestCase):

    def testRechazaPesosQueSumanMasDe100(self):
        porcentaje = Porcentaje({"asistencia": 20, "tareas": 30, "examenes": 40, "proyecto": 20})
        with self.assertRaises(ValueError) as error:
            porcentaje.validarSuma()
        self.assertEqual(str(error.exception), MENSAJE)

    def testRechazaPesosQueSumanMenosDe100(self):
        porcentaje = Porcentaje({"asistencia": 10, "tareas": 30, "examenes": 40, "proyecto": 10})
        with self.assertRaises(ValueError) as error:
            porcentaje.validarSuma()
        self.assertEqual(str(error.exception), MENSAJE)

    def testGuardarConSumaInvalidaNoPersisteNada(self):
        repositorio = RepositorioMemoria()
        with self.assertRaises(ValueError):
            Porcentaje({"asistencia": 50}).guardar(repositorio)
        self.assertIsNone(repositorio.obtener("pesos"))

    def testLaApiRespondeError400ConElMensajeExacto(self):
        with tempfile.TemporaryDirectory() as carpeta:
            cliente = crearClienteApi(str(Path(carpeta) / "prueba.db"))
            respuesta = cliente.put("/api/pesos", json={"asistencia": 50})
            self.assertEqual(respuesta.status_code, 400)
            self.assertEqual(respuesta.get_json(), {"error": MENSAJE})

    def testTrasElRechazoLosPesosGuardadosNoCambian(self):
        with tempfile.TemporaryDirectory() as carpeta:
            cliente = crearClienteApi(str(Path(carpeta) / "prueba.db"))
            cliente.put("/api/pesos", json={"asistencia": 90, "tareas": 90})
            self.assertEqual(cliente.get("/api/pesos").get_json(),
                             {"asistencia": "10", "tareas": "30", "examenes": "40", "proyecto": "20"})


if __name__ == "__main__":
    unittest.main()
