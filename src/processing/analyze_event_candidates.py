import sqlite3
import re
import spacy

modelo_frances = spacy.load("fr_core_news_lg")

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

cursor.execute("""
SELECT id, title, content, date
FROM articles
WHERE content IS NOT NULL
AND language = 'French'
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

for article_id, title, content, publication_date in articles:
    sentences = re.split(r"(?<=[.!?])\s+", content)

    for sentence in sentences:
        sentence_lower = sentence.lower()

        detected = False

        for pattern in attack_patterns:
            if re.search(pattern, sentence_lower):
                detected = True
                break

        if not detected:
            continue

        doc = modelo_frances(sentence)

        persons = []
        organizations = []
        locations = []

        for entity in doc.ents:
            if entity.label_ == "PER":
                persons.append(entity.text)
            elif entity.label_ == "ORG":
                organizations.append(entity.text)
            elif entity.label_ == "LOC":
                locations.append(entity.text)

        print()
        print("ARTICLE:", article_id)
        print("PUBLICATION DATE:", publication_date)
        print("EVIDENCE:", sentence)
        print("PERSONS:", persons)
        print("ORGANIZATIONS:", organizations)
        print("LOCATIONS:", locations)
        print("-" * 80)

connection.close()
