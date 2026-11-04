from calendar import FRIDAY, MONDAY, SATURDAY, SUNDAY, THURSDAY, TUESDAY, WEDNESDAY

from src.constantes import DIAS_DE_CLASE, ESTADOS


def test_los_dias_de_clase_son_martes_miercoles_y_viernes():
    assert DIAS_DE_CLASE == {TUESDAY, WEDNESDAY, FRIDAY}


def test_lunes_jueves_y_fin_de_semana_no_son_dias_de_clase():
    for dia in (MONDAY, THURSDAY, SATURDAY, SUNDAY):
        assert dia not in DIAS_DE_CLASE


def test_los_estados_son_presente_atraso_ausente_y_licencia():
    assert [estado.name for estado in ESTADOS] == ["PRESENTE", "ATRASO", "AUSENTE", "LICENCIA"]
