#!/usr/bin/env python3
"""
Shared cron state helper for self-improving cron jobs.
All cron jobs should use this to load/store state, append to the shared log,
and detect anomalies (no-progress, empty data streaks, etc.).

Layout (default):

    ~/.cron-state/            <- base dir, override with CRON_STATE_DIR
        state/<job_id>.json   <- per-job state files
        runs.jsonl            <- append-only run log across all jobs

Set CRON_STATE_DIR to relocate everything (e.g. for a per-user runtime such
as Hermes: `export CRON_STATE_DIR=~/.hermes/cron`).

Usage inside a cron prompt or script:
    import sys, os
    # Adjust to wherever this repo's scripts/ dir is installed on your system.
    sys.path.insert(0, os.path.expanduser('~/.cron-state/scripts'))
    from state_helper import load_state, save_state, append_run, detect_no_progress

    STATE = load_state(JOB_ID)
    # ... compute metrics ...
    save_state(JOB_ID, STATE)
    append_run(JOB_ID, "job_name", "ok", {"event_count": 5, "output_hash": "abc123"})
"""
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

BASE_DIR = os.path.expanduser(os.environ.get("CRON_STATE_DIR", "~/.cron-state"))
STATE_DIR = os.path.join(BASE_DIR, "state")
LOG_PATH = os.path.join(BASE_DIR, "runs.jsonl")


def ensure_dirs():
    os.makedirs(STATE_DIR, exist_ok=True)


def _state_path(job_id: str) -> str:
    return os.path.join(STATE_DIR, f"{job_id}.json")


def load_state(job_id: str) -> Dict[str, Any]:
    ensure_dirs()
    path = _state_path(job_id)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def save_state(job_id: str, state: Dict[str, Any]) -> None:
    ensure_dirs()
    path = _state_path(job_id)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, path)


def append_run(job_id: str, name: str, status: str, metrics: Dict[str, Any]) -> None:
    ensure_dirs()
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "job_id": job_id,
        "name": name,
        "status": status,
        **metrics,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(rec) + "\n")


def detect_no_progress(job_id: str, key: str, threshold: int = 5) -> bool:
    """Return True if the last N runs show zero change on the given key."""
    state = load_state(job_id)
    history = state.get(f"{key}_history", [])
    return len(history) >= threshold and all(v == 0 for v in history[-threshold:])
