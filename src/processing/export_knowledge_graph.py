import sqlite3
import json

connection = sqlite3.connect("data/intelligence.db")
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

nodes = {}
edges = []


def add_node(node_id, label, node_type, properties=None):
    if node_id not in nodes:
        nodes[node_id] = {
            "id": node_id,
            "label": label,
            "type": node_type,
            "properties": properties or {}
        }


def add_edge(source, target, relation):
    edge = {
        "source": source,
        "target": target,
        "relation": relation
    }

    if edge not in edges:
        edges.append(edge)


cursor.execute("""
SELECT
    id,
    title,
    event_date,
    event_type,
    country,
    confidence
FROM events
""")

for event in cursor.fetchall():
    node_id = f"event:{event['id']}"

    add_node(
        node_id,
        event["title"],
        "event",
        {
            "event_date": event["event_date"],
            "event_type": event["event_type"],
            "country": event["country"],
            "confidence": event["confidence"]
        }
    )


cursor.execute("""
SELECT
    id,
    canonical_name,
    entity_type
FROM entities
""")

for entity in cursor.fetchall():
    node_id = f"entity:{entity['id']}"

    add_node(
        node_id,
        entity["canonical_name"],
        "entity",
        {
            "entity_type": entity["entity_type"]
        }
    )


cursor.execute("""
SELECT
    id,
    canonical_name,
    country,
    latitude,
    longitude
FROM locations
""")

for location in cursor.fetchall():
    node_id = f"location:{location['id']}"

    add_node(
        node_id,
        location["canonical_name"],
        "location",
        {
            "country": location["country"],
            "latitude": location["latitude"],
            "longitude": location["longitude"]
        }
    )


cursor.execute("""
SELECT
    id,
    title,
    date,
    url,
    domain
FROM articles
""")

for article in cursor.fetchall():
    node_id = f"article:{article['id']}"

    add_node(
        node_id,
        article["title"],
        "source",
        {
            "date": article["date"],
            "url": article["url"],
            "domain": article["domain"]
        }
    )


cursor.execute("""
SELECT
    event_id,
    entity_id,
    relation_type
FROM event_entities
""")

for relation in cursor.fetchall():
    add_edge(
        f"event:{relation['event_id']}",
        f"entity:{relation['entity_id']}",
        relation["relation_type"]
    )


cursor.execute("""
SELECT
    event_id,
    location_id,
    relation_type
FROM event_locations
""")

for relation in cursor.fetchall():
    add_edge(
        f"event:{relation['event_id']}",
        f"location:{relation['location_id']}",
        relation["relation_type"]
    )


cursor.execute("""
SELECT
    event_id,
    article_id
FROM event_articles
""")

for relation in cursor.fetchall():
    add_edge(
        f"article:{relation['article_id']}",
        f"event:{relation['event_id']}",
        "supports"
    )


graph = {
    "nodes": list(nodes.values()),
    "edges": edges
}

with open(
    "data/exports/knowledge_graph.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        graph,
        file,
        ensure_ascii=False,
        indent=2
    )

connection.close()

print("Knowledge Graph exportado.")
print("Nodos:", len(nodes))
print("Relaciones:", len(edges))
print("Archivo: data/exports/knowledge_graph.json")
