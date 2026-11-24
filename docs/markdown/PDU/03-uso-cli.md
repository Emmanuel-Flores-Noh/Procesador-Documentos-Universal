# Uso de la CLI

## Ayuda

```bash
pdu                  # ayuda general
pdu --help
pdu <comando> --help # ayuda detallada de cada comando
pdu help markdown    # equivalente a: pdu markdown --help
pdu --version
```

Si se escribe mal un comando, `pdu` sugiere el más parecido (por ejemplo, `pdu mermiad` → «¿Quisiste decir mermaid?»).

## Comandos y alias

| Comando      | Alias                                      | Descripción                                   |
|--------------|--------------------------------------------|-----------------------------------------------|
| `all`        | `todo`, `pipeline`, `0`                    | Pipeline completo hasta PDF.                  |
| `mermaid`    | `diagramas`, `diagrama`, `diagrams`, `1`   | Diagramas `.mmd` a PNG, PDF y SVG.            |
| `latex`      | `2`                                        | Fórmulas LaTeX a SVG.                         |
| `markdown`   | `md`, `3`                                  | Documentos Markdown a PDF.                    |
| `estructura` | `init`                                     | Crea la estructura de carpetas `docs/`.       |

Si el primer argumento no es un comando se asume `all`: `pdu docs` equivale a `pdu all docs`.

## Pipeline completo

```bash
pdu all docs
pdu docs -o build --estilo compacto
pdu docs --forzar -j 2
```

## Etapas individuales

```bash
pdu mermaid diagrama.mmd
pdu mermaid docs/diagramas -o salida
pdu latex --expr "E = mc^2"
pdu latex --expr "\frac{a}{b}" --inline -o fraccion.svg
pdu latex documento.md --stdout
pdu markdown documento.md
pdu markdown docs --estilo academico
pdu markdown --listar-estilos
```

## Opciones comunes

| Opción                 | Comandos                    | Efecto                                                     |
|------------------------|-----------------------------|------------------------------------------------------------|
| `-o`, `--out`          | todos                       | Carpeta (o archivo) de salida.                             |
| `-s`, `--estilo`       | `all`, `markdown`           | Nombre de estilo o ruta a un `.css`.                       |
| `--diagramas-out`      | `all`, `markdown`           | Carpeta de diagramas compilados (por defecto `<salida>/diagramas`). |
| `-f`, `--forzar`       | `all`, `mermaid`            | Recompila los diagramas aunque estén al día.               |
| `-j`, `--jobs N`       | `all`, `mermaid`, `markdown`| Procesos `mmdc` simultáneos (por defecto `min(4, núcleos)`).|

## Generar estructura de proyecto

```bash
pdu estructura docs
pdu estructura docs/MiProyecto --no-confirmation   # o -nc / -y
```

## Reglas de salida

- Un solo archivo de entrada: se guarda en el directorio actual con el nombre original.
- Un directorio: se crea `./out` en el directorio actual (también para `pdu all`).
- Se puede definir la carpeta de salida con `-o` / `--out`.
- Los diagramas cuyo PNG, PDF y SVG son más recientes que el `.mmd` no se recompilan.

## Variables de entorno

| Variable                    | Uso                                                   |
|-----------------------------|-------------------------------------------------------|
| `PDU_DATA_DIR`              | Directorio de datos (estilos, binarios).              |
| `PDU_JOBS`                  | Número de procesos `mmdc` por defecto.                |
| `MMDC_PATH`, `PDU_BIN`      | Ruta de Mermaid CLI o carpeta que lo contiene.        |
| `PUPPETEER_EXECUTABLE_PATH` | Navegador que usa Mermaid CLI.                        |

![Flujo de la CLI](flujo-cli.mmd)
