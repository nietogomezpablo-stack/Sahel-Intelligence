import sqlite3
import re

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

cursor.execute("""
SELECT id, text
FROM entity_mentions
""")

mentions = cursor.fetchall()

print("Menciones para normalizar:", len(mentions))

normalizadas = 0

for mention_id, text in mentions:
    normalized_text = text.strip()

    normalized_text = re.sub(r"\s+", " ", normalized_text)

    normalized_text = normalized_text.strip(" •·–—,;:")

    if "•" in normalized_text:
        partes = normalized_text.split("•")

        if len(partes) > 1:
            normalized_text = partes[-1].strip()

    cursor.execute(
        """
        UPDATE entity_mentions
        SET normalized_text = ?
        WHERE id = ?
        """,
        (normalized_text, mention_id)
    )

    normalizadas += 1

connection.commit()
connection.close()

print("Normalización terminada.")
print("Menciones normalizadas:", normalizadas)
