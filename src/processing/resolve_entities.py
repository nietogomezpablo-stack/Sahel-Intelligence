import sqlite3
import re

connection = sqlite3.connect("data/intelligence.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

cursor.execute("""
SELECT
    id,
    article_id,
    normalized_text,
    detected_type
FROM entity_mentions
WHERE normalized_text IS NOT NULL
""")

mentions = cursor.fetchall()

print("Menciones para resolver:", len(mentions))


def clean_name(name):
    name = name.strip()

    name = re.sub(
        r"^(Le|La|Les|L'|L’)\s+",
        "",
        name,
        flags=re.IGNORECASE
    )

    return name.strip()


known_aliases = {
    "MPLJ": (
        "Mouvement patriotique pour la liberté et la justice",
        "ORG"
    ),
    "Siguédine": (
        "Séguédine",
        "LOC"
    )
}

resolved = 0

for (
    mention_id,
    article_id,
    normalized_text,
    detected_type
) in mentions:

    cleaned_name = clean_name(normalized_text)

    if cleaned_name in known_aliases:
        canonical_name, canonical_type = known_aliases[
            cleaned_name
        ]

    elif cleaned_name == "Séguédine":
        canonical_name = "Séguédine"
        canonical_type = "LOC"

    else:
        canonical_name = cleaned_name
        canonical_type = detected_type

    cursor.execute("""
    INSERT OR IGNORE INTO entities (
        canonical_name,
        entity_type
    )
    VALUES (?, ?)
    """, (
        canonical_name,
        canonical_type
    ))

    cursor.execute("""
    SELECT id
    FROM entities
    WHERE canonical_name = ?
    AND entity_type = ?
    """, (
        canonical_name,
        canonical_type
    ))

    entity_id = cursor.fetchone()[0]

    cursor.execute("""
    UPDATE entity_mentions
    SET entity_id = ?
    WHERE id = ?
    """, (
        entity_id,
        mention_id
    ))

    resolved += 1


cursor.execute("""
SELECT
    id,
    article_id,
    normalized_text,
    entity_id
FROM entity_mentions
WHERE detected_type = 'PER'
AND normalized_text LIKE '% %'
AND entity_id IS NOT NULL
""")

person_mentions = cursor.fetchall()

surname_variants_resolved = 0

for (
    mention_id,
    article_id,
    full_name,
    canonical_entity_id
) in person_mentions:

    parts = full_name.split()

    if len(parts) < 2:
        continue

    surname = parts[-1]

    cursor.execute("""
    SELECT id
    FROM entity_mentions
    WHERE article_id = ?
    AND normalized_text = ?
    AND id != ?
    """, (
        article_id,
        surname,
        mention_id
    ))

    surname_mentions = cursor.fetchall()

    for surname_mention in surname_mentions:
        surname_mention_id = surname_mention[0]

        cursor.execute("""
        UPDATE entity_mentions
        SET entity_id = ?
        WHERE id = ?
        """, (
            canonical_entity_id,
            surname_mention_id
        ))

        surname_variants_resolved += 1


connection.commit()

cursor.execute("""
SELECT COUNT(*)
FROM entities
""")

canonical_entities = cursor.fetchone()[0]

connection.close()

print("Entity Resolution terminado.")
print("Menciones procesadas:", resolved)
print(
    "Variantes de apellido resueltas:",
    surname_variants_resolved
)
print("Entidades canónicas:", canonical_entities)
