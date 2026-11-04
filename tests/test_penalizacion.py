from decimal import Decimal

import pytest

from src.modelo.penalizacion import Penalizacion
from src.repositorio.repositorio_memoria import RepositorioMemoria


@pytest.mark.parametrize("incumplen, esperado", [(0, "0"), (1, "10"), (2, "20"), (3, "30"), (4, "30"), (10, "30")])
def test_el_descuento_sube_10_por_integrante_hasta_el_tope(incumplen, esperado):
    assert Penalizacion().calcularDescuento(incumplen) == Decimal(esperado)


def test_aplicar_tope_no_toca_un_valor_menor():
    assert Penalizacion().aplicarTope(Decimal("5")) == Decimal("5")


def test_guarda_el_motivo():
    repositorio = RepositorioMemoria()
    Penalizacion().guardarMotivo(repositorio, 1, ["Ana", "Luis"])
    assert repositorio.obtener(1) == {"motivo": "Incumplieron: Ana, Luis. Descuento aplicado: 20%", "descuento": "20"}


def test_si_nadie_incumple_no_guarda_nada():
    repositorio = RepositorioMemoria()
    Penalizacion().guardarMotivo(repositorio, 1, [])
    assert repositorio.listar() == {}