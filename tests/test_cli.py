import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def test_help_diagramas():
    r = subprocess.run([PYTHON, "-m", "pdu", "diagramas", "--help"], capture_output=True, text=True, cwd=str(ROOT))
    assert r.returncode == 0, r.stderr


def test_help_latex():
    r = subprocess.run([PYTHON, "-m", "pdu", "latex", "--help"], capture_output=True, text=True, cwd=str(ROOT))
    assert r.returncode == 0, r.stderr


def test_help_markdown():
    r = subprocess.run([PYTHON, "-m", "pdu", "markdown", "--help"], capture_output=True, text=True, cwd=str(ROOT))
    assert r.returncode == 0, r.stderr


def test_help_unificado():
    env = dict(os.environ)
    r = subprocess.run([PYTHON, "-m", "pdu", "--help"], capture_output=True, text=True, cwd=str(ROOT), env=env)
    assert r.returncode == 0, r.stderr


def test_help_entrypoint():
    # Si pdu está instalado como console script, también debe responder.
    r = subprocess.run(["pdu", "--help"], capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0:
        # Fallback cuando el script no está en PATH del entorno de test.
        r = subprocess.run([PYTHON, "-m", "pdu", "--help"], capture_output=True, text=True, cwd=str(ROOT))
    assert r.returncode == 0, r.stderr


def test_help_subcomandos_muestran_opciones_reales():
    # Antes `pdu all --help` solo mostraba un argumento genérico "args".
    for comando, opcion in (("all", "--estilo"), ("mermaid", "--forzar"), ("latex", "--expr"),
                            ("markdown", "--listar-estilos"), ("estructura", "--no-confirmation")):
        r = subprocess.run([PYTHON, "-m", "pdu", comando, "--help"], capture_output=True, text=True, cwd=str(ROOT))
        assert r.returncode == 0, r.stderr
        assert opcion in r.stdout
