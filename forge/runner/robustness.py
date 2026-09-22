"""
FORGE runner -- motor de robustez.

Separa las tres cosas que normalmente se mezclan:

  que paso            resultados de la configuracion vigente
  que habria pasado   los mismos escenarios con otras configuraciones
  que aguanta mas     cual configuracion sostiene el PEOR escenario, no el mejor promedio

Regla: se elige por el peor caso. Un promedio alto con un escenario en cero es exactamente el
modo de falla que este motor existe para evitar: el escenario que falla es justo el que
vas a encontrarte en produccion, y el promedio lo esconde.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field


@dataclass
class ConfigSummary:
    name: str
    passed: int
    total: int
    worst_score: float
    mean_score: float
    latency_p95: float
    failures: list[str] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total else 0.0


def summarize(name: str, results: list[dict]) -> ConfigSummary:
    scores = [r["score"] for r in results] or [0.0]
    lats = sorted(r["latency_s"] for r in results) or [0.0]
    p95 = lats[min(len(lats) - 1, int(round(0.95 * (len(lats) - 1))))]
    return ConfigSummary(
        name=name,
        passed=sum(1 for r in results if r["passed"]),
        total=len(results),
        worst_score=min(scores),
        mean_score=statistics.fmean(scores),
        latency_p95=p95,
        failures=[r["scenario"]["id"] for r in results if not r["passed"]],
    )


def choose(summaries: list[ConfigSummary], baseline: str | None = None) -> ConfigSummary:
    """Peor caso primero, luego mas escenarios pasados.

    Hallazgo de la primera corrida (2026-09-20): con todo empatado, desempatar por latencia
    elegia la configuracion que hace menos trabajo, que es justo la que se quiere descartar.
    A igualdad se queda la configuracion vigente (la primera declarada en la mision) y solo
    despues se mira la latencia: para cambiar lo que ya opera hace falta una mejora medible."""
    return sorted(summaries, key=lambda s: (-s.worst_score, -s.pass_rate,
                                            0 if s.name == baseline else 1, s.latency_p95))[0]


def regret(summaries: list[ConfigSummary], chosen: ConfigSummary) -> dict[str, float]:
    """Cuanto se pierde por quedarse con otra configuracion, medido en tasa de escenarios."""
    return {s.name: round(chosen.pass_rate - s.pass_rate, 4) for s in summaries if s.name != chosen.name}


def verdict(chosen: ConfigSummary, thresholds: dict) -> tuple[str, list[str]]:
    reasons = []
    if chosen.total < thresholds.get("min_scenarios", 1):
        reasons.append(f"escenarios insuficientes: {chosen.total} < {thresholds['min_scenarios']}")
    if chosen.pass_rate < thresholds.get("pass_rate_min", 1.0):
        reasons.append(f"tasa de escenarios {chosen.pass_rate:.0%} < {thresholds['pass_rate_min']:.0%}")
    if chosen.worst_score < thresholds.get("worst_case_min", 1.0):
        reasons.append(f"peor escenario {chosen.worst_score:.2f} < {thresholds['worst_case_min']:.2f}")
    if chosen.latency_p95 > thresholds.get("latency_p95_max_s", 1e9):
        reasons.append(f"latencia p95 {chosen.latency_p95:.2f}s > {thresholds['latency_p95_max_s']}s")
    return ("PASS" if not reasons else "FAIL"), reasons


def compare_with_previous(current: list[ConfigSummary], previous_summary: dict | None) -> list[str]:
    """Regresiones contra la corrida anterior de la misma mision."""
    if not previous_summary:
        return []
    prev = {c["name"]: c for c in previous_summary.get("configurations", [])}
    notes = []
    for s in current:
        old = prev.get(s.name)
        if not old:
            continue
        if s.pass_rate < old.get("pass_rate", 0):
            notes.append(f"{s.name}: la tasa bajo de {old['pass_rate']:.0%} a {s.pass_rate:.0%}")
        if s.worst_score < old.get("worst_score", 0):
            notes.append(f"{s.name}: el peor escenario bajo de {old['worst_score']:.2f} a {s.worst_score:.2f}")
    return notes
