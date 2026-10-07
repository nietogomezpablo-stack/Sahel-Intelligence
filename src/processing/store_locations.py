import sqlite3

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

cursor.execute("""
SELECT
    id,
    location,
    country,
    latitude,
    longitude
FROM events
WHERE location IS NOT NULL
AND location != 'unknown'
AND latitude IS NOT NULL
AND longitude IS NOT NULL
""")

events = cursor.fetchall()

locations_created = 0
relations_created = 0

for (
    event_id,
    location,
    country,
    latitude,
    longitude
) in events:

    cursor.execute("""
    INSERT OR IGNORE INTO locations (
        canonical_name,
        country,
        latitude,
        longitude
    )
    VALUES (?, ?, ?, ?)
    """, (
        location,
        country,
        latitude,
        longitude
    ))

    if cursor.rowcount > 0:
        locations_created += 1

    cursor.execute("""
    SELECT id
    FROM locations
    WHERE canonical_name = ?
    AND country = ?
    """, (
        location,
        country
    ))

    location_id = cursor.fetchone()[0]

    cursor.execute("""
    INSERT OR IGNORE INTO event_locations (
        event_id,
        location_id,
        relation_type
    )
    VALUES (?, ?, ?)
    """, (
        event_id,
        location_id,
        "occurred_at"
    ))

    if cursor.rowcount > 0:
        relations_created += 1

connection.commit()
connection.close()

print("Migración geográfica terminada.")
print("Lugares nuevos:", locations_created)
print("Relaciones nuevas:", relations_created)
