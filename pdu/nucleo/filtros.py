"""Motor genérico de Pipes and Filters."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Generic, Iterable, Protocol, TypeVar

from .errores import ErrorProcesador

T = TypeVar("T")


class Filtro(Protocol[T]):
    """Un filtro transforma un dato de tipo T en otro dato del mismo tipo."""
    nombre: str

    def procesar(self, datos: T) -> T: ...


@dataclass
class FiltroFuncion(Generic[T]):
    """Adaptador para convertir una función en un filtro."""
    nombre: str
    funcion: Callable[[T], T]

    def procesar(self, datos: T) -> T:
        return self.funcion(datos)


class Tuberia(Generic[T]):
    """Encadena filtros aplicándolos uno tras otro sobre un único dato.

    Cualquier excepción que no sea `ErrorProcesador` se envuelve en una que
    indica el filtro y la tubería donde ocurrió. El `observador` opcional
    recibe ``al_iniciar(tuberia, filtro)`` y ``al_terminar(tuberia, filtro, segundos)``.
    """

    def __init__(self, nombre: str, filtros: Iterable[Filtro[T]], observador=None) -> None:
        self.nombre = nombre
        self.filtros = list(filtros)
        self.observador = observador

    def ejecutar(self, datos: T) -> T:
        actual = datos
        for filtro in self.filtros:
            nombre_filtro = getattr(filtro, "nombre", type(filtro).__name__)
            if self.observador is not None:
                self.observador.al_iniciar(self.nombre, nombre_filtro)
            inicio = time.perf_counter()
            try:
                actual = filtro.procesar(actual)
            except ErrorProcesador:
                raise
            except Exception as exc:
                raise ErrorProcesador(
                    f"Fallo en el filtro '{nombre_filtro}' de la tubería '{self.nombre}': {exc}"
                ) from exc
            finally:
                if self.observador is not None:
                    self.observador.al_terminar(self.nombre, nombre_filtro, time.perf_counter() - inicio)
        return actual
