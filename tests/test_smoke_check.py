from scripts.smoke_test import check


def test_canary_passes_when_accurate_and_fast():
    assert check({"live_accuracy": 1.0, "latency_ms": 9.0}, 0.85, 1000) == []


def test_canary_fails_on_low_accuracy_or_slow_responses():
    assert len(check({"live_accuracy": 0.5, "latency_ms": 9.0}, 0.85, 1000)) == 1
    assert len(check({"live_accuracy": 1.0, "latency_ms": 2500.0}, 0.85, 1000)) == 1
