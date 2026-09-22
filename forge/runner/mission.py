"""
FORGE runner -- la mision: que se prueba, con que configuraciones y con que umbrales.

Una mision es un archivo YAML bajo control de versiones. Los umbrales viven ahi y no en el
codigo, por la misma razon que forge.yaml: FORGE no puede aprobar redefiniendo PASS. Cambiar
un umbral es un commit con razon declarada.

Estructura:

    id: mi-primera-mision
    domain: ejemplo          # adaptador que ejecuta los escenarios
    question: ...                  # que decision informa esta mision
    configurations:                # las perillas que se comparan
      actual:   {query_idf: true,  corpus_lexical_rescale: true, ...}
      sin_idf:  {query_idf: false, ...}
    scenarios: [...]               # los define el adaptador o el propio archivo
    thresholds:
      pass_rate_min: 1.0           # sobre la configuracion elegida
      worst_case_min: 0.8          # peor escenario, no promedio
      latency_p95_max_s: 2.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Mission:
    id: str
    domain: str
    question: str
    configurations: dict[str, dict[str, Any]]
    thresholds: dict[str, float]
    scenarios: list[dict] = field(default_factory=list)
    scenario_file: str | None = None
    notes: str = ""
    limits: list[str] = field(default_factory=list)
    path: Path | None = None

    @property
    def baseline(self) -> str:
        """La configuracion contra la que se comparan las demas: la primera declarada."""
        return next(iter(self.configurations))


def load(path: str | Path) -> Mission:
    p = Path(path)
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    missing = [k for k in ("id", "domain", "configurations", "thresholds") if k not in raw]
    if missing:
        raise ValueError(f"{p.name}: faltan campos obligatorios: {', '.join(missing)}")
    if not raw.get("scenarios") and not raw.get("scenario_file"):
        raise ValueError(f"{p.name}: la mision no declara escenarios ni scenario_file")
    return Mission(
        id=raw["id"], domain=raw["domain"], question=raw.get("question", ""),
        configurations=raw["configurations"], thresholds=raw["thresholds"],
        scenarios=raw.get("scenarios") or [], scenario_file=raw.get("scenario_file"),
        notes=raw.get("notes", ""), limits=raw.get("limits") or [], path=p,
    )
