import sqlite3
import re

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

cursor.execute("""
SELECT id, title, content, language
FROM articles
WHERE content IS NOT NULL
""")

articles = cursor.fetchall()

attack_patterns = [
    r"\battaque\b",
    r"\battaques\b",
    r"\battaqué\b",
    r"\battaqués\b",
    r"\baffrontement\b",
    r"\baffrontements\b",
    r"\bassaut\b",
    r"\bcombats?\b"
]

print("Artículos analizados:", len(articles))
print()

candidatos = 0

for article_id, title, content, language in articles:
    if language != "French":
        continue

    sentences = re.split(r"(?<=[.!?])\s+", content)

    evidencias = []

    for sentence in sentences:
        sentence_lower = sentence.lower()

        for pattern in attack_patterns:
            if re.search(pattern, sentence_lower):
                if sentence not in evidencias:
                    evidencias.append(sentence)
                break

    if evidencias:
        candidatos += 1

        print("CANDIDATO:", article_id)
        print("Título:", title)
        print()

        for evidence in evidencias:
            print("EVIDENCIA:", evidence)

        print("-" * 80)

connection.close()

print()
print("Candidatos a armed_attack:", candidatos)
