# Procesador Universal de Documentos (pdu)

`pdu` es una herramienta de línea de comandos para transformar documentación técnica en PDF, integrando tres etapas:

1. **Mermaid**: compila diagramas `.mmd` a PNG, PDF y SVG.
2. **LaTeX**: renderiza fórmulas matemáticas a SVG embebido en HTML.
3. **Markdown**: convierte documentos Markdown a PDF con plantilla HTML/CSS.

## Objetivos

- Ofrecer un pipeline reproducible de documentación.
- Ser instalable como paquete Python (`pip install .`).
- Funcionar en Windows y Linux.
- Permitir ejecutar el pipeline completo o una etapa concreta.

## Arquitectura general

![Arquitectura general](arquitectura-general.mmd)

## Características principales

- CLI unificada: `pdu all`, `pdu mermaid`, `pdu latex`, `pdu markdown`.
- Estructura de datos de usuario en `~/.local/share/pdu` (Linux) o `%APPDATA%\pdu` (Windows).
- Estilos CSS de usuario y del paquete.
- Generación de estructura de proyecto con `pdu estructura`.
- Compilación de diagramas en paralelo e incremental (solo los que cambiaron).
- Ayuda detallada por comando (`pdu <comando> --help`).
