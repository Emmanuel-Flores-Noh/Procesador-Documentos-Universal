import os

import pytest

from pdu import cli
from pdu.nucleo.bloques_codigo import proteger, restaurar
from pdu.nucleo.patrones import es_url_externa
from pdu.nucleo.rutas import resolver_salida


def test_proteger_y_restaurar_ida_y_vuelta():
    texto = "a `x` b\n```py\nprint(1)\n```\nc `y` " * 20
    protegido = proteger(texto, prefijo="P")
    assert "`" not in protegido.texto
    assert restaurar(protegido.texto, protegido.bloques, prefijo="P") == texto


def test_restaurar_no_confunde_indices():
    # El marcador 1 no debe sustituirse dentro del 10.
    bloques = [f"<{i}>" for i in range(12)]
    texto = "".join(f"<!--P_{i}-->" for i in range(12))
    assert restaurar(texto, bloques, prefijo="P") == "".join(bloques)


def test_math_fenced_convertir():
    out = proteger("```math\na+b\n```", prefijo="P", modo_math="convertir")
    assert "$$a+b$$" in out.texto and out.bloques == []


@pytest.mark.parametrize("ruta,esperado", [
    ("https://x.org/a.png", True),
    ("data:image/png;base64,AAA", True),
    ("FILE:///tmp/a.png", True),
    ("img/a.png", False),
])
def test_es_url_externa(ruta, esperado):
    assert es_url_externa(ruta) is esperado


def test_resolver_salida(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert resolver_salida(None, True) == str(tmp_path)
    assert resolver_salida(None, False) == os.path.join(str(tmp_path), "out")
    assert resolver_salida("x", False) == os.path.join(str(tmp_path), "x")


def test_alias_registrados():
    for alias, comando in {"todo": "all", "diagramas": "mermaid", "md": "markdown", "init": "estructura"}.items():
        assert cli.ALIASES[alias] == comando


def test_comando_desconocido_sugiere(capsys):
    assert cli.main(["mermiad"]) == 2
    assert "mermaid" in capsys.readouterr().err


def test_version(capsys):
    assert cli.main(["--version"]) == 0
    assert "pdu" in capsys.readouterr().out


def test_ayuda_no_importa_weasyprint():
    import subprocess
    import sys

    codigo = "import sys; from pdu.cli import main; main(['--help']); print('weasyprint' in sys.modules)"
    r = subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True,
                       cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    assert r.stdout.strip().endswith("False")
