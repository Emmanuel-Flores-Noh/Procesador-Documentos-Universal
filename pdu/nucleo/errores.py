"""Excepciones del procesador."""


class ErrorProcesador(Exception):
    """Error genérico durante la ejecución de una tubería."""


class DependenciaFaltante(ErrorProcesador):
    """No se encontró una dependencia externa necesaria."""