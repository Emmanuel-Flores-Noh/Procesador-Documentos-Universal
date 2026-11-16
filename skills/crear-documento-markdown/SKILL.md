---
name: crear-documento-markdown
description: Redacta documentos Markdown listos para convertirse a PDF con pdu (docs/markdown/<Documento>/NN-seccion.md), con diagramas Mermaid, imágenes y fórmulas LaTeX. Úsala cuando el usuario pida crear, escribir o ampliar documentación, un manual, un informe o capítulos para pdu. NO compila; al terminar indica los comandos para revisar y convertir a PDF.
---

# Crear documentos Markdown para pdu

Escribes los archivos `.md` de un documento que `pdu` convertirá a PDF. **No ejecutes
ningún comando `pdu`** (ni `pdu markdown`, ni `pdu all`, ni `pdu latex`): el usuario
quiere revisar y editar los archivos antes de convertirlos. Al final le dices qué
comandos ejecutar.

## 1. Ubicación y estructura

```
docs/
  diagramas/            .mmd compartidos (ver skill crear-diagrama-mermaid)
  markdown/
    <Documento>/        cada subcarpeta genera <Documento>.pdf
      01-introduccion.md
      02-instalacion.md
      ...
  extras/               imágenes y otros recursos
```

- Si `docs/` (o la carpeta que indique el usuario) no tiene `diagramas/`, `markdown/` y
  `extras/`, créalas al escribir los archivos, o sugiere al usuario `pdu estructura docs`.
- El nombre de la subcarpeta es el nombre del PDF: usa algo corto y sin espacios
  (`Manual-Usuario`, `PDU`).
- Pregunta el nombre del documento solo si no se deduce del pedido.

## 2. Reglas que impone pdu

**Orden y saltos de página.** Los `.md` de una carpeta se concatenan en **orden
alfabético** y se inserta un salto de página entre archivos. Por eso:
- Usa el prefijo numérico de dos cifras: `01-`, `02-`, … `10-`.
- Un archivo equivale a un capítulo o sección que empieza en página nueva.
- Empieza cada archivo con un único `# Título`; usa `##` y `###` dentro.

**Markdown soportado.** Python-Markdown con las extensiones `fenced_code` y `tables`:
encabezados, listas, **negrita**, *cursiva*, enlaces, tablas, citas, bloques de código
con lenguaje y HTML en línea. No hay listas de tareas, notas al pie ni tablas de
contenido automáticas.
- Deja una línea en blanco antes y después de listas, tablas y bloques de código
  (Python-Markdown es estricto con esto).
- Indenta las listas anidadas con 4 espacios.

**Diagramas Mermaid.** Se referencian como imagen con extensión `.mmd`:

```markdown
![Flujo de autenticación](flujo-auth.mmd)
```

pdu busca el archivo en este orden: `docs/diagramas/<ref>.mmd`, la carpeta del
documento, `docs/<ref>.mmd` y `docs/diagramas/<nombre>.mmd`. Lo habitual es poner
solo el nombre y guardar el `.mmd` en `docs/diagramas/`. Para crear el diagrama sigue la
skill `crear-diagrama-mermaid`. Si el diagrama no existe, créalo o avisa al usuario.

**Imágenes.** Las rutas relativas se resuelven **desde la carpeta del documento**
(`docs/markdown/<Documento>/`):

```markdown
![Captura del panel](../../extras/panel.png)
<img src="../../extras/logo.png" width="120">
```

Las URL `http(s)://` y `data:` se dejan tal cual. Comprueba que la imagen exista; si no,
díselo al usuario en el resumen final.

**Fórmulas LaTeX.** Se renderizan a SVG con ziamath (no hace falta TeX instalado):

| Tipo     | Sintaxis                                       |
|----------|------------------------------------------------|
| En línea | `$E = mc^2$` o `\(E = mc^2\)`                  |
| Bloque   | `$$\int_0^1 x\,dx$$`, `\[ ... \]` o ```` ```math ```` |

- En las fórmulas en línea no dejes espacios junto a los `$`: `$x$` sí, `$ x $` no.
- Para escribir un dólar literal usa `\$` (por ejemplo, `cuesta \$20`).
- El contenido entre comillas invertidas (`` `...` `` y bloques ```` ``` ````) **no** se
  procesa: úsalo para mostrar código o LaTeX sin renderizar.

**Saltos de página manuales.** Dentro de un mismo archivo:

```html
<div style="page-break-before: always;"></div>
```

## 3. Estilo de redacción

- Escribe en el idioma del usuario (por defecto, español) con tildes correctas.
- Usa párrafos cortos, encabezados descriptivos, tablas para comparar y listas para
  pasos.
- Incluye un diagrama cuando aclare una arquitectura, un flujo o una secuencia; no lo
  añadas por adorno.
- No inventes datos técnicos (versiones, comandos, rutas). Si faltan, deja un
  `**TODO:**` visible y menciónalo en el resumen.

## 4. Al terminar (sin compilar)

Responde con:

1. La lista de archivos creados o modificados.
2. Los diagramas o imágenes que faltan, si hay alguno.
3. Los comandos para que el usuario revise y convierta, adaptados a las rutas reales:

```bash
# (Opcional) Ver el Markdown con las fórmulas ya sustituidas, sin generar PDF
pdu latex docs/markdown/<Documento>/01-introduccion.md --stdout

# Generar solo este documento -> ./out/<Documento>.pdf
pdu markdown docs/markdown/<Documento>

# Con otro estilo (pdu markdown --listar-estilos muestra los disponibles)
pdu markdown docs/markdown/<Documento> --estilo academico

# Pipeline completo: todos los diagramas y documentos de docs/ -> ./out
pdu docs
```

Recuérdale que puede editar los `.md` antes de ejecutarlos y que los diagramas
referenciados se compilan automáticamente al generar el PDF.
