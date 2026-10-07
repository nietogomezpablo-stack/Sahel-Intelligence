import sqlite3

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

cursor.execute("""
SELECT
    m.id,
    m.text,
    m.normalized_text,
    m.detected_type,
    m.start_char,
    m.end_char,
    a.content
FROM entity_mentions m
JOIN articles a ON m.article_id = a.id
ORDER BY m.id
""")

mentions = cursor.fetchall()

context_size = 100

for mention_id, text, normalized_text, detected_type, start_char, end_char, content in mentions:
    context_start = max(0, start_char - context_size)
    context_end = min(len(content), end_char + context_size)

    context = content[context_start:context_end]
    context = " ".join(context.split())

    print()
    print("Mención ID:", mention_id)
    print("Texto:", text)
    print("Normalizado:", normalized_text)
    print("Tipo:", detected_type)
    print("Contexto:", context)
    print("-" * 80)

connection.close()
