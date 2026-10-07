import sqlite3
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

DATABASE_PATH = "data/intelligence.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@app.route("/")
def index():
    return send_from_directory(
        "../../web",
        "map.html"
    )


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "Sahel Intelligence API"
    })


@app.route("/api/events")
def get_events():
    country = request.args.get("country")
    event_type = request.args.get("type")

    connection = get_connection()
    cursor = connection.cursor()

    query = """
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
        confidence
    FROM events
    WHERE 1 = 1
    """

    parameters = []

    if country:
        query += " AND country = ?"
        parameters.append(country)

    if event_type:
        query += " AND event_type = ?"
        parameters.append(event_type)

    query += " ORDER BY event_date DESC"

    cursor.execute(
        query,
        parameters
    )

    events = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return jsonify({
        "count": len(events),
        "events": events
    })


@app.route("/api/events/<int:event_id>")
def get_event(event_id):
    connection = get_connection()
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
        confidence
    FROM events
    WHERE id = ?
    """, (event_id,))

    event_row = cursor.fetchone()

    if event_row is None:
        connection.close()

        return jsonify({
            "error": "Event not found"
        }), 404

    event = dict(event_row)

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
    """, (event_id,))

    event["entities"] = [
        dict(row)
        for row in cursor.fetchall()
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
    """, (event_id,))

    event["sources"] = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return jsonify(event)


@app.route("/api/stats")
def get_stats():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM events
    """)
    total_events = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM events
    WHERE latitude IS NOT NULL
    AND longitude IS NOT NULL
    """)
    geolocated_events = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM entities
    """)
    total_entities = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM articles
    """)
    total_sources = cursor.fetchone()[0]

    cursor.execute("""
    SELECT
        event_type,
        COUNT(*) AS total
    FROM events
    GROUP BY event_type
    ORDER BY total DESC
    """)

    events_by_type = [
        {
            "event_type": row["event_type"],
            "total": row["total"]
        }
        for row in cursor.fetchall()
    ]

    connection.close()

    return jsonify({
        "events": total_events,
        "geolocated_events": geolocated_events,
        "entities": total_entities,
        "sources": total_sources,
        "events_by_type": events_by_type
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
