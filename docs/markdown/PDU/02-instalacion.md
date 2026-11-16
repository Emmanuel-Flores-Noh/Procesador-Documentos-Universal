# Instalación

## Instalación del paquete

```bash
pip install .
# o en desarrollo
pip install -e .
```

Dependencias principales: `markdown`, `weasyprint`, `ziamath`.

## Configuración local completa

Ejecuta el script de configuración:

```bash
./setup-local.sh        # Linux/macOS
setup-local.cmd         # Windows
```

El script:

- crea un entorno virtual compartido;
- instala `pdu` y sus dependencias;
- instala Mermaid CLI en `<data_dir>/bin`;
- deja disponible la carpeta de estilos de usuario.

## Directorio de datos

- Linux: `~/.local/share/pdu`
- Windows: `%APPDATA%\pdu`

Subcarpetas relevantes:

- `bin/`: binarios (Mermaid CLI).
- `estilos/`: estilos CSS de usuario.
- `puppeteer-config.json`: configuración generada para Mermaid CLI.

![Directorio de datos y estilos](datos-estilos.mmd)
