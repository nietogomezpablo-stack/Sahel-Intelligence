import sqlite3

connection = sqlite3.connect("data/intelligence.db")
connection.execute("PRAGMA foreign_keys = ON")
cursor = connection.cursor()

print("DATABASE INTEGRITY")
print("=" * 80)

cursor.execute("PRAGMA integrity_check")
integrity = cursor.fetchone()[0]

print("SQLite integrity:", integrity)

cursor.execute("""
SELECT COUNT(*)
FROM event_entities ee
LEFT JOIN events e
    ON ee.event_id = e.id
WHERE e.id IS NULL
""")

orphan_event_entities = cursor.fetchone()[0]

cursor.execute("""
SELECT COUNT(*)
FROM event_entities ee
LEFT JOIN entities e
    ON ee.entity_id = e.id
WHERE e.id IS NULL
""")

orphan_entities = cursor.fetchone()[0]

cursor.execute("""
SELECT COUNT(*)
FROM event_locations el
LEFT JOIN events e
    ON el.event_id = e.id
WHERE e.id IS NULL
""")

orphan_event_locations = cursor.fetchone()[0]

cursor.execute("""
SELECT COUNT(*)
FROM event_locations el
LEFT JOIN locations l
    ON el.location_id = l.id
WHERE l.id IS NULL
""")

orphan_locations = cursor.fetchone()[0]

cursor.execute("""
SELECT COUNT(*)
FROM event_articles ea
LEFT JOIN events e
    ON ea.event_id = e.id
WHERE e.id IS NULL
""")

orphan_event_articles = cursor.fetchone()[0]

cursor.execute("""
SELECT COUNT(*)
FROM event_articles ea
LEFT JOIN articles a
    ON ea.article_id = a.id
WHERE a.id IS NULL
""")

orphan_articles = cursor.fetchone()[0]

print("Event entities without event:", orphan_event_entities)
print("Event entities without entity:", orphan_entities)
print("Event locations without event:", orphan_event_locations)
print("Event locations without location:", orphan_locations)
print("Event articles without event:", orphan_event_articles)
print("Event articles without article:", orphan_articles)

problems = (
    orphan_event_entities
    + orphan_entities
    + orphan_event_locations
    + orphan_locations
    + orphan_event_articles
    + orphan_articles
)

print()

if integrity == "ok" and problems == 0:
    print("RESULT: DATABASE OK")
else:
    print("RESULT: DATABASE PROBLEMS DETECTED")

connection.close()
