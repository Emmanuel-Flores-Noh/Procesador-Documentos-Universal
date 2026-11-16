# Arquitectura del proyecto

El paquete principal es `pdu/`. Sus módulos principales son:

- `cli.py`: punto de entrada y registro de subcomandos (importación diferida).
- `orquestador.py`: coordina el pipeline completo.
- `nucleo/`: contextos, filtros, rutas, patrones, ayuda y errores compartidos.
- `diagramas/`: detección y compilación de Mermaid.
- `latex/`: renderizado de fórmulas LaTeX.
- `markdown/`: conversión de Markdown a PDF.
- `estructura.py`: generación de la estructura de documentación.

## Estructura del paquete

![Estructura del paquete](estructura-paquete.mmd)

## Pipeline

![Pipeline de procesamiento](pipeline.mmd)
