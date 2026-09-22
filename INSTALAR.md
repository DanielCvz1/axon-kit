# Instalación

Dos de las piezas son proyectos de otras personas. Se instalan directo de la fuente, no desde
este kit, por dos razones: así recibes sus actualizaciones, y así queda claro de quién es cada
cosa.

---

## 1. El grafo: Graphify

De **Safi Shamsi**, licencia MIT. https://github.com/safishamsi/graphify

```bash
pip install graphifyy
```

Queda como comando y como skill de Claude Code (`/graphify`). Convierte una carpeta de
archivos en un grafo consultable, con detección de comunidades y un reporte de auditoría.

**Cómo se usa después, en una línea:** antes de leer archivos, preguntarle al grafo.

```bash
python -m graphify query "tu pregunta"
```

---

## 2. El wiki: Wiki-Brain

De **@tenfoldmarc**, basado en el patrón de LLM Wiki de Andrej Karpathy.
https://github.com/tenfoldmarc/wiki-brain-skill

Sigue el README del proyecto. Te va a pedir una carpeta para el vault (sirve Obsidian, pero
no es obligatorio: son archivos Markdown).

La estructura que importa:

```
tu-vault/
  raw/      <- las fuentes tal como llegaron. NUNCA se editan.
  wiki/     <- lo interpretado. Aquí escribe el asistente.
  log.md    <- una línea por sesión.
```

**La regla que hace que funcione:** `raw/` es inmutable y `wiki/` es del asistente. Si
mezclas las dos, en un mes no vas a saber qué dijo la fuente y qué interpretó el modelo.

---

## 3. El resto de este kit

```bash
git clone <este-repo> axon-kit
cp axon-kit/CLAUDE.md.plantilla ~/.claude/CLAUDE.md
```

Edita las rutas del `CLAUDE.md` para que apunten a tu vault. Es el único archivo donde hay
rutas absolutas.

---

## 4. FORGE (opcional, y déjalo para después)

```bash
cd axon-kit/forge
python -m runner.run missions/ejemplo.yaml
```

Corre la misión de ejemplo y escribe un reporte en `reports/`. Cuando quieras medir algo tuyo,
copia `adapters/ejemplo.py` y `missions/ejemplo.yaml` y cámbialos.

No lo instales el primer día. FORGE sirve para medir algo que ya existe; si todavía no tienes
qué medir, solo agrega ceremonia.

---

## Qué NO necesitas

- No necesitas un modelo local ni GPU.
- No necesitas base de datos: todo son archivos.
- No necesitas pagar nada de este kit. Lo único que cuesta es lo que ya pagas por tu asistente.
