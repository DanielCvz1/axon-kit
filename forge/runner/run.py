"""
FORGE runner -- ejecuta una mision: escenarios x configuraciones, registro y reporte.

    python -m runner.run missions/mi-primera-mision.yaml [--registry ruta] [--quiet]

Corre sin Claude a proposito: es un script que el Programador de tareas de Windows puede
lanzar de madrugada. Claude entra despues, a leer el reporte. La leccion viene de los turnos
nocturnos de tu sistema, que se quedaban detenidos esperando un permiso de la sesion.
"""

from __future__ import annotations

import importlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runner import mission as mission_mod  # noqa: E402
from runner import report as report_mod  # noqa: E402
from runner import robustness  # noqa: E402
from runner.registry import RunRegistry, code_commit  # noqa: E402

ADAPTERS = {"ejemplo": "adapters.ejemplo"}
DEFAULT_REGISTRY = ROOT / "runs" / "forge_runs.db"
REPORTS = ROOT / "reports"


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print("uso: python -m runner.run missions/<mision>.yaml [--registry ruta] [--quiet]")
        return 2
    quiet = "--quiet" in argv
    reg_path = Path(argv[argv.index("--registry") + 1]) if "--registry" in argv else DEFAULT_REGISTRY

    m = mission_mod.load(args[0])
    if m.domain not in ADAPTERS:
        print(f"dominio sin adaptador: {m.domain}")
        return 2
    adapter = importlib.import_module(ADAPTERS[m.domain])

    scenarios = m.scenarios
    if m.scenario_file:
        import yaml
        scenarios = yaml.safe_load((m.path.parent / m.scenario_file).read_text(encoding="utf-8"))

    registry = RunRegistry(reg_path)
    commit = getattr(adapter, "code_commit", lambda: None)() or code_commit(ROOT)
    run_id = registry.start(m.id, commit, platform.node())
    if not quiet:
        print(f"FORGE {m.id} | corrida {run_id} | codigo {commit} | "
              f"{len(scenarios)} escenarios x {len(m.configurations)} configuraciones")

    summaries = []
    for name, cfg in m.configurations.items():
        results = adapter.run(cfg, scenarios)
        for r in results:
            registry.record(run_id, name, cfg, r["scenario"], r)
        s = robustness.summarize(name, results)
        summaries.append(s)
        if not quiet:
            print(f"  {name:24} {s.passed}/{s.total} escenarios | peor {s.worst_score:.2f} | "
                  f"p95 {s.latency_p95:.2f}s" + (f" | fallan: {', '.join(s.failures)}" if s.failures else ""))

    chosen = robustness.choose(summaries, baseline=m.baseline)
    status, reasons = robustness.verdict(chosen, m.thresholds)
    prev = registry.previous_run(m.id, run_id)
    prev_summary = json.loads(prev["summary"]) if prev and prev["summary"] else None
    regressions = robustness.compare_with_previous(summaries, prev_summary)

    summary = {
        "mission": m.id, "chosen": chosen.name, "verdict": status, "reasons": reasons,
        "regret": robustness.regret(summaries, chosen), "regressions": regressions,
        "scenarios": len(scenarios), "code_commit": commit,
        "configurations": [{"name": s.name, "pass_rate": s.pass_rate, "worst_score": s.worst_score,
                            "mean_score": s.mean_score, "latency_p95": s.latency_p95,
                            "failures": s.failures} for s in summaries],
    }
    registry.finish(run_id, status, summary)
    chain_ok, chain_detail = registry.verify_chain()

    REPORTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d_%H%M")
    out = REPORTS / f"{m.id}_{stamp}.md"
    out.write_text(report_mod.render(m, summaries, chosen, status, reasons, summary,
                                     run_id, commit, chain_detail), encoding="utf-8")
    registry.close()

    if not quiet:
        print(f"\nElegida: {chosen.name} | veredicto {status}")
        for r in reasons:
            print("   ", r)
        for r in regressions:
            print("   regresion:", r)
        print(f"registro: {reg_path} ({chain_detail})")
        print(f"reporte: {out}")
    return 0 if status == "PASS" and chain_ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
