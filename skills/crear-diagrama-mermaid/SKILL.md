---
name: crear-diagrama-mermaid
description: Crea diagramas Mermaid (.mmd) en docs/diagramas/ para que pdu los compile a PNG y PDF, y los enlaza desde los documentos Markdown. Úsala cuando el usuario pida un diagrama de flujo, de arquitectura, de secuencia, de clases, entidad-relación, de estados, un Gantt, etc. NO compila; al terminar indica los comandos para revisar y compilar.
---

# Crear diagramas Mermaid para pdu

Escribes archivos `.mmd` que `pdu` compilará con Mermaid CLI. **No ejecutes ningún
comando `pdu` ni `mmdc`**: el usuario quiere revisar y modificar el diagrama antes de
convertirlo. Al final le dices qué comandos ejecutar.

## 1. Ubicación y nombre

- Guarda el archivo en `docs/diagramas/<nombre>.mmd` (créala si no existe).
- Usa `<nombre>` en kebab-case, sin tildes ni espacios: `flujo-auth.mmd`,
  `arquitectura-general.mmd`. El PNG y el PDF compilados tendrán ese mismo nombre.
- Antes de crear uno, revisa `docs/diagramas/` para no duplicar un diagrama existente;
  si ya existe uno parecido, propón modificarlo.
- El archivo contiene **solo** código Mermaid: sin cercas ```` ```mermaid ```` y sin
  front-matter salvo que haga falta configurar el tema.

## 2. Elegir el tipo

| Necesidad                          | Tipo Mermaid           |
|------------------------------------|------------------------|
| Proceso, algoritmo, decisión       | `flowchart TD` / `LR`  |
| Componentes y dependencias         | `graph TD`             |
| Interacción entre actores en el tiempo | `sequenceDiagram`  |
| Modelo de clases                   | `classDiagram`         |
| Base de datos                      | `erDiagram`            |
| Ciclo de vida o estados            | `stateDiagram-v2`      |
| Planificación                      | `gantt`                |
| Proporciones                       | `pie`                  |

## 3. Reglas de estilo

- Un diagrama, una idea. Por encima de unos 15 nodos, divídelo en varios archivos.
- Usa `TD` para jerarquías y `LR` para pipelines (como `docs/diagramas/pipeline.mmd`).
  En PDF vertical, los diagramas `LR` muy largos quedan pequeños.
- Usa IDs cortos en MAYÚSCULAS o camelCase y textos legibles entre corchetes:
  `CLI[Interfaz de línea de comandos]`.
- Si una etiqueta lleva caracteres especiales (`( ) : ; # " /`, tildes, `<`, `>`),
  ponla entre comillas: `A["Lectura (async)"]`.
- Etiqueta las aristas solo cuando aporten información: `A -->|sí| B`.
- No fijes colores ni temas salvo que el usuario lo pida: pdu compila PNG con fondo
  transparente y el resultado debe verse bien sobre el CSS del documento.
- Sigue la convención de los diagramas existentes del proyecto (encabezado
  `graph TD` / `flowchart TD`, indentación de 4 espacios).

Ejemplo:

```
flowchart TD
    U[Usuario] --> LOGIN[Pantalla de acceso]
    LOGIN --> VAL{"¿Credenciales válidas?"}
    VAL -->|sí| PANEL[Panel principal]
    VAL -->|no| ERR[Mensaje de error]
    ERR --> LOGIN
```

## 4. Validar sin compilar

Revisa mentalmente la sintaxis: que cada `subgraph` tenga su `end`, que los corchetes y
las comillas estén cerrados, que en `sequenceDiagram` uses `->>`, `-->>` o `-x` y que no
haya IDs repetidos con etiquetas distintas. Si tienes dudas sobre una construcción,
elige la forma más simple y compatible.

## 5. Enlazar desde un documento

Si el diagrama pertenece a un documento de `docs/markdown/<Documento>/`, añade la
referencia en el lugar adecuado (o indícale al usuario dónde ponerla):

```markdown
![Flujo de autenticación](flujo-auth.mmd)
```

pdu sustituye esa referencia por el PNG compilado al generar el PDF. Para redactar el
documento sigue la skill `crear-documento-markdown`.

## 6. Al terminar (sin compilar)

Responde con:

1. Los archivos `.mmd` creados o modificados y, si los hay, los `.md` donde los
   enlazaste.
2. Los comandos para revisar y compilar, con las rutas reales:

```bash
# Compilar solo este diagrama -> ./flujo-auth.png y ./flujo-auth.pdf (para revisarlo)
pdu mermaid docs/diagramas/flujo-auth.mmd

# Compilar todos los diagramas de docs/ -> ./out (omite los que ya están al día)
pdu mermaid docs

# Recompilar aunque estén al día
pdu mermaid docs --forzar

# Generar el PDF del documento que lo usa (compila los diagramas que falten)
pdu markdown docs/markdown/<Documento>
```

Sugiere también la vista previa en https://mermaid.live si el usuario quiere iterar
rápido antes de compilar.
