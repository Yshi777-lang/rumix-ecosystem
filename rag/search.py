import json
from pathlib import Path

SCORE_FILE = Path.home() / "rumix" / "rag" / "scores.json"

def load_scores():
    if not SCORE_FILE.exists():
        return {}
    return json.loads(SCORE_FILE.read_text(encoding="utf-8"))

def get_context(query, top_k=3):
    words = query.lower().split()
    scores = load_scores()
    results = []

    for path, score in scores.items():
        try:
            text = Path(path).read_text(encoding="utf-8")
            hits = sum(1 for w in words if w in text.lower())
            if hits == 0:
                continue
            rank = hits * score
            results.append((rank, path, text))
        except:
            continue

    results.sort(key=lambda x: x[0], reverse=True)
    
    context = ""
    for rank, path, text in results[:top_k]:
        fname = Path(path).name
        context += f"---\nИсточник: {fname}\n\n{text[:800]}\n---\n"
    return context

if __name__ == "__main__":
    q = input("Запрос: ")
    print(get_context(q))
