import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / "src"))

from config import CHUNK_SIZE, CHUNK_OVERLAP, MAX_DISTANCE, RELATIVE_MARGIN  # noqa: E402
from retrieve import retrieve  # noqa: E402


def keep(hits, max_distance, margin):
    """Same filtering as in answer.py. margin=None means no relative filter."""
    relevant = [h for h in hits if h["distance"] <= max_distance]
    if relevant and margin is not None:
        best = min(h["distance"] for h in relevant)
        relevant = [h for h in relevant if h["distance"] <= best + margin]
    return relevant


def pct(part, total):
    return f"{part}/{total} ({100 * part / total:.0f}%)" if total else "n/a"


def main():
    with open(ROOT / "eval" / "questions.csv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    results = []
    for row in rows:
        hits = retrieve(row["question"])
        results.append(
            {"question": row["question"], "expected": row["expected_source"].strip(), "hits": hits}
        )

    inside = [r for r in results if r["expected"]]
    outside = [r for r in results if not r["expected"]]

    print(
        f"\nSettings: chunk={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}, "
        f"max_distance={MAX_DISTANCE}, margin={RELATIVE_MARGIN}"
    )

    # 1. Retrieval quality (thresholds are ignored here)
    top1 = sum(r["hits"][0]["source"] == r["expected"] for r in inside)
    top3 = sum(r["expected"] in [h["source"] for h in r["hits"]] for r in inside)
    print("\nRETRIEVAL (questions that ARE in the knowledge base)")
    print(f"  correct document is the top result: {pct(top1, len(inside))}")
    print(f"  correct document is in the top 3:   {pct(top3, len(inside))}")
    for r in inside:
        first = r["hits"][0]
        if first["source"] != r["expected"]:
            print(
                f"  MISS: {r['question']!r} -> expected {r['expected']}, "
                f"got {first['source']} ({first['distance']:.3f})"
            )
    # 1b. Hardest in-scope questions (largest closest distance)
    print("\nHARDEST in-scope questions")
    for r in sorted(inside, key=lambda r: r["hits"][0]["distance"], reverse=True)[:3]:
        print(f"  {r['hits'][0]['distance']:.3f}  {r['question']}")

    # 2. Distance threshold
    print("\nTHRESHOLD (max_distance)")
    print("  value | in-scope answered | out-of-scope rejected")
    for thr in [0.4, 0.45, 0.5, 0.55, 0.6, 0.65]:
        answered = sum(bool(keep(r["hits"], thr, None)) for r in inside)
        rejected = sum(not keep(r["hits"], thr, None) for r in outside)
        print(f"  {thr:5} | {pct(answered, len(inside)):>17} | {pct(rejected, len(outside)):>21}")

    # 3. Relative margin
    print(f"\nRELATIVE MARGIN (max_distance={MAX_DISTANCE})")
    for margin in [None, 0.05, 0.1, 0.15, 0.2]:
        kept_correct = only_correct = 0
        for r in inside:
            sources = {h["source"] for h in keep(r["hits"], MAX_DISTANCE, margin)}
            if r["expected"] in sources:
                kept_correct += 1
            if sources == {r["expected"]}:
                only_correct += 1
        label = "none" if margin is None else str(margin)
        print(
            f"  margin {label:>4} | correct doc kept: {pct(kept_correct, len(inside))} "
            f"| only the correct doc: {pct(only_correct, len(inside))}"
        )

    # 4. Closest distance for questions that are NOT in the knowledge base
    print("\nOUT-OF-SCOPE questions: closest distance")
    for r in outside:
        print(f"  {r['hits'][0]['distance']:.3f}  {r['question']}")


if __name__ == "__main__":
    main()