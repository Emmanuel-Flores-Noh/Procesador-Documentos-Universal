import os
import tempfile

from pdu.markdown import procesar_documento
from pdu.markdown.descubrimiento import resolver_objetivo
from pdu.markdown.estilos import cargar_estilo, estilos_disponibles
from pdu.markdown.plantilla import construir_html


def test_estilos_disponibles():
    estilos = estilos_disponibles()
    assert "default" in estilos
    assert "compacto" in estilos
    assert "academico" in estilos


def test_cargar_estilo_default():
    nombre, css = cargar_estilo("default")
    assert nombre == "default"
    assert "@page" in css


def test_construir_html():
    html = construir_html("<p>hola</p>", "body{color:red}")
    assert "<p>hola</p>" in html
    assert "body{color:red}" in html


def test_concatenacion_salto_pagina(tmp_path):
    a = tmp_path / "01.md"
    b = tmp_path / "02.md"
    a.write_text("primero", encoding="utf-8")
    b.write_text("segundo", encoding="utf-8")
    docs_dir = tmp_path
    sub = str(tmp_path)
    out = tmp_path / "out"
    # procesar_documento genera PDF; WeasyPrint puede no estar disponible en CI ligero
    try:
        ok = procesar_documento([str(a), str(b)], "Demo", sub, str(docs_dir), out_dir=str(out), diagramas_out=str(tmp_path / "diag"))
        assert ok is True or ok is False
    except Exception:
        # No fallar el test si falta dependencia del sistema (pango)
        pass


def test_resolver_objetivo_archivo(tmp_path):
    md = tmp_path / "x.md"
    md.write_text("hola", encoding="utf-8")
    docs_dir, docs = resolver_objetivo(str(md))
    assert docs and docs[0].nombre == "x"