import sqlite3

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    date TEXT,
    url TEXT UNIQUE,
    domain TEXT,
    language TEXT,
    source_country TEXT,
    content TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    event_date TEXT,
    event_type TEXT,
    country TEXT,
    location TEXT,
    latitude REAL,
    longitude REAL,
    description TEXT,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS event_articles (
    event_id INTEGER NOT NULL,
    article_id INTEGER NOT NULL,
    PRIMARY KEY (
        event_id,
        article_id
    ),
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (article_id) REFERENCES articles(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    UNIQUE (
        canonical_name,
        entity_type
    )
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS entity_mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    entity_id INTEGER,
    text TEXT,
    normalized_text TEXT,
    detected_type TEXT,
    start_char INTEGER,
    end_char INTEGER,
    FOREIGN KEY (article_id) REFERENCES articles(id),
    FOREIGN KEY (entity_id) REFERENCES entities(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS event_entities (
    event_id INTEGER NOT NULL,
    entity_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    PRIMARY KEY (
        event_id,
        entity_id,
        relation_type
    ),
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (entity_id) REFERENCES entities(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_name TEXT NOT NULL,
    country TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    UNIQUE (
        canonical_name,
        country
    )
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS event_locations (
    event_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    PRIMARY KEY (
        event_id,
        location_id,
        relation_type
    ),
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (location_id) REFERENCES locations(id)
)
""")

connection.commit()
connection.close()

print("Base de datos preparada correctamente.")
