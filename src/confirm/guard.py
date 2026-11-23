"""Guard of the confirmatory pipeline (plan draft 3, sections 3 and 12).

Every acquisition and analysis entry point calls check() before it reads API histories, photographs or predictions.
- Protected data: observations of locked-half observers (src/halves.py) and every observation of the six new families
  and of the 30 replication families (configs/confirmatory.yaml, sets new and replication).
- Mode "dry-run": protected data are always refused.
- Mode "confirmatory": protected data are refused unless configs/registration_lock.json exists and holds a non-empty
  "registration_id" and a "code_commit".
- Every refusal and every allowed set is appended to the guard log (JSON lines).
A refusal raises GuardRefusal; the caller stops before reading anything.
"""
import json
import time
from pathlib import Path

from src.halves import is_locked
from src.confirm.config import ROOT, load_config

LOCK_FILE = ROOT / "configs/registration_lock.json"


class GuardRefusal(Exception):
    """The guard refused a set of observations."""


def protected_families(cfg=None):
    cfg = cfg or load_config()
    return set(cfg["sets"]["new"]["families"]) | set(cfg["sets"]["replication"]["families"])


def lock_valid(lock_file=LOCK_FILE):
    p = Path(lock_file)
    if not p.exists():
        return False, "registration lock file absent"
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return False, "registration lock file not readable"
    if not str(d.get("registration_id", "")).strip() or not str(d.get("code_commit", "")).strip():
        return False, "registration lock file without registration_id or code_commit"
    return True, "registration lock valid"


def check(mode, step, families, observers, log_path, lock_file=LOCK_FILE, cfg=None):
    """mode: 'dry-run' or 'confirmatory'; families: family names of the set; observers: observer ids of the set.
    Returns None if allowed; raises GuardRefusal otherwise. Writes one log line either way."""
    if mode not in ("dry-run", "confirmatory"):
        raise GuardRefusal(f"unknown mode {mode}")
    fams = sorted(set(str(f) for f in families))
    obs = sorted(set(int(o) for o in observers))
    prot = sorted(set(fams) & protected_families(cfg))
    locked = [o for o in obs if is_locked(o)]
    ok_lock, why = lock_valid(lock_file) if mode == "confirmatory" else (False, "dry-run mode")
    refused = bool(prot or locked) and not ok_lock
    entry = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "mode": mode, "step": step, "families": fams,
             "observers": len(obs), "protected_families": prot, "locked_observers": len(locked),
             "lock": why, "decision": "refused" if refused else "allowed"}
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(entry) + "\n")
    if refused:
        raise GuardRefusal(f"{step}: {len(prot)} protected families, {len(locked)} locked observers ({why})")


def summary(log_path):
    """Counts of allowed and refused entries, and whether any allowed entry holds protected data."""
    rows = [json.loads(x) for x in Path(log_path).read_text(encoding="utf-8").splitlines() if x.strip()] \
        if Path(log_path).exists() else []
    allowed_protected = [r for r in rows if r["decision"] == "allowed" and (r["protected_families"] or r["locked_observers"])]
    return {"entries": len(rows), "allowed": sum(r["decision"] == "allowed" for r in rows),
            "refused": sum(r["decision"] == "refused" for r in rows),
            "allowed_with_protected_data": len(allowed_protected)}
