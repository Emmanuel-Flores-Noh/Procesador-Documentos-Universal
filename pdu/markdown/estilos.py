"""Carga de estilos CSS (del usuario y del paquete)."""
from __future__ import annotations

from pathlib import Path

from ..nucleo.rutas import directorio_datos

DIR_ESTILOS = Path(__file__).resolve().parent / "estilos"
ESTILO_POR_DEFECTO = "default"


def directorio_estilos_usuario(crear: bool = True) -> Path:
    """``<data_dir>/estilos``: los .css que el usuario coloque aquí quedan disponibles."""
    ruta = Path(directorio_datos(crear=crear)) / "estilos"
    if crear:
        try:
            ruta.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
    return ruta


def directorios_estilos() -> list[Path]:
    """Directorios donde se buscan estilos: usuario primero (prevalece), paquete después.

    También se acepta ``<data_dir>/styles`` por compatibilidad.
    """
    usuario = directorio_estilos_usuario()
    return [usuario, usuario.with_name("styles"), DIR_ESTILOS]


def estilos_disponibles() -> list[str]:
    nombres = {ruta.stem for d in directorios_estilos() if d.is_dir() for ruta in d.glob("*.css")}
    return sorted(nombres)


def resolver_estilo(estilo=None) -> Path:
    """Acepta un nombre de estilo (``academico``) o la ruta a un archivo .css."""
    valor = (estilo or ESTILO_POR_DEFECTO).strip()
    candidato = Path(valor).expanduser()
    if candidato.is_file():
        return candidato.resolve()
    nombre = candidato.stem if candidato.suffix.lower() == ".css" else valor
    for directorio in directorios_estilos():
        ruta = directorio / f"{nombre}.css"
        if ruta.is_file():
            return ruta.resolve()
    raise ValueError(
        f"Estilo no encontrado: '{valor}'. Disponibles: {', '.join(estilos_disponibles())} "
        f"(o la ruta a un archivo .css)."
    )


def cargar_estilo(estilo=None) -> tuple[str, str]:
    """Devuelve ``(nombre, contenido_css)``."""
    ruta = resolver_estilo(estilo)
    return ruta.stem, ruta.read_text(encoding="utf-8")
