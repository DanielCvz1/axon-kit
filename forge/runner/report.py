"""
FORGE runner -- reporte de una corrida, en lenguaje claro y sin guiones largos.

El reporte dice tres cosas, en este orden: que se eligio y por que, que habria pasado con las
otras configuraciones, y que empeoro respecto de la corrida anterior. Nada de puntajes de caja
negra: cada cifra se acompaña del escenario que la produjo.
"""

from __future__ import annotations

from datetime import datetime


def render(mission, summaries, chosen, status, reasons, summary, run_id, commit, chain_detail) -> str:
    L = []
    L.append(f"# FORGE: {mission.id}")
    L.append("")
    L.append(f"Corrida `{run_id}` del {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M')} "
             f"sobre el codigo `{commit or 'sin commit'}`.")
    L.append("")
    L.append(f"**Veredicto: {status}.** Configuracion elegida: **{chosen.name}** "
             f"({chosen.passed} de {chosen.total} escenarios, peor escenario {chosen.worst_score:.2f}, "
             f"latencia p95 {chosen.latency_p95:.2f} s).")
    if reasons:
        L.append("")
        L.append("Motivos del FAIL:")
        L.extend(f"- {r}" for r in reasons)
    if mission.question.strip():
        L.append("")
        L.append("> " + " ".join(mission.question.split()))
    L.append("")
    L.append("## Que habria pasado con otra configuracion")
    L.append("")
    L.append("| Configuracion | Escenarios | Peor escenario | Promedio | p95 | Escenarios que fallan |")
    L.append("|---|---|---|---|---|---|")
    for s in sorted(summaries, key=lambda s: (-s.worst_score, -s.pass_rate)):
        marca = " (elegida)" if s.name == chosen.name else ""
        L.append(f"| {s.name}{marca} | {s.passed}/{s.total} | {s.worst_score:.2f} | {s.mean_score:.2f} | "
                 f"{s.latency_p95:.2f} s | {', '.join(s.failures) or 'ninguno'} |")
    reg = summary.get("regret") or {}
    if reg:
        L.append("")
        L.append("Perdida por quedarse con otra configuracion, en tasa de escenarios: "
                 + ", ".join(f"{k} {v:+.0%}" for k, v in sorted(reg.items(), key=lambda kv: kv[1])))
    L.append("")
    L.append("## Comparacion con la corrida anterior")
    L.append("")
    regressions = summary.get("regressions") or []
    if regressions:
        L.extend(f"- {r}" for r in regressions)
    else:
        L.append("Sin regresiones respecto de la corrida anterior de esta mision.")
    L.append("")
    L.append("## Integridad")
    L.append("")
    L.append(f"Registro de corridas: {chain_detail}. Los resultados de esta corrida quedan "
             "encadenados por hash y no se pueden alterar despues.")
    L.append("")
    L.append("## Limites de esta medicion")
    L.append("")
    # Esta seccion se personaliza por dominio. Existe porque un reporte que no dice lo que NO
    # midio invita a leerlo como si lo midiera todo.
    for limite in (getattr(mission, "limits", None) or [
            "Mide el mecanismo, no la calidad del resultado final.",
            "Los escenarios los escribio una persona: no son una muestra representativa.",
            "Ningun escenario usa datos reales de clientes."]):
        L.append(f"- {limite}")
    return "\n".join(L) + "\n"
