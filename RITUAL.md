# El ritual de sesión

Es la parte que suena burocrática y es el motor de todo lo demás. Sin ritual, el wiki se queda
vacío, el grafo no tiene qué indexar y las correcciones nunca se escriben.

Son tres momentos.

---

## Al empezar

```bash
cd <tu-vault> && git pull --rebase origin main
```

Si trabajas en más de una máquina, esto evita que dos versiones del wiki se separen. Si
trabajas en una sola, igual sirve: te obliga a mirar qué pasó desde la última vez.

Y antes de leer archivos para entender algo, preguntarle al grafo:

```bash
python -m graphify query "tu pregunta"
```

Leer los archivos crudos es el plan B, no el A.

---

## Durante

**Si la sesión produjo conocimiento que va a servir después**, va al wiki antes de terminar:
decisiones tomadas, cosas aprendidas, problemas resueltos y por qué se resolvieron así. Con
enlaces `[[a otras páginas]]`, porque una página sin enlaces de entrada no la encuentra nadie.

**Si fue algo trivial**, no. Un arreglo de una línea no merece página. La bitácora basta.

La diferencia importa: un wiki lleno de ruido es tan inútil como uno vacío, y cuesta más
limpiarlo.

---

## Al terminar

Dos pasos, en este orden.

**1. Una línea en la bitácora:**

```markdown
## [2026-03-14 18:20] sesión | título de tres a ocho palabras
Tocado: <páginas del wiki, o "ninguna">
```

**2. Sincronizar**, con escaneo de secretos antes de commitear. Esto no es opcional: un wiki
personal acumula llaves de API, contraseñas y datos de clientes sin que nadie lo decida. Una
llave que entra al historial de git se queda ahí para siempre, aunque borres el archivo
después.

```bash
grep -rlE 'sk-[a-zA-Z0-9]{32,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}' --include='*.md' .
```

Si eso encuentra algo, **se detiene todo**, se redacta el valor y se avisa. Después se commitea.

> Una advertencia por experiencia: es fácil escribir ese escaneo de forma que siempre pase
> (por ejemplo encadenando el commit con `&&` después de un `echo` que nunca falla). Si el
> escaneo no puede detener el commit, no es un escaneo, es un adorno.

---

## Por qué el orden importa

La bitácora primero y la sincronización después, siempre. Si sincronizas antes de escribir la
bitácora, la sesión queda en el repositorio sin registro de qué fue, y en tres meses es un
commit huérfano que nadie sabe leer.

---

## Lo que este ritual compra

Nada el primer día. La segunda semana empiezas a notar que no repites explicaciones. Al mes,
el asistente contesta cosas de tu negocio que nunca le dijiste en esa conversación.

Ese es el único truco: no es que el modelo recuerde, es que escribió.
