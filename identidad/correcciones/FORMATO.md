# Cómo se escribe una corrección

Esta carpeta es la pieza más valiosa del kit y la única que no se puede copiar de nadie.

Una corrección mal escrita no cambia nada. "No inventes datos" es un buen deseo, no una
corrección: el asistente ya cree que no inventa datos. Lo que cambia el comportamiento es el
caso concreto que salió mal.

---

## Las tres partes, y por qué las tres

Un archivo por corrección, en esta carpeta, con este formato:

```markdown
---
nombre: verificar-antes-de-afirmar
descripcion: buscar en la web antes de afirmar qué puede o no puede una herramienta
tipo: correccion
fecha: 2026-03-14
---

**Qué pasó.** Afirmé que la herramienta no soportaba X. El usuario me mandó la captura de la
pantalla donde sí lo soportaba. Mi información tenía ocho meses.

**Por qué importó.** No fue un detalle: sobre esa afirmación se descartó una opción que era la
correcta, y se perdieron dos días.

**Cómo se aplica.** Antes de afirmar qué puede o no puede una herramienta, buscarlo. Mi
conocimiento envejece y el usuario está viendo el presente. Si no puedo verificarlo, digo
"creo que, pero no lo verifiqué" en vez de afirmarlo.
```

**Qué pasó** tiene que ser el caso real, con detalles. Sin eso, en tres meses nadie entiende
de qué hablaba.

**Por qué importó** es lo que separa una manía de una regla. Si no le costó nada a nadie,
probablemente no es una corrección, es una preferencia. Escríbela igual, pero como preferencia.

**Cómo se aplica** tiene que ser accionable en el momento. "Ser más cuidadoso" no lo es.
"Antes de afirmar X, hacer Y" sí.

---

## Reglas de la carpeta

- **Una corrección por archivo.** Mezclar dos hace que ninguna se encuentre.
- **Enlaza las relacionadas** con `[[nombre-de-la-otra]]`. Los errores vienen en familias.
- **Si una corrección resulta equivocada, bórrala.** Una regla incorrecta es peor que ninguna,
  porque se obedece igual.
- **No guardes aquí lo que el repositorio ya dice.** La estructura del código, el historial de
  git y los arreglos pasados ya están en otro lado. Aquí va lo que no se puede deducir.

---

## Cuántas esperar

Las primeras semanas vas a escribir varias por día. Después bajan a una por semana, y cuando
bajan a una por mes es la señal de que está funcionando.

Si llevas un mes sin escribir ninguna, no es que el asistente sea perfecto: es que dejaste de
corregirlo, y eso se nota en el trabajo unas semanas después.
