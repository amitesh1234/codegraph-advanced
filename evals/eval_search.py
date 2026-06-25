import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services import search_code
from evals.cases import WORD_OVERLAP, CONCEPT_ONLY

def score_group(name, cases, k=3):
    hits, misses = 0, []
    for query, expected in cases:
        results = search_code(query, limit=k)
        names = [r["name"] for r in results]
        if expected in names:
            hits += 1
        else:
            misses.append((query, expected, names))

    total = len(cases)
    print(f"\n{name}: {hits}/{total} = {hits/total:.0%}")
    for q, exp, got in misses:
        print(f"   MISS: '{q}' → expected '{exp}', got {got}")
    return hits, total

if __name__ == "__main__":
    print("=== search_code localization accuracy (top-3) ===")
    h1, t1 = score_group("WORD_OVERLAP (should pass, tests if search works)", WORD_OVERLAP)
    h2, t2 = score_group("CONCEPT_ONLY (hard, tests if you need semantic search)", CONCEPT_ONLY)
    print(f"\nOVERALL: {h1+h2}/{t1+t2} = {(h1+h2)/(t1+t2):.0%}")