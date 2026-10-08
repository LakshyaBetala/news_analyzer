"""Quality gate: score a labeled article set and fail if accuracy regresses.

Usage: python eval/run_eval.py [--min-accuracy 0.85] [--baseline prev.json] [--out result.json]
An article is predicted "credible" if score >= 60. Exit code 1 = gate failed (blocks the pipeline).
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.model import NewsCredibilityAnalyzer  # noqa: E402

THRESHOLD = 60.0
MAX_DROP = 0.05  # allowed accuracy drop vs. the previous release


def evaluate():
    data = json.loads((ROOT / "eval" / "dataset.json").read_text(encoding="utf-8"))
    analyzer = NewsCredibilityAnalyzer()
    correct, misses = 0, []
    for item in data:
        score = analyzer.analyze(item["title"], item["content"], item["source"])["credibility_score"]
        predicted = "credible" if score >= THRESHOLD else "fake"
        if predicted == item["label"]:
            correct += 1
        else:
            misses.append({"title": item["title"], "expected": item["label"], "score": score})
    return {"accuracy": round(correct / len(data), 4), "total": len(data), "correct": correct, "misses": misses}


def load_baseline(path):
    """Accuracy of the last PROMOTED release. Accepts releases.json (a list) or a single result dict."""
    data = json.loads(pathlib.Path(path).read_text())
    if isinstance(data, dict):
        return data.get("accuracy")
    promoted = [r for r in data if r.get("status") == "PROMOTED" and r.get("accuracy") is not None]
    return promoted[-1]["accuracy"] if promoted else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--min-accuracy", type=float, default=0.85)
    p.add_argument("--baseline", help="JSON from the previous release (has 'accuracy')")
    p.add_argument("--out", default="eval_result.json")
    args = p.parse_args()

    result = evaluate()
    reasons = []
    if result["accuracy"] < args.min_accuracy:
        reasons.append(f"accuracy {result['accuracy']:.0%} is below minimum {args.min_accuracy:.0%}")
    if args.baseline and pathlib.Path(args.baseline).exists():
        prev = load_baseline(args.baseline)
        if prev is not None:
            result["baseline_accuracy"] = prev
        if prev is not None and prev - result["accuracy"] > MAX_DROP:
            reasons.append(f"accuracy dropped {prev:.0%} -> {result['accuracy']:.0%} vs previous release")
    result["passed"] = not reasons
    result["reasons"] = reasons
    pathlib.Path(args.out).write_text(json.dumps(result, indent=2))

    print(f"EVAL: {result['correct']}/{result['total']} correct ({result['accuracy']:.0%})")
    for m in result["misses"]:
        print(f"  miss: {m['title']!r} expected={m['expected']} score={m['score']}")
    if reasons:
        print("GATE FAILED: " + "; ".join(reasons))
        sys.exit(1)
    print("GATE PASSED")


if __name__ == "__main__":
    main()
