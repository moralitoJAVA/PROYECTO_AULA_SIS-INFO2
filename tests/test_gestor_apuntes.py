import pytest

from src.constantes import MSG_APUNTE_NO_EXISTE, MSG_APUNTE_VACIO
from src.modelo.gestor_apuntes import GestorApuntes
from src.repositorio.repositorio_memoria import RepositorioMemoria


@pytest.fixture
def gestor():
    return GestorApuntes(RepositorioMemoria())


def test_crear_un_apunte_vinculado(gestor):
    clave = gestor.crear("tarea-1", "Revisar la rúbrica")
    assert gestor.listarApuntes("tarea-1") == [{"clave": clave, "vinculo": "tarea-1", "texto": "Revisar la rúbrica"}]


def test_las_claves_no_se_repiten_aunque_se_borre(gestor):
    gestor.crear("a", "uno")
    segunda = gestor.crear("a", "dos")
    gestor.borrar(segunda)
    assert gestor.crear("a", "tres") == segunda


def test_editar_cambia_el_texto(gestor):
    clave = gestor.crear("a", "uno")
    gestor.editar(clave, "dos")
    assert gestor.listarApuntes()[0]["texto"] == "dos"


def test_borrar_elimina(gestor):
    clave = gestor.crear("a", "uno")
    gestor.borrar(clave)
    assert gestor.listarApuntes() == []


def test_un_apunte_vacio_falla(gestor):
    with pytest.raises(ValueError) as error:
        gestor.crear("a", "  ")
    assert str(error.value) == MSG_APUNTE_VACIO


def test_editar_o_borrar_un_apunte_inexistente_falla(gestor):
    for accion in (lambda: gestor.editar("9", "x"), lambda: gestor.borrar("9")):
        with pytest.raises(ValueError) as error:
            accion()
        assert str(error.value) == MSG_APUNTE_NO_EXISTE


def test_listar_filtra_por_vinculo(gestor):
    gestor.crear("tarea-1", "a")
    gestor.crear("clase-2026-03-03", "b")
    assert [a["texto"] for a in gestor.listarApuntes("clase-2026-03-03")] == ["b"]