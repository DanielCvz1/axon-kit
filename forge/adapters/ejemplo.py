"""
Adaptador de ejemplo. Corre tal cual, sin instalar nada ni conectar ningún sistema.

Un adaptador es lo único que FORGE necesita saber de tu dominio. El contrato es corto:

    run(config: dict, scenarios: list[dict]) -> list[dict]

y cada resultado es `{"scenario": ..., "passed": bool, "score": float, "latency_s": float,
"detail": str}`. El `score` va de 0 a 1 y existe para poder mirar el PEOR escenario en vez del
promedio, que es lo que FORGE hace al elegir.

Lo que se mide aquí es un buscador de juguete sobre seis frases, con dos perillas. Es
deliberadamente trivial: lo que hay que entender no es el buscador, es que un promedio de 0.83
puede esconder un escenario en 0.00, y que esa diferencia es la que te muerde en producción.

Para medir lo tuyo: copia este archivo, cambia `_buscar` por una llamada a tu sistema y
registra el nombre del módulo en `runner/run.py` (diccionario `ADAPTERS`).
"""

from __future__ import annotations

import math
import re
import time
from collections import Counter
from typing import Any

# El "corpus": seis frases. En tu caso será tu base de datos, tu índice o tu API.
CORPUS = [
    ("d1", "el gato duerme sobre el tejado caliente"),
    ("d2", "la gata parió tres gatitos en el tejado"),
    ("d3", "el perro ladra al cartero todas las mañanas"),
    ("d4", "reparación del tejado después de la tormenta"),
    ("d5", "el cartero dejó un paquete para el vecino"),
    ("d6", "tormenta eléctrica prevista para el jueves"),
]


def _palabras(texto: str) -> list[str]:
    return re.findall(r"\w+", texto.lower())


def _idf() -> dict[str, float]:
    total = len(CORPUS)
    apariciones: Counter[str] = Counter()
    for _, texto in CORPUS:
        apariciones.update(set(_palabras(texto)))
    return {p: math.log(total / n) for p, n in apariciones.items()}


IDF = _idf()


def _buscar(consulta: str, config: dict[str, Any]) -> list[str]:
    """Devuelve los ids ordenados por relevancia. Dos perillas, y ambas existen porque cada
    una corresponde a un error real que se cometió alguna vez."""
    terminos = _palabras(consulta)
    puntajes: dict[str, float] = {}
    for doc_id, texto in CORPUS:
        palabras = _palabras(texto)
        puntaje = 0.0
        for t in terminos:
            if t in palabras:
                # Sin idf, "el" pesa lo mismo que "tejado" y la consulta se llena de ruido.
                puntaje += IDF.get(t, 1.0) if config.get("usar_idf", True) else 1.0
        if config.get("frase_exacta", True) and consulta.lower().strip() in texto:
            puntaje += 10.0
        if puntaje:
            puntajes[doc_id] = puntaje
    return [d for d, _ in sorted(puntajes.items(), key=lambda kv: -kv[1])]


def run_scenario(scenario: dict, config: dict[str, Any]) -> dict:
    t0 = time.perf_counter()
    resultados = _buscar(scenario["query"], config)
    latencia = time.perf_counter() - t0

    tope = scenario.get("within_top", len(resultados) or 1)
    ventana = resultados[:tope]
    partes, checks = [], []

    esperado = scenario.get("expect")
    if esperado:
        ok = esperado in ventana
        checks.append(ok)
        partes.append(f"esperado {esperado} -> " +
                      (f"posicion {ventana.index(esperado) + 1}" if ok else "NO aparece"))

    prohibido = scenario.get("forbid")
    if prohibido:
        ok = prohibido not in ventana
        checks.append(ok)
        partes.append(f"prohibido {prohibido} -> " + ("ausente" if ok else "APARECE"))

    if scenario.get("expect_empty"):
        ok = not resultados
        checks.append(ok)
        partes.append("se esperaba sin resultados -> " +
                      ("vacio" if ok else f"devolvio {len(resultados)}"))

    score = (sum(1 for c in checks if c) / len(checks)) if checks else 1.0
    return {"passed": score == 1.0, "score": round(score, 3),
            "latency_s": latencia, "detail": " | ".join(partes) or "sin comprobaciones"}


def run(config: dict[str, Any], scenarios: list[dict]) -> list[dict]:
    return [{"scenario": s, **run_scenario(s, config)} for s in scenarios]


def code_commit() -> str | None:
    """Opcional. Sirve para que el registro sepa qué versión del código se midió."""
    return None
