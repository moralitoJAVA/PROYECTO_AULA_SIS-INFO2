from src.modelo.generador_codigo import GeneradorCodigo


def test_el_codigo_tiene_el_formato_pedido():
    assert GeneradorCodigo().generar(1) == "[IS-2026][P1] Tarea 01"


def test_numeros_de_dos_digitos_no_se_rellenan():
    assert GeneradorCodigo().generar(12) == "[IS-2026][P1] Tarea 12"


def test_el_numero_aumenta_en_cada_tarea():
    generador = GeneradorCodigo()
    assert [generador.siguienteNumero() for _ in range(3)] == [1, 2, 3]


def test_continua_desde_el_ultimo_numero_guardado():
    assert GeneradorCodigo(ultimo_numero=4).siguienteNumero() == 5