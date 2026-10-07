import sqlite3

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

article_id = 4

title = "Ataque del MPLJ contra fuerzas de seguridad en Séguédine"
event_date = "2026-08-14"
event_type = "armed_attack"
country = "Niger"
location = "Séguédine"
description = "Ataques reivindicados por el MPLJ contra posiciones de las fuerzas de seguridad nigerinas en Séguédine, con varios soldados muertos y daños materiales."
confidence = 0.8

cursor.execute(
    """
    INSERT INTO events (
        title,
        event_date,
        event_type,
        country,
        location,
        description,
        confidence
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        title,
        event_date,
        event_type,
        country,
        location,
        description,
        confidence
    )
)

event_id = cursor.lastrowid

cursor.execute(
    """
    INSERT INTO event_articles (
        event_id,
        article_id
    )
    VALUES (?, ?)
    """,
    (
        event_id,
        article_id
    )
)

connection.commit()
connection.close()

print("Evento creado correctamente.")
print("Event ID:", event_id)
print("Article ID:", article_id)
