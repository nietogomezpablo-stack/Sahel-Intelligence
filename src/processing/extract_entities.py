import sqlite3
import spacy

modelo_frances = spacy.load("fr_core_news_lg")
modelo_multilingue = spacy.load("xx_ent_wiki_sm")

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

cursor.execute("DELETE FROM entity_mentions")

cursor.execute("""
SELECT id, content, language
FROM articles
WHERE content IS NOT NULL
""")

articles = cursor.fetchall()

print("Artículos para analizar:", len(articles))

menciones_detectadas = 0

for article_id, content, language in articles:
    print("Analizando artículo:", article_id, "-", language)

    if language == "French":
        nlp = modelo_frances
    else:
        nlp = modelo_multilingue

    doc = nlp(content)

    for entity in doc.ents:
        text = entity.text.strip()

        if not text:
            continue

        cursor.execute(
            """
            INSERT INTO entity_mentions (
                article_id,
                entity_id,
                text,
                detected_type,
                start_char,
                end_char
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                article_id,
                None,
                text,
                entity.label_,
                entity.start_char,
                entity.end_char
            )
        )

        menciones_detectadas += 1

connection.commit()
connection.close()

print()
print("Análisis NER terminado.")
print("Menciones detectadas:", menciones_detectadas)
