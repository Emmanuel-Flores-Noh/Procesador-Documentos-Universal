# pdu — Procesador Universal de Documentos

CLI para procesar diagramas Mermaid, fórmulas LaTeX y documentos Markdown a PDF.

## Instalación

```bash
pip install .
# o en desarrollo
pip install -e .
```

## Uso

```bash
pdu                 # pipeline completo (docs)
pdu all docs
pdu diagramas docs
pdu latex docs
pdu markdown docs
pdu --help
```

Los estilos de usuario se pueden añadir en `~/.local/share/pdu/estilos` (Linux) o `%APPDATA%\pdu\estilos` (Windows).
