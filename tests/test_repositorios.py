import sqlite3

import pytest

from src.constantes import MSG_TABLA_INVALIDA
from src.repositorio.repositorio_memoria import RepositorioMemoria
from src.repositorio.repositorio_sqlite import RepositorioSqlite


@pytest.fixture(params=["memoria", "sqlite"])
def repositorio(request):
    if request.param == "memoria":
        return RepositorioMemoria()
    return RepositorioSqlite(sqlite3.connect(":memory:"), "pruebas")


def test_guardar_y_obtener(repositorio):
    repositorio.guardar(1, {"a": 1})
    assert repositorio.obtener(1) == {"a": 1}


def test_obtener_una_clave_inexistente_devuelve_none(repositorio):
    assert repositorio.obtener("no existe") is None


def test_guardar_dos_veces_reemplaza(repositorio):
    repositorio.guardar("k", {"a": 1})
    repositorio.guardar("k", {"a": 2})
    assert repositorio.listar() == {"k": {"a": 2}}


def test_eliminar(repositorio):
    repositorio.guardar("k", {"a": 1})
    repositorio.eliminar("k")
    assert repositorio.listar() == {}


def test_nombre_de_tabla_invalido_falla():
    with pytest.raises(ValueError) as error:
        RepositorioSqlite(sqlite3.connect(":memory:"), "x; DROP TABLE y")
    assert str(error.value) == MSG_TABLA_INVALIDA
