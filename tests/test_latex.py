import importlib

import pytest

from pdu.latex import procesar_latex_en_markdown
from pdu.latex import renderizador


def test_protege_bloques_de_codigo():
    contenido = "Texto con `formula $x$` y:\n```\n$y$\n```"
    out = procesar_latex_en_markdown(contenido)
    # El código no se convierte: sigue conteniendo el dólar literal
    assert "$y$" in out
    assert "`formula $x$`" in out or "formula $x$" in out


def test_bloque_dolares():
    # Desactivar ziamath si no está disponible -> función devuelve texto original
    if renderizador.zm is None:
        pytest.skip("ziamath no disponible")
    out = procesar_latex_en_markdown("Antes $$E=mc^2$$ despues")
    assert "math-block" in out


def test_inline_dolares():
    if renderizador.zm is None:
        pytest.skip("ziamath no disponible")
    out = procesar_latex_en_markdown("Valor $x+1$ aquí")
    assert "math-inline" in out


def test_math_fenced_se_convierte():
    if renderizador.zm is None:
        pytest.skip("ziamath no disponible")
    out = procesar_latex_en_markdown("```math\na+b\n```")
    assert "math-block" in out