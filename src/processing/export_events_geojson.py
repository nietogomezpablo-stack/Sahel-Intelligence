import sqlite3
import json

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

cursor.execute("""
SELECT
    e.id,
    e.title,
    e.event_date,
    e.event_type,
    e.country,
    l.canonical_name,
    l.latitude,
    l.longitude,
    e.description,
    e.confidence
FROM events e
JOIN event_locations el
    ON e.id = el.event_id
JOIN locations l
    ON el.location_id = l.id
WHERE l.latitude IS NOT NULL
AND l.longitude IS NOT NULL
ORDER BY e.event_date DESC
""")

events = cursor.fetchall()

features = []

for event in events:
    (
        event_id,
        title,
        event_date,
        event_type,
        country,
        location,
        latitude,
        longitude,
        description,
        confidence
    ) = event

    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [
                longitude,
                latitude
            ]
        },
        "properties": {
            "event_id": event_id,
            "title": title,
            "event_date": event_date,
            "event_type": event_type,
            "country": country,
            "location": location,
            "description": description,
            "confidence": confidence
        }
    }

    features.append(feature)

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open(
    "data/exports/events.geojson",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        geojson,
        file,
        ensure_ascii=False,
        indent=2
    )

connection.close()

print("GeoJSON generado correctamente.")
print("Eventos exportados:", len(features))
print("Archivo: data/exports/events.geojson")
