import sqlite3
import re
from datetime import datetime, timedelta

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

cursor.execute("""
SELECT id, date, content
FROM articles
WHERE content IS NOT NULL
AND language = 'French'
""")

articles = cursor.fetchall()

months = {
    "janvier": 1,
    "février": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "août": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "décembre": 12
}

weekdays = {
    "lundi": 0,
    "mardi": 1,
    "mercredi": 2,
    "jeudi": 3,
    "vendredi": 4,
    "samedi": 5,
    "dimanche": 6
}

explicit_date_pattern = r"\b(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\b"

relative_weekday_pattern = r"\b(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\b"

for article_id, publication_date, content in articles:
    publication_datetime = datetime.strptime(
        publication_date,
        "%Y-%m-%d %H:%M:%S"
    )

    explicit_dates = re.findall(
        explicit_date_pattern,
        content.lower()
    )

    detected_dates = set()

    for weekday_name, day, month_name in explicit_dates:
        month = months[month_name]
        year = publication_datetime.year

        event_date = datetime(
            year,
            month,
            int(day)
        )

        if event_date > publication_datetime:
            event_date = event_date.replace(
                year=year - 1
            )

        detected_dates.add(event_date.date())

        print(
            "Artículo:",
            article_id,
            "| Tipo: explícita",
            "| Texto:",
            weekday_name,
            day,
            month_name,
            "| Fecha detectada:",
            event_date.strftime("%Y-%m-%d")
        )

    relative_weekdays = re.findall(
        relative_weekday_pattern,
        content.lower()
    )

    for weekday_name in relative_weekdays:
        target_weekday = weekdays[weekday_name]
        publication_weekday = publication_datetime.weekday()

        days_back = (
            publication_weekday - target_weekday
        ) % 7

        if days_back == 0:
            continue

        event_date = publication_datetime - timedelta(
            days=days_back
        )

        if event_date.date() in detected_dates:
            continue

        detected_dates.add(event_date.date())

        print(
            "Artículo:",
            article_id,
            "| Tipo: relativa",
            "| Texto:",
            weekday_name,
            "| Fecha detectada:",
            event_date.strftime("%Y-%m-%d")
        )

connection.close()
