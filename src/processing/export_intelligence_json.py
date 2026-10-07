import sqlite3
import json

connection = sqlite3.connect("data/intelligence.db")
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

cursor.execute("""
SELECT
    id,
    title,
    event_date,
    event_type,
    country,
    location,
    latitude,
    longitude,
    description,
    confidence,
    created_at
FROM events
ORDER BY event_date DESC
""")

event_rows = cursor.fetchall()

events = []

for row in event_rows:
    event = dict(row)

    cursor.execute("""
    SELECT
        ent.id,
        ent.canonical_name,
        ent.entity_type,
        ee.relation_type
    FROM event_entities ee
    JOIN entities ent
        ON ee.entity_id = ent.id
    WHERE ee.event_id = ?
    """, (
        event["id"],
    ))

    event["entities"] = [
        dict(entity)
        for entity in cursor.fetchall()
    ]

    cursor.execute("""
    SELECT
        a.id,
        a.title,
        a.date,
        a.url,
        a.domain
    FROM event_articles ea
    JOIN articles a
        ON ea.article_id = a.id
    WHERE ea.event_id = ?
    """, (
        event["id"],
    ))

    event["sources"] = [
        dict(source)
        for source in cursor.fetchall()
    ]

    events.append(event)

output = {
    "event_count": len(events),
    "events": events
}

with open(
    "data/exports/intelligence.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        output,
        file,
        ensure_ascii=False,
        indent=2
    )

connection.close()

print("Exportación de inteligencia terminada.")
print("Eventos exportados:", len(events))
print("Archivo: data/exports/intelligence.json")
