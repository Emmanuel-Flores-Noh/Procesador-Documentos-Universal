"""Compilación de diagramas Mermaid con `mmdc` (secuencial o en paralelo)."""
from __future__ import annotations

import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

from .entorno import buscar_mmdc

TRABAJOS_MAXIMOS_POR_DEFECTO = 4


def trabajos_por_defecto() -> int:
    """Número de procesos `mmdc` simultáneos: $PDU_JOBS o min(4, núcleos)."""
    valor = os.environ.get("PDU_JOBS")
    if valor and valor.isdigit() and int(valor) > 0:
        return int(valor)
    return max(1, min(TRABAJOS_MAXIMOS_POR_DEFECTO, os.cpu_count() or 1))


def _ejecutar_mmdc(mmdc: str, config: str, entrada: str, salida: str, config_mermaid: str | None = None) -> None:
    comando = [mmdc, "-q", "-p", config, "-i", entrada, "-o", salida, "-b", "transparent"]
    if config_mermaid:
        comando += ["-c", config_mermaid]
    resultado = subprocess.run(
        comando,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if resultado.returncode != 0:
        detalle = (resultado.stderr or "").strip().splitlines()
        raise RuntimeError(detalle[-1] if detalle else f"mmdc terminó con código {resultado.returncode}")


def compilar_diagrama(
    archivo, ruta_png, ruta_pdf, config_puppeteer, mmdc=None, ruta_svg=None, config_mermaid=None
) -> bool:
    """Compila `archivo` (.mmd) a PNG, PDF y (si se indica `ruta_svg`) SVG.

    Devuelve True si se generaron todas las salidas. El SVG se exporta con
    `config_mermaid` (etiquetas SVG nativas, compatibles con WeasyPrint).
    """
    nombre = os.path.basename(archivo)
    mmdc = mmdc or buscar_mmdc()
    if not mmdc:
        print(f"  [Error] {nombre}: no se encontró Mermaid CLI (mmdc).")
        return False
    try:
        salidas = [(ruta_png, None), (ruta_pdf, None)]
        if ruta_svg:
            salidas.append((ruta_svg, config_mermaid))
        for salida, config in salidas:
            os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True)
            _ejecutar_mmdc(mmdc, config_puppeteer, archivo, salida, config)
    except (RuntimeError, OSError) as e:
        print(f"  [Error] {nombre}: {e}")
        return False
    print(f"  [OK] {nombre} -> {'PNG, PDF y SVG' if ruta_svg else 'PNG y PDF'}")
    return True


def compilar_varios(
    diagramas, config_puppeteer, mmdc, trabajos: int | None = None, config_mermaid: str | None = None
) -> tuple[int, int]:
    """Compila una lista de `Diagrama` en paralelo. Devuelve (compilados, fallidos).

    Cada `mmdc` lanza su propio navegador, así que el paralelismo reduce mucho
    el tiempo total cuando hay varios diagramas.
    """
    diagramas = list(diagramas)
    if not diagramas:
        return 0, 0
    trabajos = max(1, min(trabajos or trabajos_por_defecto(), len(diagramas)))
    modo = f"{trabajos} procesos en paralelo" if trabajos > 1 else "1 proceso"
    print(f"Compilando {len(diagramas)} diagrama(s) con {modo} ...")

    def compilar(d):
        return compilar_diagrama(
            d.ruta_mmd, d.ruta_png, d.ruta_pdf, config_puppeteer, mmdc,
            ruta_svg=d.ruta_svg or None, config_mermaid=config_mermaid,
        )

    if trabajos == 1:
        resultados = [compilar(d) for d in diagramas]
    else:
        with ThreadPoolExecutor(max_workers=trabajos) as pool:
            resultados = list(pool.map(compilar, diagramas))
    compilados = sum(resultados)
    return compilados, len(resultados) - compilados
