from pdu.nucleo.filtros import FiltroFuncion, Tuberia


def test_orden_y_transformacion():
    tuberia = Tuberia("t", [FiltroFuncion("a", lambda x: x + 1), FiltroFuncion("b", lambda x: x * 2)])
    assert tuberia.ejecutar(3) == 8


def test_error_se_propaga():
    def boom(x):
        raise ValueError("fallo")
    tuberia = Tuberia("t", [FiltroFuncion("boom", boom)])
    try:
        tuberia.ejecutar(1)
    except Exception as e:
        assert "boom" in str(e)
    else:
        raise AssertionError("se esperaba excepción")