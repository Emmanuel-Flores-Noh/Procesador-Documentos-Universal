# Desarrollo

## Ejecutar tests

```bash
pip install -e ".[dev]"
pytest tests/
```

Con una instalación normal (`pip install .`) el comando `pdu` usa la copia de `site-packages`; para probar cambios del código fuente instala en modo editable o reinstala.

## Empaquetado

El proyecto usa `pyproject.toml` con `setuptools`. El paquete instalable se llama `pdu`.

## Extender la CLI

Los subcomandos se registran en `COMANDOS` de `pdu/cli.py`. Para añadir uno nuevo:

1. Crear el módulo en `pdu/` con una función `main(argv=None) -> int`.
2. Construir su parser con `pdu.nucleo.ayuda.crear_parser()`, incluyendo descripción, epílogo con ejemplos y alias.
3. Añadir una entrada `Comando(nombre, alias, resumen, "modulo:main")` a `COMANDOS`.

La ayuda general, los alias y las sugerencias ante errores se generan a partir de ese registro.

## Rendimiento

- No importar dependencias pesadas (WeasyPrint, ziamath) a nivel de módulo en código que use la CLI.
- Los diagramas se compilan en paralelo (`-j`) y solo cuando el `.mmd` es más reciente que sus salidas.

## Estilos de usuario

Los archivos `.css` colocados en `<data_dir>/estilos/` aparecen automáticamente en `estilos_disponibles()` y pueden usarse con `--estilo`.
