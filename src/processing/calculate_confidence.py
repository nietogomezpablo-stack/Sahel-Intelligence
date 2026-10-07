import sqlite3


DATABASE_PATH = "data/intelligence.db"


def calculate_score(source_count, domain_count, entity_count, geolocated):
    score = 0.40

    if source_count >= 1:
        score += 0.15

    if source_count >= 2:
        score += 0.10

    if source_count >= 3:
        score += 0.10

    if domain_count >= 2:
        score += 0.10

    if entity_count >= 1:
        score += 0.05

    if geolocated:
        score += 0.05

    return min(round(score, 2), 1.0)


connection = sqlite3.connect(DATABASE_PATH)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

cursor.execute("""
SELECT
    id,
    title,
    latitude,
    longitude
FROM events
ORDER BY id
""")

events = cursor.fetchall()

print("Eventos analizados:", len(events))
print()

for event in events:
    event_id = event["id"]

    cursor.execute("""
    SELECT
        COUNT(DISTINCT a.id) AS source_count,
        COUNT(DISTINCT a.domain) AS domain_count
    FROM event_articles ea
    JOIN articles a
        ON ea.article_id = a.id
    WHERE ea.event_id = ?
    """, (event_id,))

    source_data = cursor.fetchone()

    source_count = source_data["source_count"]
    domain_count = source_data["domain_count"]

    cursor.execute("""
    SELECT COUNT(DISTINCT entity_id)
    FROM event_entities
    WHERE event_id = ?
    """, (event_id,))

    entity_count = cursor.fetchone()[0]

    geolocated = (
        event["latitude"] is not None
        and event["longitude"] is not None
    )

    confidence = calculate_score(
        source_count,
        domain_count,
        entity_count,
        geolocated
    )

    cursor.execute("""
    UPDATE events
    SET confidence = ?
    WHERE id = ?
    """, (
        confidence,
        event_id
    ))

    print(f"EVENT {event_id}")
    print(event["title"])
    print("Fuentes:", source_count)
    print("Dominios independientes:", domain_count)
    print("Entidades relacionadas:", entity_count)
    print("Geolocalizado:", geolocated)
    print("Confidence:", confidence)
    print()


connection.commit()
connection.close()

print("Confidence actualizado.")
