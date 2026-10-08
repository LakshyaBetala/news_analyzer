"""Append one release record to releases.json (the file the Control Room page reads).

Called by Jenkins at the end of every run, success or failure.
Usage: python scripts/record_release.py --version 12.ab12cd3 --commit ab12cd3 --message "msg" \
         --status PROMOTED|BLOCKED|ROLLED_BACK --eval eval_result.json [--smoke smoke.json] [--cpu 7.5]
"""
import argparse
import datetime
import json
import pathlib

RELEASES = pathlib.Path("releases.json")
KEEP = 50


def load(path):
    p = pathlib.Path(path) if path else None
    return json.loads(p.read_text()) if p and p.exists() else {}


def verdict(status, ev, smoke):
    acc = ev.get("accuracy")
    if status == "BLOCKED":
        why = "; ".join(ev.get("reasons") or ["quality gate failed"])
        return f"Blocked before deploy: {why}. The previous version is still live."
    if status == "ROLLED_BACK":
        return "Quality gate passed but the new pods never became healthy in Kubernetes. Rolled back automatically."
    msg = f"Healthy. Accuracy {acc:.0%}" if acc is not None else "Healthy."
    if "baseline_accuracy" in ev:
        msg += f" (previous {ev['baseline_accuracy']:.0%})"
    if smoke.get("latency_ms") is not None:
        msg += f", live latency {smoke['latency_ms']} ms"
    return msg + ". Promoted to production."


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--version", required=True)
    p.add_argument("--commit", default="")
    p.add_argument("--message", default="")
    p.add_argument("--status", required=True, choices=["PROMOTED", "BLOCKED", "ROLLED_BACK"])
    p.add_argument("--eval")
    p.add_argument("--smoke")
    p.add_argument("--cpu", type=float)
    a = p.parse_args()

    ev, smoke = load(a.eval), load(a.smoke)
    record = {
        "version": a.version,
        "commit": a.commit,
        "message": a.message,
        "status": a.status,
        "time": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "accuracy": ev.get("accuracy"),
        "baseline_accuracy": ev.get("baseline_accuracy"),
        "latency_ms": smoke.get("latency_ms"),
        "cpu_percent": a.cpu,
        "verdict": verdict(a.status, ev, smoke),
    }
    history = json.loads(RELEASES.read_text()) if RELEASES.exists() else []
    history = (history + [record])[-KEEP:]
    RELEASES.write_text(json.dumps(history, indent=2))
    print(f"recorded {a.version}: {a.status}")


if __name__ == "__main__":
    main()
