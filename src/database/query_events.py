import sqlite3

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

cursor.execute("""
SELECT
    e.id,
    e.event_date,
    e.event_type,
    e.title,
    e.country,
    l.canonical_name,
    l.latitude,
    l.longitude,
    e.confidence
FROM events e
LEFT JOIN event_locations el
    ON e.id = el.event_id
LEFT JOIN locations l
    ON el.location_id = l.id
ORDER BY e.event_date DESC
""")

events = cursor.fetchall()

print("EVENTOS DE INTELIGENCIA")
print("=" * 100)

for event in events:
    (
        event_id,
        event_date,
        event_type,
        title,
        country,
        location,
        latitude,
        longitude,
        confidence
    ) = event

    print()
    print("ID:", event_id)
    print("FECHA:", event_date)
    print("TIPO:", event_type)
    print("TÍTULO:", title)
    print("PAÍS:", country)
    print(
        "LOCALIZACIÓN:",
        location if location else "unknown"
    )
    print(
        "COORDENADAS:",
        (
            f"{latitude}, {longitude}"
            if latitude is not None
            and longitude is not None
            else "unknown"
        )
    )
    print("CONFIANZA:", confidence)
    print("-" * 100)

connection.close()
