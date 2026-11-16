# Módulos

## `cli.py`

- `COMANDOS`: registro único de subcomandos (nombre, alias, resumen y destino `modulo:funcion`).
- Los módulos de cada subcomando se importan solo al ejecutarlo, por lo que `pdu --help` responde al instante.
- `main_all()`: subcomando `all`.

## `nucleo/`

- `rutas.py`: directorio de datos, reglas de salida (`resolver_salida`) y guardado de archivos.
- `contextos.py`: dataclasses que fluyen por las tuberías.
- `filtros.py`: motor genérico de Pipes and Filters.
- `bloques_codigo.py`: protección y restauración (en una sola pasada) de bloques de código.
- `patrones.py`: expresiones regulares compartidas (`PATRON_MMD`, `PATRON_IMG`, `PATRON_HTML_IMG`) y `es_url_externa()`.
- `ayuda.py`: `crear_parser()` con textos en español y la opción común `-j/--jobs`.
- `errores.py`: excepciones del procesador.

## `diagramas/`

- `entorno.py`: detección (cacheada) de `mmdc` y del navegador; configuración de Puppeteer en `<data_dir>/puppeteer-config.json`.
- `compilador.py`: compilación de un diagrama y `compilar_varios()` en paralelo.
- `descubrimiento.py`: búsqueda, resolución y comprobación de diagramas al día.
- `filtros.py`: filtros de la etapa.
- `tuberia.py`: tuberías autónoma y por documento.
- `cli.py`: subcomando `pdu mermaid`.

## `latex/`

- `renderizador.py`: LaTeX a SVG/Data URI con `ziamath` (cargado bajo demanda y con caché).
- `filtros.py`: sustitución de fórmulas de bloque y en línea.
- `tuberia.py`: tubería LaTeX y API pública.
- `cli.py`: subcomando `pdu latex`.

## `markdown/`

- `descubrimiento.py`: descubrimiento de documentos.
- `estilos.py`: carga de CSS (usuario y paquete).
- `filtros.py`: filtros de documentos.
- `imagenes.py`: reescritura de imágenes a URIs absolutas.
- `pdf.py`: generación de PDF con WeasyPrint (importado solo al escribir el PDF).
- `plantilla.py`: plantilla HTML.
- `tuberia.py`: procesamiento de documentos.
- `cli.py`: subcomando `pdu markdown` y opciones compartidas con `pdu all`.
