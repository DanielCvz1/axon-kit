# Kit AXON

El andamiaje para que un asistente de código deje de empezar de cero cada conversación.

No es un producto. Es lo que quedó después de varios meses de corregir a un asistente hasta
que dejó de repetir los mismos errores, empaquetado para que alguien más no tenga que
inventarlo desde el principio.

---

## Lo que esto NO es, y conviene decirlo primero

**No es un Jarvis que se instala.** El día uno vas a tener un asistente bien organizado, no
uno que te conozca. Lo que lo vuelve tuyo es el punto 2 de la lista de abajo, y ese tarda
meses porque depende de que tú lo corrijas y de que la corrección quede escrita.

**No inventamos dos de las tres piezas.** El grafo y el wiki son proyectos públicos de otras
personas, con licencia MIT, y están acreditados en [INSTALAR.md](INSTALAR.md). Se instalan
gratis en diez minutos. Si alguien te los vende, te están vendiendo algo que es de alguien más.

**No trae contenido de nadie.** Las plantillas van vacías a propósito. Un archivo de identidad
con las correcciones de otra persona no te sirve: las correcciones valen porque son las tuyas.

---

## Las cuatro piezas, y por qué ninguna sirve sola

### 1. Memoria que se acumula (wiki-brain + grafo)

Un wiki que el asistente escribe y consulta, y un grafo encima para que pueda responder sin
releer todo. Ver [INSTALAR.md](INSTALAR.md).

**Sola no sirve:** un wiki al que nadie escribe se queda vacío, y un grafo sobre un wiki vacío
no tiene qué indexar.

### 2. El mecanismo de correcciones (`identidad/`)

Cada vez que el asistente se equivoca, la corrección se escribe con tres partes: qué pasó, por
qué importó y cómo aplicarla la próxima vez. Sin las tres, la corrección no cambia nada.

**Es la pieza que hace la diferencia**, y es la única que no se puede copiar de nadie.

### 3. El ritual de sesión (`CLAUDE.md.plantilla` y [RITUAL.md](RITUAL.md))

Traer el wiki al empezar, escribir la bitácora al terminar, sincronizar. Suena burocrático y
es el motor: sin el ritual, el punto 1 se queda vacío y el punto 2 nunca se escribe.

### 4. FORGE (`forge/`)

Un banco de pruebas con los umbrales congelados en un archivo bajo control de versiones, un
registro de corridas encadenado por hash, y selección por el peor escenario en vez de por el
promedio.

**Para qué:** impide que el asistente califique su propio trabajo. Si el umbral vive en el
código o en la cabeza de alguien, siempre se puede mover después de fallar. En un archivo con
historial, moverlo deja rastro.

---

## Orden sugerido

1. Instala el wiki y el grafo ([INSTALAR.md](INSTALAR.md)). Úsalos una semana antes de seguir.
2. Copia `CLAUDE.md.plantilla` a tu `CLAUDE.md` y ajústalo a tus rutas.
3. Llena `identidad/IDENTIDAD.plantilla.md`. Diez minutos, y se corrige sobre la marcha.
4. FORGE hasta el final, y solo cuando ya tengas algo cuya calidad quieras medir. Antes de eso
   es ceremonia sin contenido.

---

## Licencia

MIT. Ver [LICENSE](LICENSE). Úsalo, cámbialo, véndelo si quieres. Lo único que no puedes hacer
es reclamar que el grafo y el wiki son tuyos: no son míos tampoco.
