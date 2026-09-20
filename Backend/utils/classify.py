import random

from data.knowledge_base import KB


def get_baseline(entries, activity, exclude_index=-1):
    """Rolling per-activity baseline = mean of all previous readings
    for that activity (excluding the reading being classified)."""
    rows = [e for i, e in enumerate(entries) if e["activity"] == activity and i != exclude_index]
    if not rows:
        return None
    return sum(e["litres"] for e in rows) / len(rows)


def classify(entries, activity, litres):
    """Simple anomaly / pattern detection: flag a reading as "high" if
    it's 30%+ above the rolling baseline (possible leak / overuse),
    "low" if it's 30%+ below (good behaviour), otherwise "normal"."""
    baseline = get_baseline(entries, activity)
    if baseline is None:
        return {"level": "normal", "baseline": None, "ratio": None}
    ratio = litres / baseline
    if ratio >= 1.3:
        return {"level": "high", "baseline": baseline, "ratio": ratio}
    if ratio <= 0.7:
        return {"level": "low", "baseline": baseline, "ratio": ratio}
    return {"level": "normal", "baseline": baseline, "ratio": ratio}


def retrieve_tip(activity, level):
    """Retrieval-augmented tip lookup: lexical match on activity tag
    first, then on severity level, falling back gracefully at each step."""
    pool = [k for k in KB if activity in k["tags"]]
    if not pool:
        pool = [k for k in KB if "general" in k["tags"]]
    by_severity = [k for k in pool if k["severity"] == level]
    if not by_severity:
        by_severity = pool
    return random.choice(by_severity)
