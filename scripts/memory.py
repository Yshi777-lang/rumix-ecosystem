# memory.py — память на grep с реранкингом
# Создано: 21.10.2026 (Тиамат + Зая)
# Обновлено: 21.10 (реранкинг по количеству совпадений)

import sys
from pathlib import Path

MEMORY_DIR = Path.home() / "Work" / "notes"
CARDS_DIR = Path.home() / "Work" / "blocks" / "cards"

def search(query, top_k=5):
    """Ищем совпадения и сортируем по релевантности."""
    query_words = query.lower().split()
    results = []
    
    for d in [MEMORY_DIR, CARDS_DIR]:
        if not d.exists():
            continue
        for f in d.glob("*.md"):
            try:
                text = f.read_text(encoding="utf-8")
                score = 0
                best_line = ""
                
                for line in text.split('\n'):
                    line_lower = line.lower()
                    # Считаем, сколько слов запроса есть в строке
                    line_score = sum(1 for w in query_words if w in line_lower)
                    if line_score > score:
                        score = line_score
                        best_line = line.strip()
                
                if score > 0:
                    results.append({
                        "file": f.name,
                        "path": str(f),
                        "line": best_line[:200],
                        "score": score
                    })
            except:
                pass
    
    # Сортируем по score (больше — лучше)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 memory.py 'запрос'")
        sys.exit(1)
    
    query = sys.argv[1]
    results = search(query)
    
    print(f"🔍 Запрос: {query}")
    print(f"📂 Найдено: {len(results)}")
    print()
    
    for r in results:
        print(f"📄 {r['file']} (score: {r['score']})")
        print(f"   {r['line']}")
        print()
