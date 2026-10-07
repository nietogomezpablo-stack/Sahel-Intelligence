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
    ent.canonical_name,
    ee.relation_type,
    e.confidence
FROM events e

LEFT JOIN event_locations el
    ON e.id = el.event_id

LEFT JOIN locations l
    ON el.location_id = l.id

LEFT JOIN event_entities ee
    ON e.id = ee.event_id

LEFT JOIN entities ent
    ON ee.entity_id = ent.id

ORDER BY
    e.event_date DESC,
    e.id
""")

rows = cursor.fetchall()

current_event = None

for row in rows:
    (
        event_id,
        event_date,
        event_type,
        title,
        country,
        location,
        latitude,
        longitude,
        entity,
        relation,
        confidence
    ) = row

    if event_id != current_event:
        if current_event is not None:
            print()

        print("=" * 100)
        print("EVENT ID:", event_id)
        print("DATE:", event_date)
        print("TYPE:", event_type)
        print("TITLE:", title)
        print("COUNTRY:", country)
        print(
            "LOCATION:",
            location if location else "unknown"
        )

        if latitude is not None and longitude is not None:
            print(
                "COORDINATES:",
                latitude,
                longitude
            )
        else:
            print("COORDINATES: unknown")

        print("CONFIDENCE:", confidence)
        print("ENTITIES:")

        current_event = event_id

    if entity is not None:
        print(
            " -",
            relation,
            "→",
            entity
        )

connection.close()
