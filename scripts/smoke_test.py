"""Canary check against a live deployment.

Sends labeled articles to <base_url>/api/analyze and reports accuracy + latency.
Prints one JSON line; exit 1 if the service errors, live accuracy is too low or it is too slow.
Usage: python scripts/smoke_test.py http://<host> [--out smoke.json]
"""
import argparse
import json
import pathlib
import statistics
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent


def post(url, payload):
    req = urllib.request.Request(url, json.dumps(payload).encode(), {"Content-Type": "application/json"})
    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = json.load(resp)
    return body, (time.perf_counter() - start) * 1000


def main():
    p = argparse.ArgumentParser()
    p.add_argument("base_url")
    p.add_argument("--out", default="smoke.json")
    p.add_argument("--min-accuracy", type=float, default=0.85)
    p.add_argument("--max-latency-ms", type=float, default=1000)
    args = p.parse_args()
    base = args.base_url.rstrip("/")

    data = json.loads((ROOT / "eval" / "dataset.json").read_text(encoding="utf-8"))
    latencies, correct = [], 0
    try:
        with urllib.request.urlopen(base + "/api/health", timeout=10) as r:
            version = json.load(r).get("version")
        for item in data:
            body, ms = post(base + "/api/analyze", {k: item[k] for k in ("title", "content", "source")})
            latencies.append(ms)
            predicted = "credible" if body["credibility_score"] >= 60 else "fake"
            correct += predicted == item["label"]
    except Exception as exc:  # unreachable, 5xx, bad JSON...
        print(json.dumps({"ok": False, "error": str(exc)}))
        sys.exit(1)

    result = {
        "live_version": version,
        "live_accuracy": round(correct / len(data), 4),
        "latency_ms": round(statistics.mean(latencies), 1),
    }
    reasons = check(result, args.min_accuracy, args.max_latency_ms)
    result["ok"], result["reasons"] = not reasons, reasons
    pathlib.Path(args.out).write_text(json.dumps(result))
    print(json.dumps(result))
    if reasons:
        sys.exit(1)


def check(result, min_accuracy, max_latency_ms):
    """Why the live deployment fails the canary (empty list = pass)."""
    reasons = []
    if result["live_accuracy"] < min_accuracy:
        reasons.append(f"live accuracy {result['live_accuracy']:.0%} below {min_accuracy:.0%}")
    if result["latency_ms"] > max_latency_ms:
        reasons.append(f"mean latency {result['latency_ms']} ms above {max_latency_ms:g} ms")
    return reasons


if __name__ == "__main__":
    main()
