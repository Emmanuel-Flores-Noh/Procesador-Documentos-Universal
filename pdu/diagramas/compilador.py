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


def _ejecutar_mmdc(mmdc: str, config: str, entrada: str, salida: str) -> None:
    resultado = subprocess.run(
        [mmdc, "-q", "-p", config, "-i", entrada, "-o", salida, "-b", "transparent"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if resultado.returncode != 0:
        detalle = (resultado.stderr or "").strip().splitlines()
        raise RuntimeError(detalle[-1] if detalle else f"mmdc terminó con código {resultado.returncode}")


def compilar_diagrama(archivo, ruta_png, ruta_pdf, config_puppeteer, mmdc=None) -> bool:
    """Compila `archivo` (.mmd) a PNG y PDF. Devuelve True si ambos se generaron."""
    nombre = os.path.basename(archivo)
    mmdc = mmdc or buscar_mmdc()
    if not mmdc:
        print(f"  [Error] {nombre}: no se encontró Mermaid CLI (mmdc).")
        return False
    try:
        for salida in (ruta_png, ruta_pdf):
            os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True)
            _ejecutar_mmdc(mmdc, config_puppeteer, archivo, salida)
    except (RuntimeError, OSError) as e:
        print(f"  [Error] {nombre}: {e}")
        return False
    print(f"  [OK] {nombre} -> PNG y PDF")
    return True


def compilar_varios(diagramas, config_puppeteer, mmdc, trabajos: int | None = None) -> tuple[int, int]:
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
        return compilar_diagrama(d.ruta_mmd, d.ruta_png, d.ruta_pdf, config_puppeteer, mmdc)

    if trabajos == 1:
        resultados = [compilar(d) for d in diagramas]
    else:
        with ThreadPoolExecutor(max_workers=trabajos) as pool:
            resultados = list(pool.map(compilar, diagramas))
    compilados = sum(resultados)
    return compilados, len(resultados) - compilados
