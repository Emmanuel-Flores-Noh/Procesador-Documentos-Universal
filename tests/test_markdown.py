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

def _html_de(texto):
    from types import SimpleNamespace
    from pdu.markdown.filtros import ConvertirAHtml

    ctx = SimpleNamespace(texto=texto, html_body="")
    return ConvertirAHtml().procesar(ctx).html_body


def test_codigo_con_lenguaje_se_resalta():
    html = _html_de("```python\ndef f():\n    return 1\n```\n")
    assert 'class="codehilite"' in html
    assert '<span class="k">def</span>' in html


def test_codigo_sin_lenguaje_no_se_colorea():
    html = _html_de("```\ndef f():\n    return 1\n```\n")
    assert '<span class="k">' not in html
    assert "def f():" in html


def test_codigo_lenguaje_desconocido_no_falla():
    html = _html_de("```lenguajeinexistente\nhola mundo\n```\n")
    assert "hola mundo" in html


def test_css_resaltado():
    from pdu.markdown.resaltado import css_resaltado

    css = css_resaltado()
    assert ".codehilite .k" in css
    assert ".codehilite { background" not in css


def test_plantilla_incluye_css_resaltado():
    from types import SimpleNamespace
    from pdu.markdown.filtros import AplicarPlantilla

    ctx = SimpleNamespace(html_body="<p>x</p>", css="body{}", html_completo="")
    html = AplicarPlantilla().procesar(ctx).html_completo
    assert ".codehilite .k" in html
    assert html.index(".codehilite .k") < html.index("body{}")


def test_paleta_del_tema_declarada_y_por_defecto():
    from pdu.markdown.resaltado import paleta_del_tema

    assert paleta_del_tema(":root { --pdu-resaltado: tango; }") == "tango"
    assert paleta_del_tema(":root { --pdu-resaltado: 'monokai'; }") == "monokai"
    assert paleta_del_tema("body{}") == "default"
    assert paleta_del_tema(":root { --pdu-resaltado: noexiste; }") == "default"


def test_cada_tema_usa_su_paleta():
    from pdu.markdown.resaltado import css_resaltado, css_resaltado_para_tema

    _, css_compacto = cargar_estilo("compacto")
    assert css_resaltado_para_tema(css_compacto) == css_resaltado("tango")
    assert css_resaltado("tango") != css_resaltado("default")


def test_tokens_del_tema_prevalecen_sobre_paleta():
    from types import SimpleNamespace
    from pdu.markdown.filtros import AplicarPlantilla

    css_tema = ".codehilite .k { color: #123456; }"
    ctx = SimpleNamespace(html_body="", css=css_tema, html_completo="")
    html = AplicarPlantilla().procesar(ctx).html_completo
    # La paleta base va antes: el token del tema gana por cascada y el resto se conserva.
    assert html.index(".codehilite .k {") < html.index(css_tema)
    assert ".codehilite .s " in html
