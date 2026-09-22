"""
FORGE runner -- registro de corridas.

Cada corrida queda guardada y no se puede alterar despues: las filas van encadenadas por hash,
igual que el audit log de GraphOS. Sirve para dos cosas que un reporte suelto no puede dar:

  - comparar una corrida contra el historial (¿esta configuracion empeoro desde ayer?);
  - sostener que el resultado que se muestra es el que realmente se midio.

Una corrida guarda: mision, commit del codigo probado, configuracion (con su huella), cada
resultado por escenario y el veredicto. No guarda datos de clientes: los escenarios de tu sistema
trabajan con el corpus publico y casos sinteticos.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id        TEXT PRIMARY KEY,
    mission_id    TEXT NOT NULL,
    started_at    TEXT NOT NULL,
    finished_at   TEXT,
    code_commit   TEXT,
    host          TEXT,
    verdict       TEXT,
    summary       TEXT,
    previous_hash TEXT NOT NULL,
    this_hash     TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS results (
    result_id     TEXT PRIMARY KEY,
    run_id        TEXT NOT NULL REFERENCES runs(run_id),
    configuration TEXT NOT NULL,
    config_hash   TEXT NOT NULL,
    scenario_id   TEXT NOT NULL,
    scenario_kind TEXT,
    passed        INTEGER NOT NULL,
    score         REAL,
    latency_s     REAL,
    detail        TEXT
);
CREATE INDEX IF NOT EXISTS idx_results_run ON results(run_id, configuration);
CREATE INDEX IF NOT EXISTS idx_runs_mission ON runs(mission_id, started_at);
"""


def config_hash(config: dict) -> str:
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]


def code_commit(repo: Path) -> Optional[str]:
    try:
        out = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=20)
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


class RunRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    def start(self, mission_id: str, commit: Optional[str], host: str) -> str:
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        prev = self.conn.execute("SELECT this_hash FROM runs ORDER BY started_at DESC LIMIT 1").fetchone()
        previous_hash = prev["this_hash"] if prev else "genesis"
        started = datetime.now(timezone.utc).isoformat()
        payload = json.dumps({"run_id": run_id, "mission": mission_id, "at": started, "commit": commit},
                             sort_keys=True)
        this_hash = hashlib.sha256((payload + previous_hash).encode()).hexdigest()
        self.conn.execute(
            "INSERT INTO runs (run_id, mission_id, started_at, code_commit, host, previous_hash, this_hash) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (run_id, mission_id, started, commit, host, previous_hash, this_hash))
        self.conn.commit()
        return run_id

    def record(self, run_id: str, configuration: str, cfg: dict, scenario: dict, result: dict) -> None:
        self.conn.execute(
            "INSERT INTO results (result_id, run_id, configuration, config_hash, scenario_id, scenario_kind, "
            "passed, score, latency_s, detail) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (f"res_{uuid.uuid4().hex[:12]}", run_id, configuration, config_hash(cfg),
             scenario.get("id", "?"), scenario.get("kind"), int(bool(result.get("passed"))),
             result.get("score"), result.get("latency_s"), json.dumps(result.get("detail", ""), ensure_ascii=False)))
        self.conn.commit()

    def finish(self, run_id: str, verdict: str, summary: dict) -> None:
        self.conn.execute("UPDATE runs SET finished_at=?, verdict=?, summary=? WHERE run_id=?",
                          (datetime.now(timezone.utc).isoformat(), verdict,
                           json.dumps(summary, ensure_ascii=False), run_id))
        self.conn.commit()

    def previous_run(self, mission_id: str, before_run: str) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM runs WHERE mission_id=? AND run_id<>? AND finished_at IS NOT NULL "
            "ORDER BY started_at DESC LIMIT 1", (mission_id, before_run)).fetchone()

    def results(self, run_id: str) -> list[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM results WHERE run_id=?", (run_id,)).fetchall()

    def verify_chain(self) -> tuple[bool, str]:
        rows = self.conn.execute("SELECT * FROM runs ORDER BY started_at").fetchall()
        previous = "genesis"
        for r in rows:
            payload = json.dumps({"run_id": r["run_id"], "mission": r["mission_id"],
                                  "at": r["started_at"], "commit": r["code_commit"]}, sort_keys=True)
            expected = hashlib.sha256((payload + previous).encode()).hexdigest()
            if r["previous_hash"] != previous or r["this_hash"] != expected:
                return False, f"cadena rota en {r['run_id']}"
            previous = r["this_hash"]
        return True, f"cadena integra, {len(rows)} corrida(s)"

    def close(self) -> None:
        self.conn.close()
