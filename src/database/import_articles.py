import json
import sqlite3

with open("data/processed/gdelt_niger.json", "r", encoding="utf-8") as file:
    data = json.load(file)

articles = data["articles"]

connection = sqlite3.connect("data/intelligence.db")
cursor = connection.cursor()

articulos_insertados = 0

for article in articles:
    cursor.execute(
        """
        INSERT OR IGNORE INTO articles (
            title,
            date,
            url,
            domain,
            language,
            source_country
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            article["title"],
            article["date"],
            article["url"],
            article["domain"],
            article["language"],
            article["source_country"]
        )
    )

    if cursor.rowcount == 1:
        articulos_insertados += 1

connection.commit()
connection.close()

print("Artículos procesados:", len(articles))
print("Artículos nuevos insertados:", articulos_insertados)
print("Artículos ignorados por estar duplicados:", len(articles) - articulos_insertados)
